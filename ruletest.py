import unittest
from rulesystem import *

from logilab.constraint import fd, Solver, Repository

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
    def testString(self):
        rule = Rule(self.rs) # info("foo") <=> info("bar")
        rule.name = "str"
        rule.removedhead = [FreeConstraint("info",[str])]
        rule.guard = [fd.Equals("_var_0_0","foo")]
        rule.body = "info('bar')"
        self.rs.rules = [rule]
        self.rs.addConstraint("info(foo)")
        [res] = self.rs.findConstraint(FreeConstraint("info",[int]))
        assert res.args[0] == "bar"
        assert len(self.rs.store) == 1
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
        rs = RuleSystem(["pred(int)"],["rule @ pred(int) ==> _var_0_0 == 1 | pred(2)"])
        rs.addConstraint("pred(1)")
        [res1,res2] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2 or res2.args[0] == 2
        assert len(rs.store) == 2
    def testSimpl(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(int) <=> _var_0_0 == 1 | pred(2)"])
        rs.addConstraint("pred(1)")
        [res1] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2
        assert len(rs.store) == 1
    def testSimpa(self):
        rs = RuleSystem(["pred(int)"],["rule @ pred(int) \ pred(int) <=> _var_0_0 == 1 and _var_1_0 == 10 | pred(2)"])
        rs.addConstraint("pred(10)")
        rs.addConstraint("pred(1)")
        [res1,res2] = rs.findConstraint(FreeConstraint("pred",[int]))
        assert res1.args[0] == 2 or res2.args[0] == 2
        assert not (res1.args[0] == 10 or res2.args[0] == 10)
        assert len(rs.store) == 2
    def testList(self):
        rs = RuleSystem(["pred(tuple)"],["rule @ pred(tuple) <=> _var_0_0 == (1,) | pred((1,2))"])
        rs.addConstraint("pred((1,))")
        [res1] = rs.findConstraint(FreeConstraint("pred",[tuple]))
        assert res1.args[0] == (1,2)
        assert len(rs.store) == 1

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
