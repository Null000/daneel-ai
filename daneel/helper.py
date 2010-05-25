'''
Created on 30.4.2010

@author: Damjan 'Null' Kosir
'''
from tp.netlib.objects import Design
import tp.client.cache

rulesystem = None
cache = None
conection = None

def nearestMyFleet(position, ignore=[]):
    return nearestFleetOwnedBy(position, whoami(), ignore)

def nearestFleetOwnedBy(targetPosition, owners, ignore=[]):
    if type(owners) == int:
        owners = [owners] 
    (x, y, z) = targetPosition
    fleets = fleetsOwnedBy(owners)
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

def cearestPlanetOwnedBy(fleetPosition, owners, ignore=[]):
    if type(owners) == int:
        owners = [owners] 
    (x, y, z) = fleetPosition
    planets = planetsOwnedBy(owners)
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

def nearestNeutralPlanet(fleetPosition, ignore=[]):
    (x, y, z) = fleetPosition
    planets = neutralPlanets()
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

def myFleets():
    global rulesystem
    fleets = rulesystem.findConstraint("fleet(int)")
    list = []
    for x in fleets:
        if owner(x.args[0]) == whoami():
            list += [int(x.args[0])]
    return list

def fleetsOwnedBy(owners):
    global rulesystem
    fleets = rulesystem.findConstraint("fleet(int)")
    list = []
    for x in fleets:
        if owner(x.args[0]) in owners:
            list += [int(x.args[0])]
    return list

def stars():
    global rulesystem
    stars = rulesystem.findConstraint("star(int)")
    return [int(x.args[0]) for x in stars]

def contains(id):
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

def name(id):
    global rulesystem
    name = rulesystem.findConstraint("name(int,str)")
    for x in name:
        if int(x.args[0]) == id:
            return x.args[1] 
    return None

def owner(id):
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

def players():
    global rulesystem
    return [player.args[0] for player in rulesystem.findConstraint("player(int,unicode)")[1:]]

def playersWithoutGuest():
    allPlayers = players()
    #remove guest (a player who is always present and has no objects)
    for player in allPlayers:
        if name(player) == "guest":
            allPlayers.remove(player)
            break
    return allPlayers

def playerName(id):
    global rulesystem
    players = rulesystem.findConstraint("player(int,unicode)")
    for player in players:
        if player.args[0] == id:
            return player.args[1]
    return None

def enemies():
    players = playersWithoutGuest()
    players.remove(whoami())
    return players

def printAboutMe():
    print "I am", whoami(), ". My name is", playerName(whoami())
    for x in enemies():
        print x , "(" + playerName(x) + ") is my enemy"
    for x in myFleets():
        print x , "(" + name(x) + ") is my fleet"
    for x in planetsOwnedBy([whoami()]):
        print x, "(" + name(x) + ") is my planet"

def printDesigns():
    global cache
    for design in cache.designs.values():
        print design.id, design.name     

def printDesign(design):
    global cache
    if type(design) != int:
        design = designByName(design)
    print cache.designs[design].name
    for (id, value) in cache.designs[design].properties:
        print cache.properties[id].name, ":", value

def planets():
    global rulesystem
    return [planet.args[0] for planet in rulesystem.findConstraint("planet(int)")]

def myPlanets():
    return planetsOwnedBy(whoami())

def planetsOwnedBy(owners):
    if isinstance(owners, int):
        owners = [owners]
    allPlanets = planets()
    planetList = []
    for planet in allPlanets:
        if owner(planet) in owners:
            planetList += [planet]
    return planetList
    
def neutralPlanets():
    allPlanets = planets()
    planetList = []
    for planet in allPlanets:
        if not owner(planet) in players():
            planetList += [planet]
    return planetList

def addDesign(name, description, categories, componentList, replaceOnDuplicate=False):
    current = designByName(name)
    if current != None and not replaceOnDuplicate:
        #design already exists and we don't want to replace it
        return
    global cache
    global connection
    if type(categories) == int:
        categories = [categories]
    #prepare design
    design = Design(-1, -1, 0, categories, name, description, 0, whoami(), componentList, "", [])
    if current == None:
        #create a new design
        evt = cache.CacheDirtyEvent("designs", "create", -1, design)
    else:
        #replace the existing design
        evt = cache.CacheDirtyEvent("designs", "create", current, design)
        
    #apply changes
    tp.client.cache.apply(connection, evt, cache)
    
    #update the cache by force or the new design won't be available
    #TODO there must be a more elegant way to do this (this way is a bit scary)
    
    #TODO Null: commented out for debugging purposes
    
#    if current == None:
#        #find the new design id
#        oldDesignIDs = [tempDesign.id for tempDesign in cache.designs.values()]
#        oldDesignIDs.remove(-1)
#        allDesignIDs = [x[0] for x in connection.get_design_ids(iter=True)]
#        for x in oldDesignIDs:
#            allDesignIDs.remove(x)
#        #there should be only one left
#        assert len(allDesignIDs) == 1
#        
#        newDesign = connection.get_designs(allDesignIDs[0])[0]
#            
#        #find the design to be replaced
#        for designNumber in cache.designs:
#            if cache.designs[designNumber].id == -1:
#                #replace the design
#                cache.designs[designNumber] = newDesign
#                break
     
    
def nop(group=None, state=None, message=None, todownload=None, amount=None):
    print group, state, message
    return

def categoryByName(name):
    global cache
    #loop through all categories
    for category in cache.categories.values():
        if category.name.lower() == name.lower():
            #return on match
            return category.id
    return None

def componentByName(name):
    global cache
    #loop through all components
    for component in cache.components.values():
        if component.name.lower() == name.lower():
            #return on match
            return component.id
    return None

def designByName(name):
    global cache
    #loop through all designs
    for design in cache.designs.values():
        if design.name.lower() == name.lower() and design.owner == whoami():
            #return on match
            return design.id
    return None

def generateDesignName(components):
    '''
    Generate an unique name based on components.
    '''
    #sort the components by id
    components.sort()
    name = ""
    for component in components:
        #find the component with the given id
        for tempComponent in cache.components.values():
            if tempComponent.id == component[0]:
                #add component information to name
                name += str(component[1]) + "x " + tempComponent.name + " "
                break
    return name.strip()
    
