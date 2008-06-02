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


if __name__ == "__main__":
    unittest.main()