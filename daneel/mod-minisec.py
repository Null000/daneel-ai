import logging
import math
import tp.client.cache
from tp.netlib.objects import OrderDescs

constraints = """order_move(int,tuple)
order_colonise(int)""".split('\n')

#rules = """""".split('\n')

rulesystem = None

def init(cache, rulesystem, connection):
    return

def startTurn(cache, store, delta=0):
    return

def endTurn(cache, rs, connection):
    global rulesystem
    #update rulesystem
    rulesystem = rs
    nullPythonAddonHack()
    orders = rulesystem.findConstraint("order_move(int,tuple)")
    for order in orders:
        objid = int(order.args[0])
        destination = [x for x in order.args[1]]
        print "Moving %s to %s" % (objid, destination)
        moveorder = findOrderDesc("Move")
        args = [0, objid, -1, moveorder.subtype, 0, [], [destination]]
        order = moveorder(*args)
        evt = cache.apply("orders", "create after", objid, cache.orders[objid].head, order)
        tp.client.cache.apply(connection, evt, cache)
    orders = rulesystem.findConstraint("order_colonise(int)")
    for order in orders:
        objid = order.args[0]
        orderd = findOrderDesc("Colonise")
        args = [0, objid, -1, orderd.subtype, 0, []]
        o = orderd(*args)
        evt = cache.apply("orders", "create after", objid, cache.orders[objid].head, o)
        if connection != None:
            tp.client.cache.apply(connection, evt, cache)

def findOrderDesc(name):
    name = name.lower()
    for d in OrderDescs().values():
        if d._name.lower() == name:
            return d

planetID = None
position = None
fleetID = None
fleetStartPosition = None

def nullPythonAddonHack():
    print "Now in python mode!"
    global rulesystem
    global position
    global planetID
    global fleetID
    
    printAboutMe()
    
    ids = allMyFleetIDs()
    if fleetID == None and len(ids)>0:
        fleetID = ids[0]
        fleetStartPosition = getPosition(fleetID)
        print "Fleet chosen:", fleetID, "(", getName(fleetID), ")"
    if fleetID != None and planetID == None:
        planetID = findNearestPlanetOwnedBy(fleetStartPosition,enemies())
        if planetID != None:
            position = getPosition(planetID)
            print "Nearest planet is", planetID, "(", getName(planetID), ") at", position
    
    if not position == None:
        if position == getPosition(fleetID):
            print fleetID , " IS HERE!!!!"
            #orderColonise(fleetID)
            print "It should freeze next turn."
        else:
            orderMove(fleetID, position)
            (x, y, z) = getPosition(fleetID)
            (x2, y2, z2) = position
            print "Only", math.sqrt((x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2), "to go"
    return

def findNearestNeutralPlanet(fleetPosition):
    return findNearestPlanetOwnedBy(fleetPosition, [-1])

def findNearestPlanetOwnedBy(fleetPosition,owners):
    global rulesystem
    (x,y,z) = fleetPosition
    planets = allPlanetsOwnedBy(owners)
    nearestPlanet = None
    minDistance = 1e300
    for planet in planets:
        (x2, y2, z2) = getPosition(planet)
        tempDistance = (x-x2)**2+(y-y2)**2+(z-z2)**2 #no need for sqrt
        #find nearest
        if tempDistance < minDistance:
            minDistance = tempDistance
            nearestPlanet = planet
    return nearestPlanet

def allMyFleetIDs():
    global rulesystem
    fleets = rulesystem.findConstraint("fleet(int)")
    list = []
    for x in fleets:
        if getOwner(x.args[0]) == whoami():
            list += [int(x.args[0])]
    return list

def allStarIDs():
    global rulesystem
    stars = rulesystem.findConstraint("star(int)")
    return [int(x.args[0]) for x in stars]

def allContainsIDs(id):
    global rulesystem
    things = rulesystem.findConstraint("contains(int,int)")
    list = []
    for x in things:
        if int(x.args[0]) == id:
            list += [x.args[1]] 
    return list

def getPosition(id):
    global rulesystem
    pos = rulesystem.findConstraint("pos(int,int,int,int)")
    for x in pos:
        if int(x.args[0]) == id:
            return [x.args[1], x.args[2], x.args[3]] 
    return None

def getName(id):
    global rulesystem
    name = rulesystem.findConstraint("name(int,str)")
    for x in name:
        if int(x.args[0]) == id:
            return x.args[1] 
    return None

def getOwner(id):
    global rulesystem
    things = rulesystem.findConstraint("owner(int,int)")
    for x in things:
        if int(x.args[0]) == id:
            return x.args[1] 
    return None

def whoami():
    global rulesystem
    return rulesystem.findConstraint("whoami(int)")[0].args[0]

def turnNumber():
    global rulesystem
    return rulesystem.findConstraint("turn(int)")[0].args[0]

def allPlayers():
    return [player.args[0] for player in rulesystem.findConstraint("player(int,unicode)")[1:]]

def playerName(id):
    players = rulesystem.findConstraint("player(int,unicode)")
    for player in players:
        if player.args[0] == id:
            return player.args[1]
    return None

def enemies():
    players = allPlayers()
    players.remove(whoami())
    return players

def orderMove(id, destination):
    '''
    Gives the move order to the object (fleet) with given id to move to the given destination [x,y,z] array.
    '''
    global rulesystem
    rulesystem.addConstraint("order_move(" + str(fleetID) + "," + str(position) + ")")
    return

def orderColonise(fleetID):
    '''
    Gives the colonise order to the object (fleet) to colonise the planet at its current location
    '''
    global rulesystem
    rulesystem.addConstraint("order_colonise(" + str(fleetID) + ")")
    return

def printAboutMe():
    print "I am", whoami(),". My name is",playerName(whoami())
    for x in enemies():
        print x ,"("+playerName(x)+") is my enemy"
    for x in allMyFleetIDs():
        print x ,"(" +getName(x) +") is my fleet"
    for x in allPlanetsOwnedBy([whoami()]):
        print x,"(" + getName(x) + ") is my planet"
    

def allPlanets():
    return [planet.args[0] for planet in rulesystem.findConstraint("planet(int)")]

def allPlanetsOwnedBy(owners):
	planets = allPlanets()
	planetList = []
	for planet in planets:
		if getOwner(planet) in owners:
			planetList += [planet]
	return planetList

def allPlanetsOfStar(starid):
	planets = allPlanets()
	stuffStarContains = allContainsIDs(starid)
	planetList = []
	for stuff in stuffStarContains:
		if stuff in planets:
			planetList += [stuff]
	return planetList

"""
Name: No Operation
Code: 0
Desc: Object does nothing for a given number of turns
Arguments: 
Arg name: wait    Arg type: ARG_TIME    Arg desc: The number of turns to wait 

Name: Move
Code: 1
Desc: Move to a given position absolute in space
Arguments: 
Arg name: pos    Arg type: ARG_ABS_COORD    Arg desc: The position in space to move to 

Name: Build Fleet
Code: 2
Desc: Build a fleet
Arguments: 
Arg name: ships    Arg type: ARG_LIST    Arg desc: The type of ship to build
Arg name: name    Arg type: ARG_STRING    Arg desc: The name of the new fleet being built 

Name: Colonise
Code: 3
Desc: Attempt to colonise a planet at the current location
No arguments
Name: Split Fleet
Code: 4
Desc: Split the fleet into two
Arguments: 
Arg name: ships    Arg type: ARG_LIST    Arg desc: The ships to be transferred 

Name: Merge Fleet
Code: 5
Desc: Merge this fleet into another one
No arguments
"""
