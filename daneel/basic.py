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

argumentTypeNames = {0:"Absolute Space Coordinates",1:"Time",2:"Object",3:"Player",4:"Relative Space Coordinates",5:"Range",6:"List",7:"String",8:"Generic Reference",9:"Generic Reference List"}

def getLastTurnTime(cache,delta=0):
    if delta == 0:
        return -1
    else:
        latest_time = cache.objects.times[0]
        for (num,time) in cache.objects.times.iteritems():
            if time > latest_time:
                latest_time = time
            else:
                pass
        return latest_time

def startTurn(cache,store,delta=0):
    
        
    #last_time = getLastTurnTime(cache,delta)       
    for (k,v) in cache.players.items():
        store.addConstraint("player(%i,%s)" % (k,v.name))
        
    store.addConstraint("whoami(%i)" % cache.players[0].id)
    store.addConstraint("turn(%i)" % cache.objects[0].Informational[0][0])
    for (k, v) in cache.objects.items():
#   this is in no way optimal but at least it holds all the data     
#        if delta and cache.objects.times[k] < last_time:
#            pass
#        else:
        store.addConstraint("subtype(%i,%i)" % (k, v.subtype))
        store.addConstraint("name(%i,%s)" % (k, v.name.replace(",", "'")))
        store.addConstraint("size(%i,%i)" % (k, v.size))
        store.addConstraint("pos(%i,%i,%i,%i)" % ((k, v.Positional.Position.vector.x,v.Positional.Position.vector.y,v.Positional.Position.vector.z)))
        store.addConstraint("vel(%i,%i,%i,%i)" % ((k, v.Positional.Velocity.vector.x,v.Positional.Velocity.vector.y,v.Positional.Velocity.vector.z)))
        for child in v.contains:
            store.addConstraint("contains(%i,%i)" % (k, child))
        #its probably Ownership[0][1]
        if hasattr(v, "Ownership"):
            #TODO this is only a guess... (I have no clue what type means)
            store.addConstraint("owner(%i,%i)" % (k, v.Ownership.Owner.id))
        if hasattr(v, "resources"):
            for res in v.resources:
                store.addConstraint("resources(%i,%i,%i,%i,%i)" % ((k,) + res))
        if hasattr(v, "ships"):
            for (t, num) in v.ships:
                store.addConstraint("ships(%i,%i,%i)" % (k, t, num))
        if hasattr(v, "damage"):
            store.addConstraint("damage(%i,%i)" % (k, v.damage))
        if hasattr(v, "start"):
            store.addConstraint("start(%i,%i,%i,%i)" % ((k,) + v.start))
        if hasattr(v, "end"):
            store.addConstraint("end(%i,%i,%i,%i)" % ((k,) + v.end))

def init(cache, rulesystem, connection):
    printPossibleOrders(cache)
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
            argumentStringList += [ "Arg name: " + arg[0] + "\tArg type: " + argumentTypeNames[arg[1]] + " (code:" + str(arg[1]) + ")\tArg desc: " + arg[2]]
        if argumentStringList == []:
            print "No arguments"
        else:
            print "Arguments:", "\n", "\n".join(argumentStringList), "\n"
        print "CODE GENERATED:"
        #constraint generation 
        #the name of the order constraint (with _ instead of spaces)
        constraintString = "order_" + tempOrder._name.replace(" ", "_").lower() + "("
        #the arguments for the constraing (with , in between)
        constraintString += ",".join([arg[0].lower() for arg in argumentList]) + ")"
        #function call generation
        #the name of the order (in camel case)
        functionString = "order" + pascalCase(tempOrder._name) + "("
        #the arguments for the function (same as the constraint)
        functionString += ",".join([arg[0].lower() for arg in argumentList]) + "):"
        functionCommentStringList = argumentStringList 
        print constraintString
        print functionString
        print "\t'''"
        print "\t" + tempOrder.doc
        print "\t id is for the object the order is for"
        for comment in functionCommentStringList:
            print "\t", comment
        print "\t'''"
        print "global rulesystem"
        print "rulesystem.addConstraint(" + ",".join(["id"] + ["str(" + arg[0].lower() + ")" for arg in argumentList]) + ")"
        print "return"
        
    print "END OF LIST OF POSSIBLE ORDERS\n"
    

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
        return "list" #TODO find out how to make a list 
    if arg[1] == 7: #string
        return "string"
    return None

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

def argumentToStringForFunction(arg):
    #swich by argument type
    if arg[1] == 0: #Absolute Space Coordinates
        return "str(x)+\",\"+str(y)+\",\"+str(z)"
    if arg[1] == 1: #Time
        return "str(time)"
    if arg[1] == 2: #object
        return "str(objectid)"
    if arg[1] == 3: #Player
        return "str(playerid)"
    if arg[1] == 4: #Relative Space Coordinates
        return "objectid,x,y,z"
    if arg[1] == 5: #range
        return "value"
    if arg[1] == 6: #list
        return "list" #TODO find out how to make a list 
    if arg[1] == 7: #string
        return "string"
    return None
