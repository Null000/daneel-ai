'''
Created on 30.4.2010

@author: Damjan 'Null' Kosir
'''
from tp.netlib.objects import Design
import tp.client.cache

rulesystem = None
cache = None
conection = None

def findNearestMyFleet(position,ignore=[]):
    return findNearestFleetOwnedBy(position, whoami(), ignore)

def findNearestFleetOwnedBy(targetPosition,owners,ignore=[]):
    if type(owners) == int:
        owners = [owners] 
    (x, y, z) = targetPosition
    fleets = allFleetsOwnedBy(owners)
    nearestFleet = None
    minDistance = 1e300
    for fleet in fleets:
        if not fleet in ignore:
            (x2, y2, z2) = position(fleet)
            tempDistance = (x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2 #no need for sqrt
            #find nearest
            if tempDistance < minDistance:
                minDistance = tempDistance
                nearestFleet = fleet
    return nearestFleet

def findNearestPlanetOwnedBy(fleetPosition, owners, ignore=[]):
    if type(owners) == int:
        owners = [owners] 
    (x, y, z) = fleetPosition
    planets = allPlanetsOwnedBy(owners)
    nearestPlanet = None
    minDistance = 1e300
    for planet in planets:
        if not planet in ignore:
            (x2, y2, z2) = position(planet)
            tempDistance = (x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2 #no need for sqrt
            #find nearest
            if tempDistance < minDistance:
                minDistance = tempDistance
                nearestPlanet = planet
    return nearestPlanet

def findNearestNeutralPlanet(fleetPosition, ignore=[]):
    (x, y, z) = fleetPosition
    planets = allNeutralPlanets()
    nearestPlanet = None
    minDistance = 1e300
    for planet in planets:
        if not planet in ignore:
            (x2, y2, z2) = position(planet)
            tempDistance = (x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2 #no need for sqrt
            #find nearest
            if tempDistance < minDistance:
                minDistance = tempDistance
                nearestPlanet = planet
    return nearestPlanet

def allMyFleets():
    global rulesystem
    fleets = rulesystem.findConstraint("fleet(int)")
    list = []
    for x in fleets:
        if getOwner(x.args[0]) == whoami():
            list += [int(x.args[0])]
    return list

def allFleetsOwnedBy(owners):
    global rulesystem
    fleets = rulesystem.findConstraint("fleet(int)")
    list = []
    for x in fleets:
        if getOwner(x.args[0]) in owners:
            list += [int(x.args[0])]
    return list

def allStars():
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

def position(id):
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
    global rulesystem
    return [player.args[0] for player in rulesystem.findConstraint("player(int,unicode)")[1:]]

def allPlayersWithoutGuest():
    players = allPlayers()
    #remove guest (a player who is always present and has no objects)
    for player in players:
        if getName(player) == "guest":
            players.remove(player)
            break
    return players

def playerName(id):
    global rulesystem
    players = rulesystem.findConstraint("player(int,unicode)")
    for player in players:
        if player.args[0] == id:
            return player.args[1]
    return None

def enemies():
    players = allPlayersWithoutGuest()
    players.remove(whoami())
    return players

def printAboutMe():
    print "I am", whoami(), ". My name is", playerName(whoami())
    for x in enemies():
        print x , "(" + playerName(x) + ") is my enemy"
    for x in allMyFleets():
        print x , "(" + getName(x) + ") is my fleet"
    for x in allPlanetsOwnedBy([whoami()]):
        print x, "(" + getName(x) + ") is my planet"
    

def allPlanets():
    global rulesystem
    return [planet.args[0] for planet in rulesystem.findConstraint("planet(int)")]

def allMyPlanets():
    return allPlanetsOwnedBy(whoami())

def allPlanetsOwnedBy(owners):
    if isinstance(owners, int):
        owners = [owners]
    planets = allPlanets()
    planetList = []
    for planet in planets:
        if getOwner(planet) in owners:
            planetList += [planet]
    return planetList
    
def allNeutralPlanets():
    planets = allPlanets()
    planetList = []
    for planet in planets:
        if not getOwner(planet) in allPlayers():
            planetList += [planet]
    return planetList

def addDesign(name,description,categories,componentList):
    global cache
    global connection
    if type(categories) == int:
        categories = [categories]
    design = Design(-1, -1, 0, categories, name, description,-1,-1, componentList, "", [])
    evt = cache.CacheDirtyEvent("designs", "create", -1, design)
    tp.client.cache.apply(connection, evt, cache)

def findCategoryByName(name):
    global cache
    for categoryNumber in cache.categories:
        if cache.categories[categoryNumber].name.lower() == name.lower():
            return cache.categories[categoryNumber].id
    return None

def findComponentByName(name):
    global cache
    for componentNumber in cache.components:
        if cache.components[componentNumber].name.lower() == name.lower():
            return cache.components[componentNumber].id
    return None

def findDesignByName(name):
    global cache
    for designNumber in cache.designs:
        if cache.designs[designNumber].name.lower() == name.lower() and cache.designs[designNumber].owner == whoami():
            return cache.designs[designNumber].id
    return None