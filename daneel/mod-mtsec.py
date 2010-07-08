'''
@author: Damjan 'Null' Kosir
'''
import logging
import tp.client.cache
from tp.netlib.objects import OrderDescs
import extra.objectutils
import helper
import random
from time import sleep
import math

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
    assert len(pos) == 3
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

def orderSplitFleet(fleetid, ships):
    '''
    Split the fleet into two
    id is for the object the order is for
     Arg name: ships    Arg type: List (code:6)    Arg desc: The ships to be transferred
    '''
    global rulesystem
    rulesystem.addConstraint("order_split_fleet(" + str(fleetid) + ", " + str(ships) + ")")
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
    helper.addDesign(helper.generateDesignName(components), "its a ship", helper.categoryByName("ships"), components)
    return helper.designByName(helper.generateDesignName(components))
    
def addWeaponDesign(components):
    helper.addDesign(helper.generateDesignName(components), "it's a weapon", helper.categoryByName("weapons"), components)

#serial number for numbering fleets when naming for tracking purposes
fleetSerialNumber = 0

def buildShip(planet, ship, numberOfShips=1):
    global fleetSerialNumber
    print "building ships on", helper.name(planet), "(", helper.designName(ship), ")"
    orderBuildFleet(planet, [(ship, numberOfShips)], helper.playerName(helper.whoami()) + "'s fleet #" + str(fleetSerialNumber))
    fleetSerialNumber += 1
    
def factories(planet):
    return helper.resourceAvailable(planet, "Factories")

def optimalBuildWeapon(planet, weaponDict, explosivesList, maxExplosives, maxPointsToWaste=0.2, maxTurns=1, pointsAlreadyUsed=0):
    '''
    weaponDict - dictionary of number of weapons needed to be build by type {"alpha":3,"xi":2}
    '''
    #TODO correct this when mining gets implemented (if ever)
    #currently a 1 production point is used for every component of the weapon (1 for the hull and 1 for each unit of explosives)
    #this means only the first explosive from the explosives list will be used (and it is meaningless to use anything but the strongest)
    #the current implementation ignores most of the optional arguments and just builds as many weapons as possible in a single turn
    
    #factories on planet
    factoriesOnPlanet = factories(planet) - pointsAlreadyUsed
    buildList = []
    for type in weaponDict.keys():
        design = designWeapon(type, explosivesList[0], maxExplosives)
        #cost of one unit of this design
        cost = 0
        #count the number of parts used
        for (id, number) in helper.designComponents(design):
            cost += number
        #calculate how many units of this type of weapon you can build
        numberToBuild = factoriesOnPlanet / cost
        if numberToBuild == 0:
            continue
        factoriesOnPlanet -= numberToBuild * cost
        buildList.append((design, numberToBuild))
    
    assert buildList != []
    orderBuildWeapon(planet, buildList)
    

def optimalBuildShip(planet, ship, maxPointsToWaste=0.2, maxTurns=5, pointsAlreadyUsed=0):
    '''
    maxPointsToWaste is the % of the production points that can go unused. (0.0 - 1.0)
    '''    
    #factories on planet
    factoriesOnPlanet = factories(planet)
    #TODO make this global
    #dictionary of hull sizes
    hullSize = {"scout hull":60.0, "battle scout hull":80.0, "advanced battle scout hull":133.0, "frigate":200.0, "battle frigate":200.0, "destroyer":300.0, "battle destroyer":300.0, "battleship":375.0, "dreadnought":500.0, "argonaut":1000.0}
    size = 0
    
    #create the design
    design = addShipDesign(ship)
    
    #get the size for this design
    for (id, number) in helper.designComponents(design):
        name = helper.componentName(id).lower()
        #if the component is a hull 
        if hullSize.has_key(name):
            size = hullSize[name]
            break
    assert size > 0
    #calculate how many points do you need to build 1 ship
    pointsPerShip = int(math.ceil(size / 10.0))
    numberToBuild = 0
    points = -pointsAlreadyUsed
    for turn in xrange(maxTurns):
        #calculate production points available at 1 + turn turns
        points += min(factoriesOnPlanet + turn, 100)
        #how many ships you could build in 1 + turn turns
        numberToBuild = points / pointsPerShip
        #check if there are little enough points wasted
        if points - numberToBuild * pointsPerShip <= points * maxPointsToWaste:
            break
    #in case 1 ships takes longer than maxTurns to build, build just one
    if numberToBuild == 0:
        numberToBuild = 1
    
    buildShip(planet, design, numberToBuild)
    #TODO return the number of points used (in the current turn)
    
def buildWeapon(planet, weapon, numberOfWeapons=1):
    print "building weapons on" , helper.name(planet)
    orderBuildWeapon(planet, [(weapon, numberOfWeapons)])

def moveToObject(objectToMove, objectToMoveTo):
    orderMove(objectToMove, helper.position(objectToMoveTo))
    


def designWeapon(type, explosive, maxExplosives=1000):
    '''
    Creates a design for a weapon of specified type using the maximum amount of specified explosives. Returns the id of the design.
    Example: for delta missile with uranium explosives use designWeapon("delta","uranium explosives")
    '''
    #TODO this could be global
    weaponSize = {"alpha":3.0, "beta":6.0, "gamma":8.0, "delta":12.0, "epsilon":24.0, "omega":40.0, "upsilon":60.0, "tau":80.0, "sigma":110.0, "rho":150.0, "xi":200.0}
    explosiveSize = {"uranium explosives":4.0, "thorium explosives":4.5, "cerium explosives":3.0, "enriched uranium":2.0, "massivium":12.0, "antiparticle explosives":0.8, "antimatter explosives":0.5}
    weaponHullDict = {"alpha":helper.componentByName("alpha missile hull"), "beta":helper.componentByName("beta missile hull"), "gamma":helper.componentByName("gamma missile hull"), "delta":helper.componentByName("delta missile hull"), "epsilon":helper.componentByName("epsilon missile hull"), "omega":helper.componentByName("omega torpedoe hull"), "upsilon":helper.componentByName("upsilon torpedoe hull"), "tau":helper.componentByName("tau torpedoe hull"), "sigma":helper.componentByName("sigma torpedoe hull"), "rho":helper.componentByName("rho torpedoe hull"), "xi":helper.componentByName("xi torpedoe hull")}
    
    #make a list of components to use (and calculate the max amount of explosives)
    #TODO this is the real version, the other one if in use until the bug is fixed
    #components = [(weaponHullDict[type], 1), (helper.componentByName(explosive), min(int(math.floor(weaponSize[type] / explosiveSize[explosive]),maxExplosives)))]
    components = [(weaponHullDict[type], 1), (helper.componentByName(explosive), min(1, maxExplosives))]
    addWeaponDesign(components)
    return helper.designByName(helper.generateDesignName(components)) 

