import tp.client.cache
from tp.netlib.objects import OrderDescs

constraints = """adjacent(int,int)*
ownedplanets(tuple)*
reinforcements(int)""".split('\n')

rules = """adjacentset @ adjacent(A,B) \ adjacent(A,B) <=> pass
whoami(Me) and owner(P,Me) and planet(P) \ ownedplanets(T) <=> P not in T | findajacencies(P); ownedplanets(T + (P,))
adjacent(A,B) ==> print 'Adjacent planets: %s and %s' % (A,B)""".split('\n')

functions = """
import tp.client.cache
from tp.netlib.objects import OrderDescs

def findajacencies(planet):
    moveorder = findOrderDesc("Move")
    args = [0, planet, -1, moveorder.subtype, 0, [], ([], [])]
    order = moveorder(*args)
    evt = cache.apply("orders","create after",planet,cache.orders[planet].head,order)
    tp.client.cache.apply(connection,evt,cache)
    for (i,name,something) in cache.orders[planet].first.CurrentOrder.Planet[0]:
        rulesystem.addConstraint('adjacent(%s,%s)'%(i,planet))
        rulesystem.addConstraint('adjacent(%s,%s)'%(planet,i))

def findOrderDesc(name):
    name = name.lower()
    for d in OrderDescs().values():
        if d._name.lower() == name:
            return d
"""

def init(cachelocal,rulesystem,connectionlocal):
    rulesystem.addConstraint("ownedplanets(())")

def startTurn(cache,store):
    me = cache.players[0].id
    for (k,v) in cache.objects.items():
        if v.subtype == 3 and v.owner == me:
            store.addConstraint("reinforcements(%i)"%v.resources[0][2])
            break
