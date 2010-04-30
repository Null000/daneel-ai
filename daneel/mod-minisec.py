import logging
import math
import tp.client.cache
from tp.netlib.objects import OrderDescs
import objectutils
from types import NoneType
import helper

constraints = """order_move(int,int,int,int)
order_colonise(int)
order_none(int)""".split('\n')

#rules = """""".split('\n')

rulesystem = None

def endTurn(cache, rs, connection):
    global rulesystem
    #update rulesystem
    rulesystem = rs
    nullPythonAddonHack()
    executeOrdersMove(cache, connection)
    executeOrdersColonise(cache, connection)
    executeOrdersNone(cache, connection)
            
def executeOrdersNone(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_none(int)")
    for orderConstraint in orders:
        objectId = int(orderConstraint.args[0])
        executeOrder(cache, connection, objectId, None)

def executeOrdersMove(cache, connection):
    global rulesystem
    orders = rulesystem.findConstraint("order_move(int,int,int,int)")
    for orderConstraint in orders:
        objectId = int(orderConstraint.args[0])
        destination = [x for x in orderConstraint.args[1:]]
        moveorder = findOrderDesc("Move")
        args = [0, objectId, -1, moveorder.subtype, 0, [], [destination]]
        order = moveorder(*args)
        executeOrder(cache, connection, objectId, order)
        
def executeOrdersColonise(cache, connection):
    orders = rulesystem.findConstraint("order_colonise(int)")
    for orderConstraint in orders:
        objectId = orderConstraint.args[0]
        orderd = findOrderDesc("Colonise")
        args = [0, objectId, -1, orderd.subtype, 0, []]
        order = orderd(*args)
        executeOrder(cache, connection, objectId, order)

def executeOrder(cache, connection, objectId, order):
    # get the queue for the object
    queueid = objectutils.getOrderQueueList(cache, objectId)[0][1]
    queue = cache.orders[queueid]
    node = queue.first
    
    #check if there is no existing order
    if order != None and isinstance(queue.first.CurrentOrder, NoneType):
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
    helper.rulesystem = rulesystem
    
    helper.printAboutMe()
    
    ids = helper.allMyFleets()
    if fleetID == None and len(ids) > 0:
        fleetID = ids[0]
        fleetStartPosition = helper.getPosition(fleetID)
        print "Fleet chosen:", fleetID, "(", helper.getName(fleetID), ")"
    if fleetID != None and planetID == None:
        planetID = helper.findNearestNeutralPlanet(fleetStartPosition)
        if planetID != None:
            position = helper.getPosition(planetID)
            print "Nearest planet is", planetID, "(", helper.getName(planetID), ") at", position
    
    if not position == None:
        if position == helper.getPosition(fleetID):
            print fleetID , " IS HERE!!!!"
            orderColonise(fleetID)
            print "It should freeze next turn."
        else:
            orderMove(fleetID, position)
            [x, y, z] = helper.getPosition(fleetID)
            [x2, y2, z2] = position
            print "Only", math.sqrt((x - x2) ** 2 + (y - y2) ** 2 + (z - z2) ** 2), "to go"
    for fleet in ids:
        orderNone(fleet)
    return



def orderNone(id):
    '''
    Removes orders from the object.
    '''
    global rulesystem
    rulesystem.addConstraint("order_none(" + str(id) + ")")
    return

def orderMove(id, destination):
    '''
    Gives the move order to the object (fleet) with given id to move to the given destination [x,y,z] array.
    '''
    global rulesystem
    assert len(destination) == 3
    
    rulesystem.addConstraint("order_move(" + str(fleetID) + "," + str(destination[0]) + "," + str(destination[1]) + "," + str(destination[2]) + ")")
    return

def orderColonise(fleetID):
    '''
    Gives the colonise order to the object (fleet) to colonise the planet at its current location
    '''
    global rulesystem
    rulesystem.addConstraint("order_colonise(" + str(fleetID) + ")")
    return

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