def maxWeaponsOfDesign(design):
    '''
    Returns a dictionary of types of weapons the design (name or id) can carry. {"alpha":4,"beta":1,...}
    '''
    if isinstance(design, str):
        design = helper.designByName(design)

    #TODO this could be made global
    tubeDict = {helper.componentByName("alpha missile tube"):"alpha", helper.componentByName("beta missile tube"):"beta", helper.componentByName("gamma missile tube"):"gamma", helper.componentByName("delta missile tube"):"delta", helper.componentByName("epsilon missile tube"):"epsilon", helper.componentByName("omega torpedoe tube"):"omega", helper.componentByName("upsilon torpedoe tube"):"upsilon", helper.componentByName("tau torpedoe tube"):"tau", helper.componentByName("sigma torpedoe tube"):"sigma", helper.componentByName("rho torpedoe tube"):"rho", helper.componentByName("xi torpedoe tube"):"xi"}
    missileRackDict = {helper.componentByName("alpha missile rack"):"alpha", helper.componentByName("beta missile rack"):"beta", helper.componentByName("gamma missile rack"):"gamma", helper.componentByName("delta missile rack"):"delta", helper.componentByName("epsilon missile rack"):"epsilon"}
    torpedoRackDict = {helper.componentByName("omega torpedoe rack"):"omega", helper.componentByName("upsilon torpedoe rack"):"upsilon", helper.componentByName("tau torpedoe rack"):"tau", helper.componentByName("sigma torpedoe rack"):"sigma", helper.componentByName("rho torpedoe rack"):"rho", helper.componentByName("xi torpedoe rack"):"xi"}
        
    weapons = {}
    for (component, numberOfUnits) in helper.designComponents(design):
        #is the component a tube?
        #each tube can carry 1 weapon
        if tubeDict.has_key(component):
            type = tubeDict[component]
            if weapons.has_key(type):
                weapons[type] += numberOfUnits 
            else:
                weapons[type] = numberOfUnits
            continue
        #is the component a missile rack?
        #each missile rack can carry 2 weapons
        if tubeDict.has_key(component):
            type = tubeDict[component]
            if weapons.has_key(type):
                weapons[type] += numberOfUnits * 2 
            else:
                weapons[type] = numberOfUnits * 2
            continue
        #is the component a torpedo rack?
        #each torpedo rack can carry 4 weapons
        if tubeDict.has_key(component):
            type = tubeDict[component]
            if weapons.has_key(type):
                weapons[type] += numberOfUnits * 4 
            else:
                weapons[type] = numberOfUnits * 4
            continue
        #this component doesn't affect the number of weapons directly
    return weapons

def maxWeaponsOfFleet(fleetid):
    '''
    Returns a dictionary of types of weapons the fleet can carry. {"alpha":4,"beta":1,...}
    '''
    maxWeapons = {}
    #find out the sum of weapons all the ships in this fleet can hold (and ther types)
    for (something, design, number) in helper.shipsOfFleet(fleetid):
        tempMaxWeapons = maxWeaponsOfDesign(design)
        #add all the weapons to the sum
        for weaponType in tempMaxWeapons.keys():
            if maxWeapons.has_key(weaponType):
                maxWeapons[weaponType] += tempMaxWeapons[weaponType] * number
            else:
                maxWeapons[weaponType] = tempMaxWeapons[weaponType] * number
    return maxWeapons

def typeOfWeapon(design):
    '''
    Returns the type of weapon. Example if the design contains an alpha missile hull the function returns "alpha"
    '''
    #TODO make this global and initialse it only once
    reverseWeaponHullDict = {helper.componentByName("alpha missile hull"):"alpha", helper.componentByName("beta missile hull"):"beta", helper.componentByName("gamma missile hull"):"gamma", helper.componentByName("delta missile hull"):"delta", helper.componentByName("epsilon missile hull"):"epsilon", helper.componentByName("omega torpedoe hull"):"omega", helper.componentByName("upsilon torpedoe hull"):"upsilon", helper.componentByName("tau torpedoe hull"):"tau", helper.componentByName("sigma torpedoe hull"):"sigma", helper.componentByName("rho torpedoe hull"):"rho", helper.componentByName("xi torpedoe hull"):"xi"}
    components = helper.designComponents(design)
    #loop through all components and look for a match
    for (id, value) in components:
        if reverseWeaponHullDict.has_key(id):
            return reverseWeaponHullDict[id]
    return None

def weaponsNeeded(fleetid):
    '''
    Returns a dictionary of weapons that can be loaded by type {"alpha":3,"delta":1,...}
    '''
    maxWeapons = maxWeaponsOfFleet(fleetid)
    #get the weapons already loaded on board the fleet [(resource id, number of units),...]
    weaponsLoaded = weaponsOnObject(fleetid)
    # a dictionary for weapons that could be loaded by type
    weaponsNeededDict = {}
    for type in maxWeapons.keys():
        if weaponsLoaded.has_key(type):
            if maxWeapons[type] > weaponsLoaded[type]:
                weaponsNeededDict[type] = maxWeapons[type] - weaponsLoaded[type]
        else:
            weaponsNeededDict[type] = maxWeapons[type]
    return weaponsNeededDict

