import tp.client.cache
from tp.netlib.objects import OrderDescs

constraints = """subtype(int,int)
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
fleettype @ subtype(X,4) ==> fleet(X)""".split('\n')

def startTurn(cache,store):
    store.addConstraint("whoami(%i)" % cache.players[0].id)
    store.addConstraint("turn(%i)"%cache.objects[0].turn)
    for (k,v) in cache.objects.items():
        store.addConstraint("subtype(%i,%i)"%(k,v.subtype))
        store.addConstraint("name(%i,%s)"%(k,v.name))
        store.addConstraint("size(%i,%i)"%(k,v.size))
        store.addConstraint("pos(%i,%i,%i,%i)"%((k,) + v.pos))
        store.addConstraint("vel(%i,%i,%i,%i)"%((k,) + v.vel))
        for child in v.contains:
            store.addConstraint("contains(%i,%i)"%(k,child))
        if hasattr(v,"owner"):
            store.addConstraint("owner(%i,%i)"%(k,v.owner))
        if hasattr(v,"resources"):
            for res in v.resources:
                store.addConstraint("resources(%i,%i,%i,%i,%i)"%((k,)+res))
        if hasattr(v,"ships"):
            for (t,num) in v.ships:
                store.addConstraint("ships(%i,%i,%i)"%(k,t,num))
        if hasattr(v,"damage"):
            store.addConstraint("damage(%i,%i)"%(k,v.damage))
