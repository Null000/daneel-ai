from tp.netlib.objects import OrderDescs

constraints = """player(int,unicode)
subtype(int,int)
name(int,unicode)
size(int,int)
pos(int,int,int,int)
vel(int,int,int,int)
contains(int,int)
universe(int)
galaxy(int)
star(int)
planet(int)
fleet(int)
wormhole(int)
start(int,int,int,int)
end(int,int,int,int)
owner(int,int)
resources(int,int,int,int,int)
whoami(int)
turn(int)
ships(int,int,int)
damage(int,int)
cacheentered""".split('\n')

rules = """universetype @ subtype(X,0) ==> universe(X)
galaxytype @ subtype(X,1) ==> galaxy(X)
startype @ subtype(X,2) ==> star(X)
planettype @ subtype(X,3) ==> planet(X)
fleettype @ subtype(X,4) ==> fleet(X)
wormholetype @ subtype(X,5) ==> wormhole(X)""".split('\n')

argumentTypeNames = {0:"Absolute Space Coordinates", 1:"Time", 2:"Object", 3:"Player", 4:"Relative Space Coordinates", 5:"Range", 6:"List", 7:"String", 8:"Generic Reference", 9:"Generic Reference List"}


def init(cache, rulesystem, connection):
    printPossibleOrders(cache)
    printPossibleOrdersCode(cache)
    #force end of program
    exit(0)
    return
   

def printPossibleOrders(cache):
    ''' Prints possible orders and their arguments with descriptions.
     List of orders is send by the server.
     NOTE: argument types may be wrong (as I don't understand them yet) '''
     
    global argumentTypeNames
    print "LIST OF POSSIBLE ORDERS\n"
    orderList = OrderDescs()
    
    
    for i in range(len(orderList)):
        tempOrder = orderList[i]
        print "Name:", tempOrder._name
        print "Code:", tempOrder.subtype 
        print "Desc:", tempOrder.doc
        argumentStringList = []
        argumentList = tempOrder.packet.arguments
        for arg in argumentList:
            argumentStringList += [ "Arg name: " + arg[0] + "    Arg type: " + argumentTypeNames[arg[1]] + " (code:" + str(arg[1]) + ")    Arg desc: " + arg[2]]
        if argumentStringList == []:
            print "No arguments"
        else:
            print "Arguments:", "\n", "\n".join(argumentStringList), "\n"
        print
    print "END OF LIST OF POSSIBLE ORDERS\n"