def weaponsOnObject(objectid):
    '''
    Returns a dictionary of weapons on this object (available on planet or loaded on fleet) by type. {"alpha":3,"delta":1,...}
    '''
    stuffOnObject = [(resource[0], resource[1]) for resource in helper.resources(objectid)]
    #build a dict of all the weapons loaded by type
    weaponsLoaded = {}
    for (id, number) in stuffOnObject:
        #ignore if there is 0 units (why does it even report it then?)
        if number == 0:
            continue
        #find a design id from the resource id (they have the same name)
        resourceName = helper.resourceName(id)
        designid = helper.designByName(resourceName)
        if designid == None:
            #resource is not a weapon
            continue
        type = typeOfWeapon(designid)
        if type == None:
            #design not a weapon design
            continue
        #add to the list of weapons
        if weaponsLoaded.has_key(type):
            weaponsLoaded[type] += number
        else:
            weaponsLoaded[type] = number
    return weaponsLoaded
            
def loadWeapons(fleet, planet, weaponDict, alreadyLoaded={}):
    '''
    Gives a Load Armament order for all weapons in the weapon dictionary.
    Already loaded dictionary provides how many weapons of each type have already been asigned to other ships.
    '''
    stuffOnPlanet = [(resource[0], resource[1]) for resource in helper.resources(planet)]
    stuffToLoad = []
    
    #make a copy so we don't change the original
    alreadyLoaded2 = alreadyLoaded.copy()
    weaponDict2 = weaponDict.copy()

    #for every type we need to load
    for typeToLoad in weaponDict2.keys():
        #loop through all the resources on the planet until we add enough weapons of this type to the loading list
        for (id, available) in stuffOnPlanet:
            #find a design id from the resource id (they have the same name)
            resourceName = helper.resourceName(id)
            designid = helper.designByName(resourceName)
            if designid == None:
                #resource is not a weapon
                continue
            type = typeOfWeapon(designid)
            if type == None:
                #design not a weapon design
                continue
            #check the type of the weapon
            if type == typeToLoad:
                #how many are to be loaded to other ships
                markedForLoading = 0
                if alreadyLoaded2.has_key(type):
                    markedForLoading = alreadyLoaded2[type]
                #number of weapon we can load
                canLoad = available - markedForLoading
                #if we can load any of them
                if canLoad > 0:
                    willLoad = min(canLoad, weaponDict2[type])
                    #add weapons to the list of weapons to load
                    stuffToLoad.append((id, willLoad))
                    
                    #reduce the number of this type that need loading
                    weaponDict2[type] -= willLoad
                    
                    #we have passed all the weapons that were marked for other ships
                    alreadyLoaded2[type] = 0
                    
                    #continue to another type if all weapons of this type have been marked for loading
                    if weaponDict2[type] == 0:
                        break
                #all are to be loaded to ther ships    
                else:
                    if alreadyLoaded2.has_key(type):
                        alreadyLoaded2[type] -= available
    
    assert stuffToLoad != []
    orderLoadArmament(fleet, stuffToLoad)

#list of fleets marked for invasion
invasionFleets = []

def commandoAI():
    '''
    AI player that builds strong units and attacks fast.
    '''
    print "I am Rambo."
    
    #number of ships and weapons needed to start an invasion
    invasionShips = 1
    #retreat if less than this number of ships marked for invasion
    invasionShipsRetreat = 0
    #ships left on every planet when there is an invasion
    defenceShipsOnInvasion = 0
    #ships left on every planet (others go colonise)
    defenceShips = 0
    
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship.append([helper.componentByName("dreadnought"), 1])
    #ship.append([helper.componentByName("colonisation module"), 1])
    ship.append([helper.componentByName("xi torpedoe tube"), 2])
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #choose a cheap explosives for use in weapons
    explosive = "antimatter explosives"
    
    stupidAIBase(ship, explosive, invasionShips, invasionShipsRetreat, defenceShipsOnInvasion, defenceShips)

def rushAI():
    '''
    AI player that builds large armies of cheap units and attacks in waves.
    '''
    print "I am Zerg."
    
    #number of ships and weapons needed to start an invasion
    invasionShips = 10
    #retreat if less than this number of ships marked for invasion
    invasionShipsRetreat = 3
    #ships left on every planet when there is an invasion
    defenceShipsOnInvasion = 1
    #ships left on every planet (others go colonise)
    defenceShips = 3
    
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship.append([helper.componentByName("advanced battle scout hull"), 1])
    #ship.append([helper.componentByName("colonisation module"), 1])
    ship.append([helper.componentByName("delta missile tube"), 1])
    ship.append([helper.componentByName("delta missile rack"), 1])
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #choose a cheap explosives for use in weapons
    explosive = "enriched uranium"
    
    stupidAIBase(ship, explosive, invasionShips, invasionShipsRetreat, defenceShipsOnInvasion, defenceShips)
    
