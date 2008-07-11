from functools import partial
from collections import defaultdict

from logilab.constraint import fd, Solver, Repository
from logilab.constraint.fd import ConsistencyFailure

import re

class RuleSystem:
    def __init__(self,constraints=[],rules=[],functions={}):
        self.constraints = constraints
        self.store = ConstraintStore()
        self.activestore = ConstraintStore()
        self.parser = RuleParser(self,constraints)
        self.rules = [self.parser.parseRule(r) for r in rules]
        self.protocontext = self.createPrototypeContext(functions)

    def addConstraint(self,constraint):
        parsedcon = self.parser.parseConstraint(constraint)
        self.store.add(parsedcon)
        self.activestore.add(parsedcon)
        while len(self.activestore) > 0:
            activecon = self.activestore.pop()
            self.matchActive(activecon)

    def removeConstraint(self,constraint):
        try:
            self.activestore.remove(constraint)
        except KeyError:
            pass
        self.store.remove(constraint)

    def matchActive(self,constraint):
        for r in self.rules:
            if r.matchActive(constraint):
                break

    def clearStore(self):
        #TODO: long-term storage
        self.store.clear()
        self.activestore.clear()

    def createContext(self):
        return self.protocontext.copy()

    def createPrototypeContext(self,functions):
        context = functions.copy()
        #we insert a function for each constraint. When this function is called,
        #a new instance of the constraint gets inserted in the constraint store
        #with arguments as passed with the function
        def createCons(name,*args):
            cons = BoundConstraint(name,list(args))
            self.addConstraint(cons)
        for c in self.constraints:
            context[c] = partial(createCons,c)
        return context

    def findConstraint(self,con):
        """Given a free constraint, returns a list of constraints in the store that match it"""
        return list(self.store.elems[(con.functor,con.arity)])

    def findConstraints(self,cons,excluded=set()):
        """Given a list of free constraint, and a set of constraints to exclude,
        returns a generator for constraints in the store that match it, with no duplicates
        and no entries from the excluded set"""
        return self.store.findterms(cons,excluded)

class RuleParser:
    freecon = re.compile(r"^(\w*)/(\d*)$")
    boundcon = re.compile(r"^(\w+)(\( *(.+?, *)*.+ *\))?$")
    #these regexps might be a bit too loose, then again, we're trying to match a CFL.
    #probably, it can be compiled in one RE too.
    simplrule = re.compile(r"^((?P<name>\w+) @ )?(?P<removedhead>[^\\]+)<=>((?P<guard>.+)\|)?(?P<body>.+)$")
    simparule = re.compile(r"^((?P<name>\w+) @ )?(?P<kepthead>.+)\\(?P<removedhead>.+)<=>((?P<guard>.+)\|)?(?P<body>.+)$")
    proprule = re.compile(r"^((?P<name>\w+) @ )?(?P<kepthead>.+)==>((?P<guard>.+)\|)?(?P<body>.+)$")

    def __init__(self,rulesystem,constraints=[]):
        self.constraints = constraints
        self.rulesystem = rulesystem

    def parseRule(self,rule):
        if isinstance(rule,Rule):
            return rule
        m = RuleParser.simplrule.match(rule)
        if m is not None:
            return Rule(self.rulesystem,**m.groupdict())
        m = RuleParser.simparule.match(rule)
        if m is not None:
            return Rule(self.rulesystem,**m.groupdict())
        m = RuleParser.proprule.match(rule)
        if m is not None:
            return Rule(self.rulesystem,**m.groupdict())

    def parseHead(self,head):
        if isinstance(head,list):
            return head
        splitted = head.split(" and ")
        return [self.parseConstraint(x.strip()) for x in splitted]

    def parseGuard(self,guard):
        if isinstance(guard,list):
            return guard
        #TODO: parse these into logilab constraints
        return [guard.strip()]

    def parseBody(self,body):
        return body.strip()

    def parseConstraint(self,cons):
        if isinstance(cons,Constraint):
            return cons
        m = RuleParser.freecon.match(cons)
        if m is not None:
            return FreeConstraint(m.group(1),int(m.group(2)))
        m = RuleParser.boundcon.match(cons)
        if(m is not None):
            functor = m.group(1)
            args = []
            if(m.group(2) is not None):
                args = m.group(2)[1:-1].split(",")
            return BoundConstraint(functor,args)

