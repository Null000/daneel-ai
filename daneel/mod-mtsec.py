'''
@author: Damjan 'Null' Kosir
'''
import logging
import tp.client.cache
from tp.netlib.objects import OrderDescs
import extra.objectutils
import helper
from time import sleep

rulesystem = None

constraints = """order_no_operation(int,int)
order_move(int,int,int,int)
order_build_fleet(int,list,str)
order_build_weapon(int,list)
order_colonise(int)
order_split_fleet(int,list)
order_merge_fleet(int)
order_enhance(int,int)
order_send_points(int,list)
order_load_armament(int,list)
order_unload_armament(int,list)
order_none(int)""".split('\n')

def endTurn(cache2, rs, connection2):
    global rulesystem
    global cache
    global connection
    #update globals
    rulesystem = rs
    cache = cache2
    connection = connection2
    helper.rulesystem = rulesystem
    helper.cache = cache
    helper.connection = connection
    
    AICode()
    executeOrdersNoOperation(cache, connection)
    executeOrdersMove(cache, connection)
    executeOrdersBuildFleet(cache, connection)
    executeOrdersBuildWeapon(cache, connection)
    executeOrdersColonise(cache, connection)
    executeOrdersSplitFleet(cache, connection)
    executeOrdersMergeFleet(cache, connection)
    executeOrdersEnhance(cache, connection)
    executeOrdersSendPoints(cache, connection)
    executeOrdersLoadArmament(cache, connection)
    executeOrdersUnloadArmament(cache, connection)

def orderNoOperation(id, wait):
    '''
    Object does nothing for a given number of turns
    id is for the object the order is for
     Arg name: wait    Arg type: Time (code:1)    Arg desc: The number of turns to wait
    '''
    global rulesystem
    rulesystem.addConstraint("order_no_operation(" + str(id) + ", " + str(wait) + ")")
    return

def orderMove(id, pos):
    '''
    Move to a given position absolute in space
    id is for the object the order is for
     Arg name: pos    Arg type: Absolute Space Coordinates (code:0)    Arg desc: The position in space to move to
    '''
    global rulesystem
    rulesystem.addConstraint("order_move(" + str(id) + ", " + str(pos[0]) + "," + str(pos[1]) + "," + str(pos[2]) + ")")
    return

def orderBuildFleet(id, ships, name):
    '''
    Build a fleet
    id is for the object the order is for
     Arg name: Ships    Arg type: List (code:6)    Arg desc: The type of ship to build
     Arg name: Name    Arg type: String (code:7)    Arg desc: The name of the new fleet being built
    '''
    global rulesystem
    rulesystem.addConstraint("order_build_fleet(" + str(id) + ", " + str(ships) + ", " + name + ")")
    return

def orderBuildWeapon(id, weapons):
    '''
    Build a Weapon
    id is for the object the order is for
     Arg name: Weapons    Arg type: List (code:6)    Arg desc: The type of weapon to build
    '''
    global rulesystem
    rulesystem.addConstraint("order_build_weapon(" + str(id) + ", " + str(weapons) + ")")
    return

def orderColonise(id):
    '''
    Attempt to colonise a planet at the current location
    id is for the object the order is for
    '''
    global rulesystem
    rulesystem.addConstraint("order_colonise(" + str(id) + ")")
    return

def orderSplitFleet(id, ships):
    '''
    Split the fleet into two
    id is for the object the order is for
     Arg name: ships    Arg type: List (code:6)    Arg desc: The ships to be transferred
    '''
    global rulesystem
    rulesystem.addConstraint("order_split_fleet(" + str(id) + ", " + str(ships) + ")")
    return

def orderMergeFleet(id):
    '''
    Merge this fleet into another one
    id is for the object the order is for
    '''
    global rulesystem
    rulesystem.addConstraint("order_merge_fleet(" + str(id) + ")")
    return

def orderEnhance(id, points):
    '''
    Enhance your Production
    id is for the object the order is for
     Arg name: Points    Arg type: Time (code:1)    Arg desc: The number of points you want to enhance with.
    '''
    global rulesystem
    rulesystem.addConstraint("order_enhance(" + str(id) + ", " + str(points) + ")")
    return

def orderSendPoints(id, planet):
    '''
    Send Production Points
    id is for the object the order is for
     Arg name: Planet    Arg type: List (code:6)    Arg desc: The Planet to send points to.
    '''
    global rulesystem
    rulesystem.addConstraint("order_send_points(" + str(id) + ", " + str(planet) + ")")
    return

def orderLoadArmament(id, weapons):
    '''
    Load a weapon onto your ships
    id is for the object the order is for
     Arg name: Weapons    Arg type: List (code:6)    Arg desc: The weapon to load
    '''
    global rulesystem
    rulesystem.addConstraint("order_load_armament(" + str(id) + ", " + str(weapons) + ")")
    return