def stupidAIBase(ship, explosive, invasionShips, invasionShipsRetreat, defenceShipsOnInvasion, defenceShips):
    global invasionFleets
    print "I am not the smartest one."
    
    #build ships on all planets (and load them with weapons)
    for myPlanet in helper.myPlanets():
        print "checking what to do with", helper.name(myPlanet)
        #check if there is already something being build on this planet
        if not helper.hasOrder(myPlanet):
            #load ships with weapons and build more weapons if necessary
            #what type of weapon should be build
            weaponToBuild = None

            weaponsOnPlanet = weaponsOnObject(myPlanet)
            #weapons already loaded
            weaponsLoadedDict = {}
            
            for thingOnPlanet in helper.contains(myPlanet):
                if helper.isMyFleet(thingOnPlanet):
                    #find out if it needs any more weapons
                    weaponsNeededDict = weaponsNeeded(thingOnPlanet)
                    #if no needed weapons skip this fleet
                    if len(weaponsNeededDict) == 0:
                        continue
                    
                    #make a list of all weapons that will be loaded
                    weaponsToLoadDict = {}
                    for typeOfWeaponNeeded in weaponsNeededDict.keys():
                        available = 0
                        if weaponsOnPlanet.has_key(typeOfWeaponNeeded):
                            available = weaponsOnPlanet[typeOfWeaponNeeded]
                            if weaponsLoadedDict.has_key(typeOfWeaponNeeded):
                                available -= weaponsLoadedDict[typeOfWeaponNeeded]
                            assert available >= 0
                            #if there are any to load
                            if available > 0:
                                #mark weapons for loading
                                weaponsToLoadDict[typeOfWeaponNeeded] = min(available, weaponsNeededDict[typeOfWeaponNeeded])
                        #give build order if nesessary
                        if weaponToBuild == None and available < weaponsNeededDict[typeOfWeaponNeeded]:
                            weaponToBuild = typeOfWeaponNeeded
                    #if there is anything to load
                    if weaponsToLoadDict != {}:
                        #actualy load the weapons...
                        loadWeapons(thingOnPlanet, myPlanet, weaponsToLoadDict, weaponsLoadedDict)
                        #mark them as loaded
                        for type in weaponsToLoadDict.keys():
                            #make sure other ships don't try to load the same weapons
                            if weaponsLoadedDict.has_key(type):
                                weaponsLoadedDict[type] += weaponsToLoadDict[type]
                            else:
                                weaponsLoadedDict[type] = weaponsToLoadDict[type]
                    
            #build weapons/ships order
            if weaponToBuild == None:
                #no weaopns to build... build a ship
                buildShip(myPlanet, ship)
            else:
                #build a weapon of the required type
                buildWeapon(myPlanet, designWeapon(weaponToBuild, explosive))    

    allMyFleets = helper.myFleets() 
    removeFromInvasionFleets = []
    for fleet in invasionFleets:
        #mark nonexistant fleets (probably destroyed) for removal
        if fleet not in allMyFleets:
            removeFromInvasionFleets.append(fleet)        
    #remove all nonexistent fleets
    for fleet in removeFromInvasionFleets:
        invasionFleets.remove(fleet)

    #check how many fleets are available for the invasion
    potentialInvasionFleets = helper.myFleets()
    removeFromInvasionFleets = []
    #remove all of the fleets that are already marked for the invasion and fleets that can no longer fight (no weapons)
    for fleet in invasionFleets:
        potentialInvasionFleets.remove(fleet)
        #if it can no longer attack
        if weaponsOnObject(fleet) == {}:
            print helper.name(fleet), "is no longer invading"
            removeFromInvasionFleets.append(fleet)
    #remove all fleet without weapons
    for fleet in removeFromInvasionFleets:
        invasionFleets.remove(fleet)

    #remove all of the fleets that are not fully loaded with weapons
    removeFromPotentialInvasionFleets = []
    for fleet in potentialInvasionFleets:
        #remove ship if it's not loaded with weapons
        if weaponsOnObject(fleet) != maxWeaponsOfFleet(fleet):
            removeFromPotentialInvasionFleets.append(fleet)
    for fleet in removeFromPotentialInvasionFleets:
        potentialInvasionFleets.remove(fleet)
    
        
    guardOnPlanets = {}
    allMyPlanets = helper.myPlanets()
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
                if currentGuard < defenceShipsOnInvasion:
                    guardOnPlanets[parent] = currentGuard + 1
                    continue
            #mark it for invasion
            invasionFleets.append(fleet)
    
    #make the invasion fleets go back if there are only a few of them left
    if len(invasionFleets) < invasionShipsRetreat:
        print "to little attack ships. Retreat!"
        invasionFleets = [] 
    
    #attack the enemy with ships marked for invasion
    for fleet in invasionFleets:
        print helper.name(fleet), "is invading (beware!)"
        #find a planet to attack
        nearestPlanet = helper.nearestEnemyPlanet(helper.position(fleet))
        #move to that planet
        if nearestPlanet != None:
            print helper.name(fleet), "is attacking", helper.name(nearestPlanet) 
            planetPosition = helper.position(nearestPlanet)
            if helper.position(fleet) != planetPosition:
                orderMove(fleet, planetPosition)
        else:
            print helper.name(fleet), "has nothing to attack"
    
    #make a list of fleets not marked for invasion
    freeFleets = helper.myFleets()
    for fleet in invasionFleets:
           freeFleets.remove(fleet)
    
    #give orders to ships not marked for invasion
    #move ships to neutral planets and colonise them (leave some ships on every planet for defense)
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
                orderNone(fleet)
                continue

        #move only ships that can colonise other planets
        if canColonise(fleet):                
            nearestPlanet = helper.nearestNeutralPlanet(helper.position(fleet), planetsToIgnore)
            if nearestPlanet == None:
                print helper.name(fleet), "has no planet to colonise."
            else:
                planetPosition = helper.position(nearestPlanet)
                planetsToIgnore.append(nearestPlanet)
                
                if helper.position(fleet) == planetPosition:
                    #colonise if there
                    print helper.name(fleet), "is colonising", helper.name(nearestPlanet)
                    orderColonise(fleet)
                    pass
                else:
                    #move to planet
                    print "moving", helper.name(fleet), "to", helper.name(nearestPlanet)
                    orderMove(fleet, planetPosition)
        #other ships should go to a friendly palanet for suplies (if not already there)
        else:
            nearestPlanet = helper.nearestMyPlanet(helper.position(fleet))
            assert nearestPlanet != None
            planetPosition = helper.position(nearestPlanet)
            #move if not already there
            if helper.position(fleet) != planetPosition:
                print "moving", helper.name(fleet), "to", helper.name(nearestPlanet)
                orderMove(fleet, planetPosition)
    return
    
