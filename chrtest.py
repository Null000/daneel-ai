import unittest
from chr import *

class ContextTest(unittest.TestCase):
    def setUp(self):
        self.c = Context(["pred"])
    def testParsing(self):
        assert isinstance(self.c.parse(42),PythonTerm)
        assert isinstance(self.c.parse("X"),LogicVar)
        assert isinstance(self.c.parse("pred(32)"),Constraint)
        assert isinstance(self.c.parse("f(32)"),PythonTerm)
    def testTrivialUnification(self):
        assert self.c.unify(42,42)
        assert not self.c.unify(42,43)
    def testVarUnification(self):
        assert self.c.unify("X",23)
        assert not self.c.unify("X",230)
        assert self.c.unify("X",23)
        assert self.c.unify(23,"X")
        assert self.c.has_key("X")
        assert self.c["X"].ground()
    def testInfiniteUnification(self):
        assert not self.c.unify("X","f(X)")
        assert not self.c.unify("X","pred(X)")
        assert not self.c["X"].ground()
    def testTwowayUnification(self):
        assert self.c.unify("pred(A,2)","pred(4,B)")
        assert self.c.has_key("A")
        assert not self.c.unify("A",5)
        assert self.c.unify("A",4)
        assert self.c.has_key("B")
        assert not self.c.unify("B",5)
        assert self.c.unify("B",2)
    def testFailingPythonUnification(self):
        #this doesn't unify because f is not defined as being a constraint
        #we see it as a Python term, it doesn't make sense to try to unify this
        assert not self.c.unify("f(1,2)","f(A,B)")
        assert not self.c["A"].ground()
        assert not self.c["B"].ground()
    def testFailingConstraintUnification(self):
        assert not self.c.unify("pred(1,2,5)","pred(A,3,B)")
        assert not self.c["A"].ground()
        assert not self.c["B"].ground()
    def testMultiUnification(self):
        #hope I get about all cases here
        assert self.c.unify("pred(A,pred(B),pred(5),pred(A))","pred(1,pred(pred(5)),B,pred(1))")
        assert self.c["A"].ground()
        assert str(self.c["A"].canonical()) == '1'
        assert isinstance(self.c["A"],LogicVar)
        assert isinstance(self.c["A"].link,PythonTerm)
        assert self.c["B"].ground()
        assert str(self.c["B"].canonical()) == 'pred(5)'
        assert isinstance(self.c["B"],LogicVar)
        assert isinstance(self.c["B"].link,Constraint)
    def testChainUnification(self):
        assert self.c.unify("A","B")
        assert self.c.unify("pred(B)","pred(C)")
        assert self.c.unify("C","5")
        assert str(self.c["A"].canonical()) == '5'

    def testPythonTermEval(self):
        self.c["f"] = lambda x:x+5
        term = self.c.parse("f(f(X))")
        assert not term.ground()
        assert self.c.unify("X",10)
        assert term.ground()
        assert term.evaluate() == 20

class ConstraintStoreTest(unittest.TestCase):
    def setUp(self):
        self.s = ConstraintStore(["pred","pred2"])

    def testMultiset(self):
        self.s.add("pred(1)")
        self.s.add("pred(1)")
        assert len(self.s) == 2

    def testMatch(self):
        self.s.add("pred(1)")
        matches = self.s.match(["pred(X)"])
        assert len(matches) == 1
        assert isinstance(matches[0][0],Constraint)
        assert str(matches[0][0]) == "pred(1)"

    def testMultiMatch(self):
        self.s.add("pred(1)")
        self.s.add("pred2(5)")
        matches = self.s.match(["pred2(X)","pred(Y)"])
        assert len(matches) == 1
        assert isinstance(matches[0][0],Constraint)
        assert str(matches[0][0]) == "pred2(5)"
        assert str(matches[0][1]) == "pred(1)"

    def testMultiMatchSame(self):
        self.s.add("pred(1)")
        self.s.add("pred(5)")
        matches = self.s.match(["pred(X)","pred(Y)"])
        assert len(matches) == 2 #once for 1,5 and once for 5,1

if __name__ == "__main__":
    unittest.main()