def orderUnloadArmament(id, weapons):
    '''
    Unload a weapon onto your ships
    id is for the object the order is for
     Arg name: Weapons    Arg type: List (code:6)    Arg desc: The weapon to unload
    '''
    global rulesystem
    rulesystem.addConstraint("order_unload_armament(" + str(id) + ", " + str(weapons) + ")")
    return

def orderNone(id):
    '''
    Removes orders from the object.
    '''
    global rulesystem
    rulesystem.addConstraint("order_none(" + str(id) + ")")
    return
   
def executeOrdersNone(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_none(int)")
    for orderConstraint in orders:
        executeOrder(cache, connection, objectId, None)

def executeOrdersNoOperation(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_no_operation(int,int)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        wait = int(args[1])
        ordertype = findOrderDesc("No Operation")
        args = [0, objectId, -1, ordertype.subtype, 0, [], wait]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersMove(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_move(int,int,int,int)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        pos = [[int(args[1]), int(args[2]), int(args[3])]]
        ordertype = findOrderDesc("Move")
        args = [0, objectId, -1, ordertype.subtype, 0, [], pos]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersBuildFleet(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_build_fleet(int,list,str)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        ships = [[], args[1]]
        name = [len(args[2]), args[2]]
        ordertype = findOrderDesc("Build Fleet")
        args = [0, objectId, -1, ordertype.subtype, 0, [], ships, name]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersBuildWeapon(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_build_weapon(int,list)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        weapons = [[], args[1]]
        ordertype = findOrderDesc("Build Weapon")
        args = [0, objectId, -1, ordertype.subtype, 0, [], weapons]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersColonise(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_colonise(int)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        ordertype = findOrderDesc("Colonise")
        args = [0, objectId, -1, ordertype.subtype, 0, []]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersSplitFleet(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_split_fleet(int,list)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        ships = [[], args[1]]
        ordertype = findOrderDesc("Split Fleet")
        args = [0, objectId, -1, ordertype.subtype, 0, [], ships]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersMergeFleet(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_merge_fleet(int)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        ordertype = findOrderDesc("Merge Fleet")
        args = [0, objectId, -1, ordertype.subtype, 0, []]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersEnhance(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_enhance(int,int)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        points = int(args[1])
        ordertype = findOrderDesc("Enhance")
        args = [0, objectId, -1, ordertype.subtype, 0, [], Points]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersSendPoints(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_send_points(int,list)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        planet = [[], args[1]]
        ordertype = findOrderDesc("Send Points")
        args = [0, objectId, -1, ordertype.subtype, 0, [], planet]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersLoadArmament(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_load_armament(int,list)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        weapons = [[], args[1]]
        ordertype = findOrderDesc("Load Armament")
        args = [0, objectId, -1, ordertype.subtype, 0, [], weapons]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrdersUnloadArmament(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_unload_armament(int,list)")
    for orderConstraint in orders:
        args = orderConstraint.args
        objectId = int(args[0])
        weapons = [[], args[1]]
        ordertype = findOrderDesc("Unload Armament")
        args = [0, objectId, -1, ordertype.subtype, 0, [], weapons]
        order = ordertype(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrder(cache, connection, objectId, order):
    # get the queue for the object
    queueid = extra.objectutils.getOrderQueueList(cache, objectId)[0][1]
    queue = cache.orders[queueid]
    node = queue.first
    
    #check if there is no existing order
    if order != None and queue.first.CurrentOrder is None:
        # make a new order   
        evt = cache.apply("orders", "create after", queueid, node, order)
        tp.client.cache.apply(connection, evt, cache)
    #check if the existing order is the same as current order
    elif not checkIfOrdersSame(node.CurrentOrder, order):
        if order != None:
            #replace the current order with the new one
            evt = cache.apply("orders", "change", queueid, node, order)
            tp.client.cache.apply(connection, evt, cache)
        #delete order
        else:
            nodes = [x for x in queue]
            evt = cache.apply("orders", "remove", queueid, nodes=nodes)
            tp.client.cache.apply(connection, evt, cache)

def checkIfOrdersSame(order1, order2):
    #check if both are None
    if order1 is None and order2 is None:
        return True
    #check the type
    if type(order1) != type(order2):
        return False
    #check the name TODO: might be included in type
    if order1._name != order2._name:
        return False
    #check the order arguments
    if order1.properties != order2.properties:
        return False
    return True

def findOrderDesc(name):
    name = name.lower()
    for d in OrderDescs().values():
        if d._name.lower() == name:
            return d
           
def canColonise(fleet):
    listOfShips = helper.shipsOfFleet(fleet)
    for (type, design, number) in listOfShips:
        if helper.designPropertyValue(design, "colonise") == "Yes":
            return True
    return False

def waitingAI():
    print "I am lazy."
    return

def addShipDesign(components):
    helper.addDesign(helper.generateDesignName(components), "", helper.categoryByName("ships"), components)
    
def addWeaponDesign(components):
    helper.addDesign(helper.generateDesignName(components), "", helper.categoryByName("weapons"), components)

#serial number for numbering fleets when naming for tracking purposes
fleetSerialNumber = 0

def buildShip(planet, ship):
    global fleetSerialNumber
    print "building ships on", helper.name(planet)
    orderBuildFleet(planet, [(ship, 1)], helper.playerName(helper.whoami()) + "'s fleet #" + str(fleetSerialNumber))
    fleetSerialNumber += 1
    
def buildWeapon(planet, weapon):
    print "building weapons on" , helper.name(planet)
    orderBuildWeapon(planet, [(weapon, 1)])
    
def orderOfID(objectId):
    #TODO think about adding this to helper
    # get the queue for the object
    queueid = extra.objectutils.getOrderQueueList(cache, objectId)[0][1]
    queue = cache.orders[queueid]
    #return current order
    return queue.first.CurrentOrder

def commandoAI():
    print "I am Rambo."
    #this code will be very similar to rushAI (only with stronger ships)
    return

#TODO think about what if another object gets the same id after the fleet was destroyed
invasionFleets = []

def rushAI():
    global invasionFleets
    print "I am Zerg."
    
    #number of ships and weapons needed to start an invasion
    invasionShips = 10
    invasionWeaponsPerShip = 2
    
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship += [[helper.componentByName("frigate"), 1]]
    #ship += [[helper.componentByName("colonisation module"), 1]]
    ship += [[helper.componentByName("delta missile tube"), 1]]
    ship += [[helper.componentByName("delta missile rack"), 1]]
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #construct a design for a missile that fits the ship
    weapon = []
    weapon += [[helper.componentByName("delta missile hull"), 1]]
    weapon += [[helper.componentByName("uranium explosives"), 2]]
    #add the design
    addWeaponDesign(weapon)
    weaponName = helper.generateDesignName(weapon)
    #replace the list of components with the id
    weapon = helper.designByName(weaponName)
    
    #TODO make this go away
    #debugging only, skip turn to add designs
    if ship == -1 or weapon == -1:
        return
    
    #build ships on all planets (and load them with weapons)
    for myPlanet in helper.myPlanets():
        currentOrder = orderOfID(myPlanet) 
        print "checking what to do with", helper.name(myPlanet)
        #check if there is already something being build on this planet
        if currentOrder == None:
            #load ships with weapons and build more weapons if necessary
            orderGiven = False
            weaponsLoaded = 0
            for thingOnPlanet in helper.contains(myPlanet):
                if helper.isMyFleet(thingOnPlanet):
                    #check if it's rushAI design
                    listOfShips = helper.shipsOfFleet(thingOnPlanet)
                    #TODO take care of all ships not just rushAI design
                    if listOfShips == [(9, ship, 1)]:
                        weaponsNeeded = invasionWeaponsPerShip - helper.resourceAvailable(thingOnPlanet, helper.designName(weapon))
                        print helper.name(thingOnPlanet), "needs", weaponsNeeded, "more weapons"
                        if weaponsNeeded > 0:
                            #check if there is weapons available on the planet to load
                            weaponsOnPlanet = helper.resourceAvailable(myPlanet, helper.designName(weapon)) - weaponsLoaded
                            print weaponsOnPlanet, "weapons are on planet" 
                            if weaponsOnPlanet > 0:
                                #load as much as possible
                                print "loading weapons onto", helper.name(thingOnPlanet)
                                orderLoadArmament(thingOnPlanet, [(helper.resourceByName(helper.designName(weapon)), min(weaponsNeeded, weaponsOnPlanet))])
                                weaponsLoaded += min(weaponsNeeded, weaponsOnPlanet)
                            else:
                                #build more weapons
                                buildWeapon(myPlanet, weapon)
                                orderGiven = True
                                break
            #build a new ship if there is no orders to build weapons
            if not orderGiven:
                buildShip(myPlanet, ship)
                
    #check how many fleets are available for the invasion
    potentialInvasionFleets = helper.myFleets()
    #remove all of the fleets that are already marked for the invasion
    for fleet in invasionFleets:
        potentialInvasionFleets.remove(fleet)
    #remove all of the fleets that are not fully loaded with weapons
    for fleet in potentialInvasionFleets:
        #TODO make this work for all designs
        if helper.shipsOfFleet(fleet) != [(9, ship, 1)]:
            potentialInvasionFleets.remove(fleet)
            continue
        #remove ship if its not loaded with weapons
        if helper.resourceAvailable(fleet, helper.designName(weapon)) < invasionWeaponsPerShip:
            potentialInvasionFleets.remove(fleet)
            continue
        
        
    guardOnPlanets = {}
    allMyPlanets = helper.myPlanets()
    defenceShips = 1
    #mark fleets for invasion
    print "there are", len(potentialInvasionFleets), "fleets ready for invasion"
    if len(potentialInvasionFleets) >= invasionShips:
        for fleet in potentialInvasionFleets:
            parent = helper.containedBy(fleet)        
            #if the fleet is on one of our planets and the number of fleets on that planet
            #is less than the minimum don't send the ships away
            if parent in allMyPlanets:
                #how many fleets are guarding this planet
                currentGuard = 0
                if parent in guardOnPlanets:
                    currentGuard = guardOnPlanets[parent]
                #if not enough fleets are guarding add this one
                if currentGuard < defenceShips:
                    guardOnPlanets[parent] = currentGuard + 1
                    continue
            #mark it for invasion
            invasionFleets += [fleet]
        
    allMyFleets = helper.myFleets()
    #attack the enemy with ships marked for invasion
    for fleet in invasionFleets:
        if not fleet in allMyFleets:
            #this is not my fleet anymore... remove it
            invasionFleets.remove(fleet)
        print helper.name(fleet), "is invading (beware!)"
        #find a planet to attack
        nearestPlanet = helper.nearestEnemyPlanet(helper.position(fleet))
        #move to that planet
        if nearestPlanet != None:
            print helper.name(fleet), "is attacking", helper.name(nearestPlanet) 
            orderMove(fleet, helper.position(nearestPlanet))
        else:
            print helper.name(fleet), "has nothing to attack"
        #TODO find out if you have to colonise a planet to take it over
    
    #make a list of fleets not marked for invasion
    freeFleets = helper.myFleets()
    for fleet in invasionFleets:
        freeFleets.remove(fleet)
    
    #give orders to ships not marked for invasion
    #move ships to neutral planets and colonise them (leave some ships on every planet for defense)
    defenceShips = 3
    planetsToIgnore = []
    guardOnPlanets = {}
    for fleet in freeFleets:  
        parent = helper.containedBy(fleet)        
        #if the fleet is on one of our planets and the number of fleets on that planet
        #is less than the minimum don't send the ships away
        if parent in allMyPlanets:
            #how many fleets are guarding this planet
            currentGuard = 0
            if parent in guardOnPlanets:
                currentGuard = guardOnPlanets[parent]
            #if not enough fleets are guarding add this one
            if currentGuard < defenceShips:
                guardOnPlanets[parent] = currentGuard + 1
                #make it stay there
                #TODO can this destroy our loading orders?
                orderNone(fleet)
                continue

        #move only ships that can colonise other planets
        if canColonise(fleet):                
            nearestPlanet = helper.nearestNeutralPlanet(helper.position(fleet), planetsToIgnore)
            planetPosition = helper.position(nearestPlanet)
            planetsToIgnore += [nearestPlanet]
            
            if helper.position(fleet) == planetPosition:
                #colonise if there
                print helper.name(fleet), "is colonising", helper.name(nearestPlanet)
                orderColonise(fleet)
                pass
            else:
                #move to planet
                print "moving", helper.name(fleet), "to", helper.name(nearestPlanet)
                orderMove(fleet, planetPosition)
    return
    
def randomAI():
    print "I am confused."
    return
    
def bunkerAI():
    print "I am paranoid"
    return

def greedyAI():
    print "I am not wealthy enough"
    #this code will be very similar to rushAI (only without attacking)
    return
    
def multipleAI():
    print "I am a shapeshifter."
    return

def AICode():
    print "It's turn", helper.turnNumber()
    #helper.printAboutMe()
    #helper.printDesignsWithProperties()
    rushAI()
    return

"""\
list of possible components

scout hull
battle scout hull
advanced battle scout hull
frigate
battle frigate
destroyer
battle destroyer
battleship
dreadnought
argonaut

uranium explosives
thorium explosives
cerium explosives
enriched uranium
massivium
antiparticle explosives
antimatter explosives

alpha missile tube
alpha missile rack
alpha missile hull
beta missile tube
beta missile rack
beta missile hull
gamma missile tube
gamma missile rack
gamma missile hull
delta missile tube
delta missile rack
delta missile hull
epsilon missile tube
epsilon missile rack
epsilon missile hull

omega torpedoe tube
omega torpedoe rack
omega torpedoe hull
upsilon torpedoe tube
upsilon torpedoe rack
upsilon torpedoe hull
tau torpedoe tube
tau torpedoe rack
tau torpedoe hull
sigma torpedoe tube
sigma torpedoe rack
sigma torpedoe hull
rho torpedoe tube
rho torpedoe rack
rho torpedoe hull
xi torpedoe tube
xi torpedoe rack
xi torpedoe hull

armor
colonisation module
"""
