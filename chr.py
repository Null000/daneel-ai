import re

class Context(dict):
    """Keeps track of logical variables."""
    def checkTerm(f):
        """Allows you to both pass a string representing a variable or a LogicVar object as arguments"""
        def checked(self,var):
            if(not isinstance(var,Term)):
                var = self.parse(var)
            return f(self,var)
        return checked

    def __init__(self,constraintList=[]):
        """Initializes the context with a list of constraint terms"""
        self.constraints = constraintList

    def __missing__(self,key):
        if(re.match(r"^[A-Z]\w*$",key)):
            v = LogicVar(self,key)
            self[key] = v
            return v
        raise KeyError, "Name (%s) not found in CHR context!" % key

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

    def parse(self,expr):
        """Parses an expression into a Term.
        Valid expressions are for example "X", "z" or "f(g(123),B)".
        We use the Prolog convention that tokens starting with lowercase are terms
        and tokens starting with uppercase are variables.
        Only functors that appear in the constraint list will be parsed to CHR constraints,
        the other expressions are assumed to be Python code.
        """
        expr = str(expr).strip()
        if(re.match(r"^[A-Z]\w*$",expr)):
            return self[expr] #variable
        else:
            m = re.match(r"^(\w+)(\( *(.+, *)*.+ *\))?$",expr)
            if(m is not None):
                functor = m.group(1)
                if(functor in self.constraints):
                    args = m.group(2)[1:-1].split(",")
                    args = [self.parse(x) for x in args]
                    return Constraint(self,functor,*args)
            return PythonTerm(self,expr)


class Term:
    """A term in a CHR context. Can be a variable, a constraint or a wrapped Python primitive."""
    def __init__(self,context):
        self.context = context

class LogicVar(Term):
    """A logical variable in a CHR context. Can optionally be linked to
    another logical variable to make this an alias of the other.
    To prevent loops, the last link in a chain of aliases should always
    be used, this is the canonical form of the variable"""
    def __init__(self,context,name,alias=None):
        Term.__init__(self,context)
        self.name = name
        self.link = alias            

    def __str__(self):
        return (self.name if self.link is None else "%s=%s" % self.name,self.canonical())

    def canonical(self):
        var = self
        while(isinstance(var,LogicVar) and var.link is not None):
            var = var.link
        if(isinstance(var,LogicVar)):
            return var
        else:
            return var.canonical()
        
    def contains(self, other):
        return self.canonical() == other.canonical()

    def ground(self):
        return not isinstance(self.canonical(),LogicVar)

class Constraint(Term):
    def __init__(self,context,name,*args):
        Term.__init__(self,context)
        self.functor = name
        self.args = [(x if isinstance(x,Term) else PythonTerm(self.context,x)) for x in args]

    def arity(self):
        return len(self.args)

    def canonical(self):
        args = [x.canonical() for x in self.args]
        return Constraint(self.context,self.functor,*args)

    def __str__(self):
        if(len(self.args) > 0):
            return "%s(%s)" % (self.functor, ','.join([str(x) for x in self.args]))
        else:
            return self.functor

    def contains(self,other):
        return any([x.contains(other) for x in self.canonical().args])

    def ground(self):
        return all([x.ground() for x in self.canonical().args])

class PythonTerm(Term):
    p = re.compile(r"\b([A-Z]\w*)\b")

    def __init__(self,context,term):
        Term.__init__(self,context)
        if(isinstance(term,PythonTerm)):
            self.term = term.term
        else:
            self.term = term
        self.args = PythonTerm.p.findall(self.term)

    def canonical(self):
        if(self.ground()):
            localterm = self.term
            for x in self.args:
                pat = re.compile(r"\b%s\b" % x)
                repl = self.context[x].canonical()
                localterm = pat.sub(str(repl),localterm)
            return eval(localterm)
        else:
            return self.term

    def __str__(self):
        return "%s" % (self.term,)

    def contains(self,other):
        return other == self or other == self.term

    def ground(self):
        #The correct way to do this would probably be to create the parse tree
        #and search whether all variables are ground, but this seems to work too
        if(len(self.args) == 0):
            return True
        else:
            return all([self.context.parse(x).ground() for x in self.args])


class ConstraintStore(set):
    """A CHR constraint store is used to hold a collection of facts in the form of predicates."""
    #TODO
    #def match(self,pred):
        