def randomAI():
    '''
    AI player that selects randomly from a set of predefined actions.
    '''
    print "I am confused."
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship.append([helper.componentByName("advanced battle scout hull"), 1])
    #ship.append([helper.componentByName("colonisation module"), 1]) 
    ship.append([helper.componentByName("delta missile tube"), 1])
    ship.append([helper.componentByName("delta missile rack"), 1])
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #construct a design for a missile that fits the ship
    weapon = []
    weapon.append([helper.componentByName("delta missile hull"), 1])
    weapon.append([helper.componentByName("enriched uranium"), 2])
    #add the design
    addWeaponDesign(weapon)
    weaponName = helper.generateDesignName(weapon)
    #replace the list of components with the id
    weapon = helper.designByName(weaponName)
    
    #give orders to planets
    for myPlanet in helper.myPlanets():
        #only give orders if the planet has none
        if helper.hasOrdeR(myPlanet):
            print helper.name(myPlanet), "already has orders"
            continue
        #list available actions
        actionList = ["wait", "buildShip", "buildWeapon"]
        
        #pick an action
        action = random.choice(actionList)
        if action == "buildShip":
            buildShip(myPlanet, ship)
            continue
        if action == "buildWeapon":
            buildWeapon(myPlanet, weapon)
            continue
        print "doing nothing on", helper.name(myPlanet)
        
    #give orders to fleets
    for fleet in helper.myFleets():
        #only give orders if the fleet has none
        if helper.hasOrder(fleet):
            print helper.name(fleet), "already has orders"
            continue
        #automatic weapon loading if on friendly planet with weapons
        #TODO this only works for fleets specified earlier
        maxMissiles = 3
        if helper.shipsOfFleet(fleet) == [(9, ship, 1)]: 
            nearestMyPlanet = helper.nearestMyPlanet(fleet)
            if helper.position(fleet) == helper.position(nearestMyPlanet):
                weaponsOnFleet = helper.resourceAvailable(fleet, helper.designName(weapon))
                if weaponsOnFleet < maxMissiles:
                    weaponsOnPlanet = helper.resourceAvailable(nearestMyPlanet, helper.designName(weapon))
                    if weaponsOnPlanet > 0:
                        weaponsToLoad = min(maxMissiles - weaponsOnFleet, weaponsOnPlanet)
                        orderLoadArmament(fleet, [(helper.resourceByName(helper.designName(weapon)), weaponsToLoad)])
        
        #TODO maybe add an automatic colonisation if on neutral planet and can colonise
        
        #list available actions
        actionList = ["wait", "colonise", "attack", "move to friendly planet", "move to neutral planet"]
        #remove colonise option if the fleet can't colonise planets
        if not canColonise(fleet):
            actionList.remove("colonise")
        #remove the colonise option if the fleet is not on an neutral planet
        elif helper.position(fleet) != helper.position(helper.nearestNeutralPlanet(fleet)):            
            actionList.remove("colonise")
        #remove attack option if the fleet has no weapons on board 
        if not helper.resourceAvailable(fleet, helper.designName(weapon)) > 0:
             actionList.remove("attack")
        
        #pick an action
        action = random.choice(actionList)
        if action == "colonise":
            print helper.name(fleet), "is colonising", helper.name(helper.nearestNeutralPlanet(fleet))
            orderColonise(fleet)
            continue
        if action == "attack":
            #find 3 nearest enemy planets
            nearestEnemyPlanets = [helper.nearestEnemyPlanet(fleet)]
            nearestEnemyPlanets.append(helper.nearestEnemyPlanet(fleet, nearestEnemyPlanets))
            nearestEnemyPlanets.append(helper.nearestEnemyPlanet(fleet, nearestEnemyPlanets))
            #remove Nones
            while None in nearestEnemyPlanets:
                nearestEnemyPlanets.remove(None)
            #pick one to attack
            planetToAttack = random.choice(nearestEnemyPlanets) 
            #attack it
            moveToObject(fleet, planetToAttack)
            print helper.name(fleet), "is attacking", helper.name(planetToAttack)
            continue
        if action == "move to friendly planet":
            #find 3 nearest enemy planets
            nearestMyPlanets = [helper.nearestMyPlanet(fleet)]
            nearestMyPlanets.append(helper.nearestMyPlanet(fleet, nearestMyPlanets))
            nearestMyPlanets.append(helper.nearestMyPlanet(fleet, nearestMyPlanets))
            #remove Nones
            while None in nearestMyPlanets:
                nearestMyPlanets.remove(None)
            #pick one to attack
            planetToMoveTo = random.choice(nearestMyPlanets)
                        
            #attack it
            moveToObject(fleet, planetToMoveTo)
            print helper.name(fleet), "is moving to a friendly planet", helper.name(planetToMoveTo)
            continue
        if action == "move to neutral planet":
            #find 3 nearest enemy planets
            nearestNeutralPlanets = [helper.nearestNeutralPlanet(fleet)]
            nearestNeutralPlanets.append(helper.nearestNeutralPlanet(fleet, nearestNeutralPlanets))
            nearestNeutralPlanets.append(helper.nearestNeutralPlanet(fleet, nearestNeutralPlanets))
            #remove Nones
            while None in nearestNeutralPlanets:
                nearestNeutralPlanets.remove(None)
            #pick one to attack
            planetToMoveTo = random.choice(nearestNeutralPlanets) 
            #attack it
            moveToObject(fleet, planetToMoveTo)
            print helper.name(fleet), "is moving to a neutral planet", helper.name(planetToMoveTo)
            continue
        print helper.name(fleet), "is doing nothing"    
    return
    
