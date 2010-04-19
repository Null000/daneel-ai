import tp.client.cache
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
    
        
    last_time = getLastTurnTime(cache,delta)       
    for (k,v) in cache.players.items():
        store.addConstraint("player(%i,%s)" % (k,v.name))
        
    store.addConstraint("whoami(%i)" % cache.players[0].id)
    store.addConstraint("turn(%i)" % cache.objects[0].turn)
    for (k, v) in cache.objects.items():
#   this is in no way optimal but at least it holds all the data     
#        if delta and cache.objects.times[k] < last_time:
#            pass
#        else:
        store.addConstraint("subtype(%i,%i)" % (k, v.subtype))
        store.addConstraint("name(%i,%s)" % (k, v.name.replace(",", "'")))
        store.addConstraint("size(%i,%i)" % (k, v.size))
        store.addConstraint("pos(%i,%i,%i,%i)" % ((k,) + v.pos))
        store.addConstraint("vel(%i,%i,%i,%i)" % ((k,) + v.vel))
        for child in v.contains:
            store.addConstraint("contains(%i,%i)" % (k, child))
        if hasattr(v, "owner"):
            store.addConstraint("owner(%i,%i)" % (k, v.owner))
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
            argumentStringList += [ "Arg name: " + arg[0] + "\tArg type: " + tempOrder.ARG_NAMEMAP[arg[1]] + " (code:" + str(arg[1]) + ")\tArg desc: " + arg[2]]
        if argumentStringList == []:
            print "No arguments"
        else:
            print "Arguments:", "\n", "\n".join(argumentStringList), "\n"        
    print "END OF LIST OF POSSIBLE ORDERS\n"