import tp.client.cache
from tp.netlib.objects import OrderDescs

constraints = """adjacent(int,int)*
reinforcements(int)
armies(int,int)
order_move(int,int,int)
order_reinforce(int,int)
order_colonise(int,int)""".split('\n')

rules = """adjacentset @ adjacent(A,B) \ adjacent(A,B) <=> pass
addarmies @ resources(P,1,N,_) ==> armies(P,N)""".split('\n')

def init(cache,rulesystem,connection):
    planets = {}
    #two loops because we want to make sure all planet positions are stored first
    for obj in cache.objects.itervalues():
        if obj.subtype == 3:
            planets[obj.pos] = obj.id
    for obj in cache.objects.itervalues():
        if obj.subtype == 5:
            rulesystem.addConstraint("adjacent(%i,%i)"%(planets[obj.start],planets[obj.end]))
            rulesystem.addConstraint("adjacent(%i,%i)"%(planets[obj.end],planets[obj.start]))


def startTurn(cache,store):
    me = cache.players[0].id
    for (k,v) in cache.objects.items():
        if v.subtype == 3 and v.owner == me:
            store.addConstraint("reinforcements(%i)"%v.resources[0][2])
            break

def endTurn(cache,rulesystem,connection):
    orders = rulesystem.findConstraint("order_move(int,int,int)")
    for order in orders:
        start = int(order.args[0])
        destination = int(order.args[1])
        amount = int(order.args[2])
        print "Moving %s troops from %s to %s" % (amount,start,destination)
        moveorder = findOrderDesc("Move")
        args = [0, start, -1, moveorder.subtype, 0, [], ([], [(destination, amount)])]
        order = moveorder(*args)
        evt = cache.apply("orders","create after",start,cache.orders[start].head,order)
        tp.client.cache.apply(connection,evt,cache)
    orders = rulesystem.findConstraint("order_reinforce(int,int)")
    for order in orders:
        objid = order.args[0]
        amount = order.args[1]
        print "Reinforcing %s with %s troops" % (objid,amount)
        orderd = findOrderDesc("Reinforce")
        args = [0, objid, -1, orderd.subtype, 0, [], amount, 0]
        order = orderd(*args)
        evt = cache.apply("orders","create after",objid,cache.orders[objid].head,order)
        tp.client.cache.apply(connection,evt,cache)
    #TODO: Colonization doesn't seem to work yet?
    #orders = rulesystem.findConstraint("order_colonise(int,int)")
    orders = []
    for order in orders:
        objid = order.args[0]
        amount = order.args[1]
        print "Colonizing %s with %s troops" % (objid,amount)
        order = findOrderDesc("Colonize")
        args = [0, objid, -1, order.subtype, 0, [], ([], [(amount, 0)])]
        o = order(*args)
        evt = cache.apply("orders","create after",objid,cache.orders[objid].head,o)
        tp.client.cache.apply(connection,evt,cache)

def findOrderDesc(name):
    name = name.lower()
    for d in OrderDescs().values():
        if d._name.lower() == name:
            return d