def bunkerAI():
    '''
    AI player that builds strong defences.
    '''
    print "I am paranoid"

    
    #number of ships and weapons needed to start an invasion
    invasionShips = 100
    #retreat if less than this number of ships marked for invasion
    invasionShipsRetreat = 0
    #ships left on every planet when there is an invasion
    defenceShipsOnInvasion = 10
    #ships left on every planet (others go colonise)
    defenceShips = 10
    
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship.append([helper.componentByName("argonaut"), 1])
    #ship.append([helper.componentByName("colonisation module"), 1])
    ship.append([helper.componentByName("xi torpedoe tube"), 4]) #TODO this should be 5 units
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #choose a cheap explosives for use in weapons
    explosive = "antimatter explosives"
    
    stupidAIBase(ship, explosive, invasionShips, invasionShipsRetreat, defenceShipsOnInvasion, defenceShips)

def greedyAI():
    '''
    AI player that expands rapidely, but does not attack.
    '''
    print "I am not wealthy enough"
    
    #number of ships and weapons needed to start an invasion
    invasionShips = 100
    #retreat if less than this number of ships marked for invasion
    invasionShipsRetreat = 3
    #ships left on every planet when there is an invasion
    defenceShipsOnInvasion = 1
    #ships left on every planet (others go colonise)
    defenceShips = 1
    
    #construct a design for a simple attack/colonisation ship
    ship = []
    ship.append([helper.componentByName("advanced battle scout hull"), 1])
    ship.append([helper.componentByName("colonisation module"), 1])
    #ship.append([helper.componentByName("delta missile tube"), 1])
    #ship.append([helper.componentByName("delta missile rack"), 1])
    #add the design
    addShipDesign(ship)
    shipName = helper.generateDesignName(ship)
    #replace the list of components with the id
    ship = helper.designByName(shipName)
    
    #choose a cheap explosives for use in weapons
    explosive = "enriched uranium"
    
    stupidAIBase(ship, explosive, invasionShips, invasionShipsRetreat, defenceShipsOnInvasion, defenceShips)
    
def multipleAI():
    print "I am a shapeshifter."
    #randomly choose one of the other behaviours
    random.choice([rushAI, commandoAI, bunkerAI, greedyAI])()
    return

def smartPlanetCode(ignoreFleets=[]):
    #TODO this should be around 0.25 when the colonisation is working again
    colonisationShipsPercent = 0 #TODO this will vary dynamicaly in the future
    loadPercent = 0.7 #TODO use this, this can vary in the future
    
    #colonisation ship design
    #there is still space for tubes
    colonisationShip = []
    colonisationShip.append([helper.componentByName("advanced battle scout hull"), 1])
    colonisationShip.append([helper.componentByName("colonisation module"), 1])
    
    #attack ship design
    ship = []
    ship.append([helper.componentByName("scout hull"), 1])
    #TODO add max number of tubes to the design, just no need to fill them all
    #there is no need to have this many weapons on one ship (20 is the max)
    ship.append([helper.componentByName("alpha missile tube"), 10])
    
    #list of explosives to use
    explosivesList = ["antimatter explosives", "antiparticle explosives"]
    maxExplosives = 1 #TODO this could be an array for each type or maybe a dictionary
    
    #build ships on all planets (and load them with weapons)
    for myPlanet in helper.myPlanets():
        print "checking what to do with", helper.name(myPlanet)
        #check if there is already something being build on this planet
        if not helper.hasOrder(myPlanet):
            #load ships with weapons and build more weapons if necessary
            #what type of weapon should be build
            weaponsToBuild = {}

            weaponsOnPlanet = weaponsOnObject(myPlanet)
            #weapons already loaded
            weaponsLoadedDict = {}
            
            for thingOnPlanet in helper.contains(myPlanet):
                if helper.isMyFleet(thingOnPlanet):
                    #find out if it needs any more weapons
                    weaponsNeededDict = weaponsNeeded(thingOnPlanet)
                    #if no needed weapons skip this fleet
                    if len(weaponsNeededDict) == 0:
                        continue
                    
                    #make a list of all weapons that will be loaded
                    weaponsToLoadDict = {}
                    for typeOfWeaponNeeded in weaponsNeededDict.keys():
                        available = 0
                        if weaponsOnPlanet.has_key(typeOfWeaponNeeded):
                            available = weaponsOnPlanet[typeOfWeaponNeeded]
                            if weaponsLoadedDict.has_key(typeOfWeaponNeeded):
                                available -= weaponsLoadedDict[typeOfWeaponNeeded]
                            assert available >= 0
                            #if there are any to load
                            if available > 0:
                                #mark weapons for loading
                                weaponsToLoadDict[typeOfWeaponNeeded] = min(available, weaponsNeededDict[typeOfWeaponNeeded])
                        #give build order if nesessary
                        if available < weaponsNeededDict[typeOfWeaponNeeded]:
                            #add it to the dictionary of weapons that need to be build
                            if weaponsToBuild.has_key(typeOfWeaponNeeded):
                                weaponsToBuild[typeOfWeaponNeeded] += weaponsNeededDict[typeOfWeaponNeeded] - available
                            else:
                                weaponsToBuild[typeOfWeaponNeeded] = weaponsNeededDict[typeOfWeaponNeeded] - available
                    #if there is anything to load
                    if weaponsToLoadDict != {}:
                        #actualy load the weapons... if the fleet is not in the process of being split
                        if not thingOnPlanet in ignoreFleets:
                            loadWeapons(thingOnPlanet, myPlanet, weaponsToLoadDict, weaponsLoadedDict)
                        #mark them as loaded
                        for type in weaponsToLoadDict.keys():
                            #make sure other ships don't try to load the same weapons
                            if weaponsLoadedDict.has_key(type):
                                weaponsLoadedDict[type] += weaponsToLoadDict[type]
                            else:
                                weaponsLoadedDict[type] = weaponsToLoadDict[type]
                    
            #build weapons/ships order
            if weaponsToBuild == {}:
                #no weaopns to build... build a ship
                #choose betwen an attack ship and a colonisation ship
                if random.random() < colonisationShipsPercent:
                    #build colonisation ship
                    #TODO experiment with max turns and other arguments
                    optimalBuildShip(myPlanet, colonisationShip)
                else:
                    #bild attack ship
                    #TODO experiment with max turns and other arguments
                    optimalBuildShip(myPlanet, ship)
            else:
                #build weapons of the required type
                optimalBuildWeapon(myPlanet, weaponsToBuild, explosivesList, maxExplosives)    