def printPossibleOrdersCode(cache):
    ''' Prints code for possible orders and their arguments with descriptions.
     List of orders is send by the server.
     NOTE: argument types may be wrong (as I don't understand them yet) '''
     
    global argumentTypeNames
    print "LIST OF POSSIBLE ORDERS CODE\n"
    orderList = OrderDescs()
    
    #constraint generation
    import sys
    print """import logging
import tp.client.cache
from tp.netlib.objects import OrderDescs
import extra.objectutils
import helper

rulesystem = None"""
    print 
    sys.stdout.write("constraints = \"\"\"")
    for i in range(len(orderList)):
        tempOrder = orderList[i]
        argumentList = tempOrder.packet.arguments 
        #the name of the order constraint (with _ instead of spaces)
        constraintString = "order_" + tempOrder._name.replace(" ", "_").lower() + "("
        #the arguments for the constraint (with , in between)
        constraintString += ",".join(["int"] + [argumentToStringForConstraint(arg) for arg in argumentList]) + ")"
        print constraintString
    print "order_none(int)\"\"\".split(\'\\n\')"
    print
    print "def endTurn(cache2, rs, connection2):"
    print "    global rulesystem"
    print "    global cache"
    print "    global connection"
    print "    #update globals"
    print "    rulesystem = rs"
    print "    cache = cache2"
    print "    connection = connection2"
    print "    helper.rulesystem = rulesystem"
    print "    helper.cache = cache"
    print "    helper.connection = connection"
    print "    "
    print "    AICode()"
    for i in range(len(orderList)):
        tempOrder = orderList[i]
        print "    executeOrders" + pascalCase(tempOrder._name) + "(cache, connection)"
    
    
    print
    #order function call generation
    for i in range(len(orderList)):
        tempOrder = orderList[i]
        argumentList = tempOrder.packet.arguments
        argumentStringList = []
        for arg in argumentList:
            argumentStringList += [ "Arg name: " + arg[0] + "    Arg type: " + argumentTypeNames[arg[1]] + " (code:" + str(arg[1]) + ")    Arg desc: " + arg[2]]
        
        #the name of the order (in camel case)
        functionString = "order" + pascalCase(tempOrder._name) + "(id"
        #the arguments for the function (same as the constraint)
        for arg in argumentList:
            functionString += ", " + arg[0].lower()
        functionString += "):"
        functionCommentStringList = argumentStringList 
        print "def " + functionString
        print "    '''"
        print "    " + tempOrder.doc
        print "    id is for the object the order is for"
        for comment in functionCommentStringList:
            print "    ", comment
        print "    '''"
        print "    global rulesystem"    
        sys.stdout.write("    rulesystem.addConstraint(\"order_" + tempOrder._name.replace(" ", "_").lower() + "(\" + str(id)")
        for x in argumentList:
            sys.stdout.write(" + \", \"" + argumentToStringForFunction(x))
        print " + \")\")"
        print "    return"
        print
    
    #order removing function    
    print "def orderNone(id):"
    print "    \'\'\'"
    print "    Removes orders from the object."
    print "    \'\'\'"
    print "    global rulesystem"
    print "    rulesystem.addConstraint(\"order_none(\" + str(id) + \")\")"
    print "    return"
    print
    print "def executeOrdersNone(cache, connection):"
    print "    global rulesystem"
    print "    orders = rulesystem.findConstraint(\"order_none(int)\")"
    print "    for orderConstraint in orders:"
    print "        executeOrder(cache, connection, objectId, None)"
    print
    
    #order function execution generation
    for i in range(len(orderList)):
        tempOrder = orderList[i]
        argumentList = tempOrder.packet.arguments
        #the name of the order constraint (with _ instead of spaces)
        constraintString = "order_" + tempOrder._name.replace(" ", "_").lower() + "("
        #the arguments for the constraint (with , in between)
        constraintString += ",".join(["int"] + [argumentToStringForConstraint(arg) for arg in argumentList]) + ")"
        
        print "def executeOrders" + pascalCase(tempOrder._name) + "(cache, connection):"
        print "    global rulesystem"
        print "    orders = rulesystem.findConstraint(\"" + constraintString + "\")"
        print "    for orderConstraint in orders:"
        print "        args = orderConstraint.args"
        print "        objectId = int(args[0])"
        offset = 1
        for arg in argumentList:
            transformationString, offset = argumentTransformarion(arg, offset)
            print "        " + transformationString
        print "        ordertype = findOrderDesc(\"" + tempOrder._name + "\")"
        sys.stdout.write("        args = [0, objectId, -1, ordertype.subtype, 0, []")
        for arg in argumentList:
            sys.stdout.write(", " + camelCase(arg[0]))
        print "]"
        print "        order = ordertype(*args)"
        print "        executeOrder(cache, connection, objectId, order)"
        print
    
    #order execution code and some helper functions
    print """def executeOrder(cache, connection, objectId, order):
    # get the queue for the object
    queueid = extra.objectutils.getOrderQueueList(cache, objectId)[0][1]
    queue = cache.orders[queueid]
    node = queue.first
    
    #check if there is no existing order
    if order != None and queue.first.CurrentOrder is None:
        # make a new order   
        evt = cache.apply(\"orders\", \"create after\", queueid, node, order)
        tp.client.cache.apply(connection, evt, cache)
    #check if the existing order is the same as current order
    elif not checkIfOrdersSame(node.CurrentOrder, order):
        if order != None:
            #replace the current order with the new one
            evt = cache.apply(\"orders\", \"change\", queueid, node, order)
            tp.client.cache.apply(connection, evt, cache)
        #delete order
        else:
            nodes = [x for x in queue]
            evt = cache.apply(\"orders\", \"remove\", queueid, nodes=nodes)
            tp.client.cache.apply(connection, evt, cache)

def checkIfOrdersSame(order1, order2):
    #check if both are None
    if order1 is None and order2 is None:
        return True
    
    #check the type
    if type(order1) != type(order2):
        return False
    #check the name
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

def AICode():
    #TODO your AI code comes here
    return"""
    
    
    print "END OF LIST OF POSSIBLE ORDERS CODE\n"
    
