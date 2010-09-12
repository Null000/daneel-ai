import unittest
from rulesystem import *

from logilab.constraint import fd, Solver, Repository

import logging, sys
logging.basicConfig(level=logging.WARNING,stream=sys.stdout)

class RuleSystemTest(unittest.TestCase):
    def setUp(self):
        self.rs = RuleSystem(["pred(int)","gcd(int)","info(str)","a"])
    def testExchange(self):
        rule = Rule(self.rs)
        rule.name = "exchange"
        rule.removedhead = [FreeConstraint("pred",[int])]
        rule.guard = [fd.Equals("_var_0_0",2)]
        rule.body = "pred(42)"
        self.rs.rules = [rule]
        self.rs.addConstraint("pred(2)")
        [res] = self.rs.findConstraint(FreeConstraint("pred",[int]))
        assert res.args[0] == 42
        assert len(self.rs.store) == 1
    def testFiniteFiring(self):
        rule = Rule(self.rs) # pred(2) ==> pred(42)
        rule.name = "finite"
        rule.kepthead = [FreeConstraint("pred",[int])]
        rule.guard = [fd.Equals("_var_0_0",2)]
        rule.body = "pred(42)"
        self.rs.rules = [rule]
        self.rs.addConstraint("pred(2)")
        [res1,res2] = self.rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 42 or res2.args[0] == 42
        assert len(self.rs.store) == 2
    def testMultiFiring(self):
        rule = Rule(self.rs) # a and pred(X) ==> gcd(X)
        rule.name = "multi"
        rule.kepthead = [FreeConstraint("a",[]),FreeConstraint("pred",[int])]
        rule.guard = []
        rule.body = "gcd(_var_1_0)"
        self.rs.rules = [rule]
        self.rs.addConstraint("pred(2)")
        self.rs.addConstraint("pred(3)")
        self.rs.addConstraint("a")
        assert len(self.rs.store) == 5
    def testNoArg(self):
        rule = Rule(self.rs) # a and pred(2) <=> pred(1)
        rule.name = "noarg"
        rule.removedhead = [FreeConstraint("a",[]),FreeConstraint("pred",[int])]
        rule.guard = [fd.Equals("_var_1_0",2)]
        rule.body = "pred(1)"
        self.rs.rules = [rule]
        self.rs.addConstraint("pred(2)")
        self.rs.addConstraint("a")
        [res] = self.rs.findConstraint(FreeConstraint("pred",[int]))
        assert res.args[0] == 1
        assert len(self.rs.store) == 1
    def testGCD(self):
        rule1 = Rule(self.rs) # gcd(0) <==> pass
        rule1.name = "remove"
        rule1.removedhead = [FreeConstraint("gcd",[int])]
        rule1.guard = [fd.Equals("_var_0_0",0)]
        rule1.body = "pass"
        rule2 = Rule(self.rs) # gcd(X) \ gcd(Y) <==> X<=Y | gcd(Y-X)
        rule2.name = "reduce"
        rule2.kepthead = [FreeConstraint("gcd",[int])]
        rule2.removedhead = [FreeConstraint("gcd",[int])]
        rule2.guard = [fd.make_expression(("_var_0_0","_var_1_0"),"_var_0_0 <= _var_1_0")]
        rule2.body = "p = _var_1_0 - _var_0_0; gcd(p)"
        self.rs.rules = [rule1,rule2]
        self.rs.addConstraint("gcd(15)")
        self.rs.addConstraint("gcd(20)")
        [res] = self.rs.findConstraint(FreeConstraint("gcd",[int]))
        assert res.args[0] == 5
        assert len(self.rs.store) == 1
    def testMultiRule(self):
        rule1 = Rule(self.rs) # pred(1) ==> pred(2)
        rule1.name = "one"
        rule1.kepthead = [FreeConstraint("pred",[int])]
        rule1.guard = [fd.Equals("_var_0_0",1)]
        rule1.body = "pred(2)"
        rule2 = Rule(self.rs) # pred(1) ==> pred(3)
        rule2.name = "two"
        rule2.kepthead = [FreeConstraint("pred",[int])]
        rule2.guard = [fd.Equals("_var_0_0",1)]
        rule2.body = "pred(3)"
        self.rs.rules = [rule1,rule2]
        self.rs.addConstraint("pred(1)")
        assert len(self.rs.store) == 3