def speed(fleet):
    minSpeed = 1e10
    #check the speed of every ship design present
    for (something, design, numberOfUnits) in helper.shipsOfFleet(fleet):
        #get the ship speed
        #Note: there are 2 speed properties and looks like the wrong one is used in the server code
        #this might break if that gets fixed
        propertyId = helper.propertyByDescription("The number of units the weapon can move each turn")
        assert propertyId != None
        speed = helper.designPropertyValue(design, propertyId)
        #parse the speed string
        speed = float(speed.split(" ")[0])
        assert speed != None
        minSpeed = min(speed, minSpeed)
    return minSpeed
        

def distanceToObjectInTurns(fleet, object):
    fleetSpeed = speed(fleet) * 1e6 #convert from mega units
    distance = helper.distance(fleet, object)
    return int(math.ceil(distance / fleetSpeed))
    

def smartColonisationHeuristic(fleet, planet):
    #BTW smaller is better
    distance = distanceToObjectInTurns(fleet, planet)
    distanceToEnemyPlanet = int(math.ceil(helper.distance(planet, helper.nearestEnemyPlanet(planet)) / speed(fleet)))
    #if its closer its better, if its futher away from the enemy its better
    return distance - distanceToEnemyPlanet / 3
    
def smartSplitFleets(fleets=None):
    '''
    Splits fleets with more than one ship in half.
    '''
    if fleets == None:
        fleets = helper.myFleets()
    #list of fleets that will be split
    splitFleets = []
    for fleet in fleets:
        #total number of ships in the fleet
        numberOfShips = 0
        fleetContent = helper.shipsOfFleet(fleet)
        for (something, design, ships) in fleetContent:
            numberOfShips += ships
        if numberOfShips > 1:
            #half of the ships
            firstPartOfShips = numberOfShips / 2
            assert firstPartOfShips > 0
            tempShipNumber = 0
            #list of ships in the first half
            firstListOfShips = []
            for (something, design, ships) in fleetContent:
                temp = min(ships, firstPartOfShips - tempShipNumber)
                firstListOfShips.append((design, temp))
                tempShipNumber += temp
                assert tempShipNumber <= firstPartOfShips
                if tempShipNumber == firstPartOfShips:
                    break
            #add it to the list of fleets that will be split
            splitFleets.append(fleet)
            #give order (you only need one part defined)
            orderSplitFleet(fleet, firstListOfShips)
    return splitFleets
            

def smartColonisationCode(ignoreFleets=[]):
    #find ships able to colonise
    fleets = []
    for fleet in helper.myFleets():
        #add the fleet if it can colonise and if it isn't in the process of being split
        if canColonise(fleet) and not fleet in ignoreFleets:
            fleets.append(fleet)
            
    #dictionary for scores by planet
    scoreDict = {}
    #calculate heuristics
    for planet in helper.neutralPlanets():
        planetScores = []
        for fleet in fleets:
            score = smartColonisationHeuristic(fleet, planet)
            planetScores.append((score, fleet))
        #sort the scores in ascending order
        planetScores.sort()
        scoreDict[planet] = planetScores
    
    #dictonary of ships in use
    shipPlanetDict = {}
    
    planetsToCheck = helper.neutralPlanets()
    
    #while not all planets checked
    while planetsToCheck != []:
        planet = planetsToCheck[0]
        #select best ship
        for (score, ship) in scoreDict[planet]:
            #if ship already used
            if shipPlanetDict.has_key(ship):
                (oldScore, oldPlanet) = shipPlanetDict[ship]
                #if score of this planet is better (smaller is better)
                if score < oldScore:
                    #use this ship and make the other planet choose again
                    shipPlanetDict[ship] = (score, planet)
                    #make the other planet choose again
                    planetsToCheck.append(oldPlanet)
                    #done for this planet
                    break
                #choose next ship
            #first planet to want this ship
            else:
                shipPlanetDict[ship] = (score, planet)
                #done for this planet
                break
        #remove the planet from the list
        planetsToCheck.remove(planet)
    
    #give orders to all ships
    for ship in shipPlanetDict.keys():
        (score, planet) = shipPlanetDict[ship]
        #if the ship is already on the planet
        if helper.position(ship) == helper.position(planet):
            #colonise it
            orderColonise(ship)
        else:
            #move towards it
            moveToObject(ship, planet)

