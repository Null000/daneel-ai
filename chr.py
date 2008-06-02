class Context(dict):
    def checkTerm(f):
        """Allows you to both pass a string representing a variable or a LogicVar object as arguments"""
        def checked(self,var):
            if(not isinstance(var,Term)):
                var = self[var]
            return f(self,var)
        return checked

    def __missing__(self,key):
        v = LogicVar(key)
        self[key] = v
        return v

    @checkTerm
    def variable(self,var):
        return isinstance(self.canonical(var),LogicVar)
    
    @checkTerm
    def canonical(self,var):
        return var.canonical()

    def unify(self,first,second):
        """Uses the Martelli-Montanari algorithm to compute the most general unification"""
        mgu = [(first,second)]
        stop = False
        while(not stop and len(mgu) > 0):
            s,t = mgu.pop()
            if(self.variable(t) and not self.variable(s)):
                mgu.append((t,s))
            elif(s.canonical() == t.canonical()):
                pass
            elif(self.variable(s) and not self.variable(t) and t.contains(s)):
                stop = True
            elif(self.variable(s)):
                s.link = t
            elif(isinstance(s,PythonTerm) and isinstance(t,PythonTerm)):
                stop = (s.term == t.term)
            elif(isinstance(s,Constraint) and isinstance(t,Constraint)):
                if(s.functor != s.functor or s.arity() != t.arity()):
                    stop = True
                else:
                    mgu.extend(zip(s.args,t.args))
        return not stop

class Term:
    """A term in a CHR context. Can be a variable, a constraint or a wrapped Python primitive."""
    pass

class LogicVar(Term):
    """A logical variable in a CHR context. Can optionally be linked to
    another logical variable to make this an alias of the other.
    To prevent loops, the last link in a chain of aliases should always
    be used, this is the canonical form of the variable"""
    def __init__(self,name,alias=None):
        self.name = name
        self.link = alias            

    def __str__(self):
        return (self.name if self.link is None else str(self.canonical()))

    def canonical(self):
        var = self
        while(isinstance(var,LogicVar) and var.link is not None):
            var = var.link
        return var
        
    def contains(self, other):
        return self.canonical() == other.canonical()

class Constraint(Term):
    def __init__(self,name,*args):
        self.functor = name
        self.args = [(x if isinstance(x,Term) else PythonTerm(x)) for x in args]

    def arity(self):
        return len(self.args)

    def canonical(self):
        args = [self.functor]
        args += [x.canonical() for x in self.args]
        return apply(Constraint,args)

    def __str__(self):
        if(len(self.args) > 0):
            return "%s(%s)" % (self.functor, ','.join([str(x) for x in self.args]))
        else:
            return self.functor

    def contains(self,other):
        return any([x.contains(other) for x in self.canonical().args])

class PythonTerm(Term):
    def __init__(self,term):
        if(isinstance(term,PythonTerm)):
            self.term = term.term
        else:
            self.term = term

    def canonical(self):
        return self

    def __str__(self):
        return "%s" % (self.term,)

    def contains(self,other):
        return other == self or other == self.term

class ConstraintStore(set):
    """A CHR constraint store is used to hold a collection of facts in the form of predicates."""
    #TODO
    #def match(self,pred):
        