class ParsingTest(unittest.TestCase):
    def testProp(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(1) ==> pred(2)"])
        rs.addConstraint("pred(1)")
        [res1,res2] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2 or res2.args[0] == 2
        assert len(rs.store) == 2
    def testSimpl(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(1) <=> pred(2)"])
        rs.addConstraint("pred(1)")
        [res1] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2
        assert len(rs.store) == 1
    def testSimpa(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(1) \ pred(10) <=> pred(2)"])
        rs.addConstraint("pred(10)")
        rs.addConstraint("pred(1)")
        [res1,res2] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2 or res2.args[0] == 2
        assert not (res1.args[0] == 10 or res2.args[0] == 10)
        assert len(rs.store) == 2
    def testList(self):
        rs = RuleSystem(["pred(tuple)"],["rule @ pred((1,)) <=> pred((1,2))"])
        rs.addConstraint("pred((1,))")
        [res1] = rs.findConstraint(FreeConstraint("pred",[tuple]))
        assert res1.args[0] == (1,2)
        assert len(rs.store) == 1
    def testString(self):
        rs = RuleSystem(["info(str)"],["rule @ info('foo') <=> info('bar')"])
        rs.addConstraint("info('foo')")
        [res] = rs.findConstraint(FreeConstraint("info",[int]))
        assert res.args[0] == "bar"
        assert len(rs.store) == 1
    def testUnicode(self):
        rs = RuleSystem(["info(unicode)"],["rule @ info('foo') <=> info('bar')"])
        rs.addConstraint("info('foo')")
        [res] = rs.findConstraint(FreeConstraint("info",[int]))
        assert res.args[0] == "bar"
        assert len(rs.store) == 1
    def testGuard(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(X) ==> X > 5 | Y = X - 10; pred(Y)"])
        rs.addConstraint("pred(2)")
        rs.addConstraint("pred(11)")
        assert len(rs.store) == 3
    def testEquals(self):
        rs = RuleSystem(["pred(int)","prod(int)"],["rule @ pred(X) and prod(X) ==> Y = X - 10; pred(Y)"])
        rs.addConstraint("pred(2)")
        rs.addConstraint("prod(3)")
        rs.addConstraint("prod(2)")
        assert len(rs.store) == 4
    def testSearchAlgo(self):
        #you might want to draw this
        basic = ["search(int,int,tuple)", "edge(int,int)", "goal(int)", "reached(tuple)"]
        rules = ["edge(V1,V2) and search(V1,N,L) ==> V2 not in L and N > 0 | search(V2,N-1,L+(V2,))",
                    "search(V,0,L) and goal(V) <=> reached(L)",
                    "search(V,_,_) <=> pass"]
        rs = RuleSystem(basic,rules)
        rs.addConstraint("edge(1,2)")
        rs.addConstraint("edge(2,3)")
        rs.addConstraint("edge(2,4)")
        rs.addConstraint("edge(3,4)")
        rs.addConstraint("edge(4,5)")
        rs.addConstraint("goal(5)")
        assert len(rs.store) == 6
        rs.addConstraint("search(2,1,(2,))")
        assert len(rs.store) == 6
        assert rs.findConstraint(FreeConstraint("reached",[int])) == []
        rs.addConstraint("search(1,3,(1,))")
        assert len(rs.store) == 6
        [res] = rs.findConstraint(FreeConstraint("reached",[int]))
        path = res.args[0]
        assert path == (1,2,4,5)

class LongTermTest(unittest.TestCase):
    def setUp(self):
        self.rs = RuleSystem(["short(int)","long(int)*"])
    def testClear(self):
        self.rs.addConstraint("short(5)")
        self.rs.addConstraint("long(10)")
        self.rs.clearStore()
        assert len(self.rs.store) == 1
        [res] = self.rs.findConstraint(FreeConstraint("long",[int]))
        assert res.args[0] == 10

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromName("ruletest")
    unittest.TextTestRunner().run(suite)
