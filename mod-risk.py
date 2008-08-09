import tp.client.cache
from tp.netlib.objects import OrderDescs

constraints = """adjacent(int,int)*
reinforcements(int)
armies(int,int)""".split('\n')

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