def pascalCase(string):
    '''
    ConvertsTextToPascalCase
    '''
    return "".join([word[0].upper() + word[1:] for word in string.split(" ")])

def camelCase(string):
    '''
    convertsTextToCamelCase
    '''
    string = pascalCase(string)
    string = string[0].lower() + string[1:] 
    return string

def argumentToStringForConstraint(arg):
    #swich by argument type
    if arg[1] == 0: #Absolute Space Coordinates
        return "int,int,int"
    if arg[1] == 1: #Time
        return "int"
    if arg[1] == 2: #object
        return "int"
    if arg[1] == 3: #Player
        return "int"
    if arg[1] == 4: #Relative Space Coordinates
        return "int,int,int,int"
    if arg[1] == 5: #range
        return "int" #prbobably int
    if arg[1] == 6: #list
        return "list" 
    if arg[1] == 7: #string
        return "str"
    return None


def argumentToStringForFunction(arg):
    #swich by argument type
    if arg[1] == 0: #Absolute Space Coordinates
        return " + str(" + camelCase(arg[0]) + "[0]) + \",\" + str(" + camelCase(arg[0]) + "[1])""+\",\" + str(" + camelCase(arg[0]) + "[2])"
    if arg[1] == 1: #Time
        return " + str(" + camelCase(arg[0]) + ")"
    if arg[1] == 2: #object
        return " + str(" + camelCase(arg[0]) + ")"
    if arg[1] == 3: #Player
        return " + str(" + camelCase(arg[0]) + ")"
    if arg[1] == 4: #Relative Space Coordinates
        return " + str(" + camelCase(arg[0]) + "[0]) + \",\" + str(" + camelCase(arg[0]) + "[1])""+\",\" + str(" + camelCase(arg[0]) + "[2])""+\",\" + str(" + camelCase(arg[0]) + "[3])"
    if arg[1] == 5: #range
        return " + str(" + camelCase(arg[0]) + ")"
    if arg[1] == 6: #list
        return " + str(" + camelCase(arg[0]) + ")" 
    if arg[1] == 7: #string
        return " + " + camelCase(arg[0])
    return None

def argumentTransformarion(arg, offset):
    #swich by argument type
    if arg[1] == 0: #Absolute Space Coordinates
        return camelCase(arg[0]) + " = [[int(args[" + str(offset) + "]), int(args[" + str(offset + 1) + "]), int(args[" + str(offset + 2) + "])]]", offset + 3
    if arg[1] == 1: #Time
        return camelCase(arg[0]) + " = int(args[" + str(offset) + "])" , offset + 1
    if arg[1] == 2: #object
        return camelCase(arg[0]) + " = int(args[" + str(offset) + "])" , offset + 1
    if arg[1] == 3: #Player
        return camelCase(arg[0]) + " = int(args[" + str(offset) + "])" , offset + 1
    if arg[1] == 4: #Relative Space Coordinates
        return camelCase(arg[0]) + " = [[int(args[" + str(offset) + "]), int(args[" + str(offset + 1) + "]), int(args[" + str(offset + 2) + "]), int(args[" + str(offset + 3) + "])]]", offset + 4
    if arg[1] == 5: #range
        return camelCase(arg[0]) + " = int(args[" + str(offset) + "])" , offset + 1
    if arg[1] == 6: #list
        return camelCase(arg[0]) + " = [[], args[" + str(offset) + "]]" , offset + 1
    if arg[1] == 7: #string
        return camelCase(arg[0]) + " = [len(args[" + str(offset) + "]), args[" + str(offset) + "]]", offset + 1
    return None, None