def smartAttackCode(ignoreFleets=[]):
    global invasionFleets
    #TODO don't forget the auto attack code
    #TODO send only a limited amount of ships to every planet
    
    invasionShips = 1
    invasionShipsRetreat = 0
    defenceShipsOnInvasion = 0
    minimalLoadToAttack = 0.50 #TODO make this dynamic
    minimalLoadToGuard = 0.20 #TODO maybe use this
    
    allMyFleets = helper.myFleets() 
    for fleet in invasionFleets[:]:
        #mark nonexistant fleets (probably destroyed) for removal
        if fleet not in allMyFleets:
            invasionFleets.remove(fleet)        

    #check how many fleets are available for the invasion
    potentialInvasionFleets = helper.myFleets()
    #remove all of the fleets that are already marked for the invasion 
    #and fleets that can no longer fight (no weapons)
    for fleet in invasionFleets[:]:
        potentialInvasionFleets.remove(fleet)
        #if it can no longer attack
        if weaponsOnObject(fleet) == {}:
            print helper.name(fleet), "is no longer invading"
            invasionFleets.remove(fleet)


    #remove all of the fleets that are not fully loaded with weapons and colonisation ships
    for fleet in potentialInvasionFleets[:]:
        #remove ship if it's a colonisation ship
        if canColonise(fleet):
            potentialInvasionFleets.remove(fleet)
            continue
        #remove fleets in process of being split
        if fleet in ignoreFleets:
            potentialInvasionFleets.remove(fleet)
            continue
        #remove ship if it doesn't have enough weapons
        maxWeaponsOnBoard = 0
        for (type, number) in maxWeaponsOfFleet(fleet).items():
            maxWeaponsOnBoard += number
        weaponsOnBoard = 0
        for (type, number) in weaponsOnObject(fleet).items():
            weaponsOnBoard += number
        assert maxWeaponsOnBoard != 0
        if weaponsOnBoard / maxWeaponsOnBoard < minimalLoadToAttack:
            potentialInvasionFleets.remove(fleet)
        
    guardOnPlanets = {}
    allMyPlanets = helper.myPlanets()
    
    #TODO remove guard fleets from potential invasion fleets
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
                if currentGuard < defenceShipsOnInvasion:
                    guardOnPlanets[parent] = currentGuard + 1
                    continue
            #mark it for invasion
            invasionFleets.append(fleet)
    
    #make the invasion fleets go back if there are only a few of them left
    if len(invasionFleets) < invasionShipsRetreat:
        print "to little attack ships. Retreat!"
        #the smart guard code takes care of returning to friendly planets
        invasionFleets = [] 

    #attack the enemy with ships marked for invasion
    for fleet in invasionFleets:
        print helper.name(fleet), "is invading (beware!)"
        #find a planet to attack
        #TODO make a weighted choise betwen say... 3 nearest planets (make it a bit less predictable)
        nearestPlanet = helper.nearestEnemyPlanet(helper.position(fleet))
        #move to that planet
        if nearestPlanet != None:
            print helper.name(fleet), "is attacking", helper.name(nearestPlanet) 
            planetPosition = helper.position(nearestPlanet)
            if helper.position(fleet) != planetPosition:
                orderMove(fleet, planetPosition)
        else:
            print helper.name(fleet), "has nothing to attack"


def smartGuardCode(ignoreFleets=[]):
    global invasionFleets
    #make a list of all attack ships not currently attacking
    freeFleets = helper.myFleets()
    #remove colonisation ships and ships marked for invasion and fleets in the process of beeing split
    for fleet in freeFleets[:]:
        if canColonise(fleet) or fleet in invasionFleets or fleet in ignoreFleets: 
            freeFleets.remove(fleet)
        
    for fleet in freeFleets:
        parent = helper.containedBy(fleet)
        #is the feet on a friendly planet?        
        if parent in helper.myPlanets():
            #make it stay here
            #TODO check for orders so we don't mess up loading orders
            orderNone(fleet)
        #other ships should go to a friendly palanet for suplies (if not already there)
        #TODO make a weighted choise where to return (distance, weapons needed by ships already there)
        else:
            nearestPlanet = helper.nearestMyPlanet(helper.position(fleet))
            assert nearestPlanet != None
            planetPosition = helper.position(nearestPlanet)
            orderMove(fleet, planetPosition)    

#dictionary of information about the enemy fleets designs (max speed which can tell us ship type)
enemyDesignMaxSpeed = {}
enemyDesignType = {}

#TODO this is currently not working since the velocity is always (0,0,0) thest it when this gets fixed
def smartScanEnemy():
    global enemyDesignMaxSpeed
    enemyFleets = helper.fleetsOwnedBy(helper.enemies())
    
    #update info for every enemy fleet
    for fleet in enemyFleets:
        #calculate velocity
        velocity = helper.velocity(fleet)
        velocitySize = math.sqrt(velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2)
        
        #get the designs
        ships = helper.shipsOfFleet(fleet)
        for (something, design, number) in ships:
            #change data if the speed is bigger or no previous data exists
            if enemyDesignMaxSpeed.has_key(design) and enemyDesignMaxSpeed[design] < velocitySize or not enemyDesignMaxSpeed.has_key(design):
                #update the max speed seen for this design
                enemyDesignMaxSpeed[design] = velocitySize
                #guess again what type of ship could this be
                designGuess = shipTypeGuess(velocitySize)
                enemyDesignType[design] = designGuess

def shipTypeGuess(maxSpeed):
    #TODO implement this
    pass

def smartAI():
    print "I am the smart one."
    
    #scan the enemy fleets
    smartScanEnemy()
    
    #split fleets that can be split
    splitFleets = smartSplitFleets()
    
    #give orders to planets
    smartPlanetCode(splitFleets)

    #give orders to colonisation ships
    smartColonisationCode(splitFleets)
    
    #give orders to attack ships marked for invasion 
    smartAttackCode(splitFleets)
        
    #give orders to attack ships not marked for invasion
    smartGuardCode(splitFleets)
    
    return

def AICode():
    #helper.printAboutMe()
    print "It's turn", helper.turnNumber()
    if helper.turnNumber() > 0:
        if helper.myPlanets() == []:
            print "Today was a good day to die."
            exit(0)
        if helper.planetsOwnedBy(helper.enemies()) == []:
            print "I won!"
            exit(0)
    
    #delete all messages so you don't get spammed
    helper.deleteAllMessages()
    #helper.printDesignsWithProperties()
    if helper.playerName(helper.whoami()) == "ai":
        pass
        #commandoAI()
        #rushAI()
        smartAI()
    else:
        pass
        waitingAI()
        #greedyAI()
        #rushAI()
        #bunkerAI()
        #commandoAI()
        #smartAI()
        
    #ship = []
    #ship.append([helper.componentByName("scout hull"), 1])
    #ship.append([helper.componentByName("alpha missile tube"), 10])
    #addShipDesign(ship)
    
    #designWeapon("alpha", "antimatter explosives", 1)

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