class Rule:
    """A rule consist of:
    * name, string, preferable unique although nothing requires this
    * kepthead, list of free constraints
    * removedhead, list of free constraints
    * guard, List of Python code evaluating to True or False represented as string
    * body, a mix of constraints, PythonTerms and unifications, represented as string"""

    uniquecount = 0

    def __init__(self,rulesystem,name=None,kepthead=[],removedhead=[],guard=[],body=""):
        Rule.uniquecount = Rule.uniquecount + 1
        if name is None:
            name = "rule_%i" % Rule.uniquecount

        self.rulesystem = rulesystem
        parser = rulesystem.parser
        self.name = name
        self.kepthead = parser.parseHead(kepthead)
        self.removedhead = parser.parseHead(removedhead)
        self.guard = parser.parseGuard(guard)
        self.body = parser.parseBody(body)

    def matchActive(self,con):
        positions = self.canAcceptAt(con)
        if(positions == []):
            return False
        allConstraints = self.kepthead + self.removedhead
        for pos in positions:
            var1 = ["_var_%i" % i for i in range(len(allConstraints))]
            var2 = ["_var_%i_%i" % (i,j) for i in range(len(allConstraints)) for j in range(allConstraints[i].arity)]

            domains = {}
            #TODO: empty domain, return false?
            for i in range(len(allConstraints)):
                c = "_var_%i" % i
                vals = self.rulesystem.findConstraint(allConstraints[i])
                domains[c] = fd.FiniteDomain(vals)
                for j in range(allConstraints[i].arity):
                    c2 = "%s_%i" % (c,j)
                    vals2 = [x.args[j] for x in vals]
                    domains[c2] = fd.FiniteDomain(vals2)

            constraints = []
            if(len(var1) > 1):
                constraints.append(fd.AllDistinct(var1))
            constraints.append(fd.Equals("_var_%i" % pos,con))
            for i in range(len(allConstraints)):
                for j in range(allConstraints[i].arity):
                    c = "_var_%i" % i
                    a = "_var_%i_%i" % (i,j)
                    constraints.append(fd.make_expression((c,a),"%s.args[%i] == %s"%(c,j,a)))
            constraints.extend(self.guard)

            try:
                r = Repository(var1+var2, domains, constraints)
                solution = Solver().solve_one(r, False)
            except ConsistencyFailure:
                continue
            if solution is None:
                continue
            p = [solution["_var_%i"%i] for i in range(len(allConstraints))]
            assert len(p) == len(self.kepthead) + len(self.removedhead)
            context = self.rulesystem.createContext()

            #bind vars
            for i in range(len(p)):
                tempcon = p[i]
                for j in range(tempcon.arity):
                    var = "_var_%i_%i" % (i,j)
                    context[var] = tempcon.args[j]
            #print "Rule fired: %s" % self.name
            if self.removedhead == []:
                removedConstraints = []
            else:
                removedConstraints = p[-len(self.removedhead):]
            for c in removedConstraints:
                self.rulesystem.removeConstraint(c)
            exec(self.body,context)
            return True

    def canAcceptAt(self,cons):
        head = self.kepthead + self.removedhead
        return [i for i in range(len(head)) if head[i].unifiesWith(cons)]

class ConstraintStore:
    """A CHR constraint store is used to hold a collection of facts in the form of predicates."""
    def __init__(self):
        self.elems = defaultdict(set)

    def add(self,elem):
        assert isinstance(elem,Constraint), "%s is not a Constraint" % (elem, )
        func = elem.functor
        ar = elem.arity
        if(self.elems.has_key((func,ar))):
            self.elems[(func,ar)].add(elem)
        else:
            self.elems[(func,ar)] = set([elem])

    def remove(self,elem):
        assert isinstance(elem,Constraint), "%s is not a Constraint" % (elem, )
        func = elem.functor
        ar = elem.arity
        self.elems[(func,ar)].remove(elem)

    def __len__(self):
        return sum(map(len,self.elems.values()))

    def __str__(self):
        return str(self.elems.values())

    def findterms(self,terms,previousterms=set()):
        """Matches a list of strings against the store. Generates the predicate lists that match.
        Variables will not be bound yet as these are tentative choices.
        Note that all arguments should be unbounded and different (head-normal form of rules).
        For example: match(["pred(X)","pred2(Y,Z)"]) might return [pred(5),pred2(5,7)] and [pred(""),pred2("x",3)]"""
        if terms == []:
            yield []
            return
        terms.reverse()
        matches = self.findmatches(terms,previousterms)
        while True:
            yield matches.next()

    def findmatches(self,needles,previousterms):
        newneedles = list(needles)
        constr = newneedles.pop()
        if(isinstance(constr,Constraint)):
            possiblematches = self.elems[constr.functor,constr.arity].difference(previousterms)
            if newneedles == []:
                for x in possiblematches:
                    yield [x]
                return
            finallist = []
            for x in possiblematches:
                usedterms = set(previousterms)
                usedterms.add(x)
                for y in self.findmatches(newneedles,usedterms):
                    yield [x] + y
        else:
            assert False #TODO: PythonTerm?

    def pop(self):
        v = self.elems.values()
        for s in v:
            if len(s) > 0:
                return s.pop()

    def clear(self):
        self.elems.clear()

class Constraint:
    def __init__(self,name,arity):
        self.functor = name
        self.arity = arity

class FreeConstraint(Constraint):
    """A constraint with all arguments unbounded (different variables)."""
    def __init__(self,name,arity):
        Constraint.__init__(self,name,arity)

    def __str__(self):
        return "%s/%i" % (self.functor,self.arity)

    def __repr__(self):
        return "<FreeConstraint: %s at 0x%x>" % (str(self),id(self))

    def bind(self,args):
        assert len(args) == self.arity
        return BoundConstraint(self.name,args)

    def unifiesWith(self,other):
        return self.functor == other.functor and self.arity == other.arity

class BoundConstraint(Constraint):
    """A constraint with all arguments known Python expressions."""
    def __init__(self,name,args):
        Constraint.__init__(self,name,len(args))
        self.args = args

    def __str__(self):
        if(self.args == []):
            return self.functor
        else:
            return "%s(%s)" % (self.functor, ','.join([str(x) for x in self.args]))

    def __repr__(self):
        return "<BoundConstraint: %s at 0x%x>" % (str(self),id(self))

    def unifiesWith(self,other):
        if(hasattr(other,"args")):
            return self.functor == other.functor and self.arity == other.arity and self.args == other.args
        else:
            return other.unifiesWith(self)
