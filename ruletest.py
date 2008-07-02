import unittest
from rulesystem import *

class RuleSystemTest(unittest.TestCase):
    def setUp(self):
        self.rs = RuleSystem(["pred","gcd"])
    def testExchange(self):
        rule = Rule(self.rs)
        rule.removedhead = [FreeConstraint("pred",1)]
        rule.guard = "_var_0_0 == 2"
        rule.body = "pred(42)"
        self.rs.rules = [rule]
        self.rs.addConstraint(BoundConstraint("pred",[2]))
        [res] = self.rs.findConstraint(FreeConstraint("pred",1))
        assert res.args[0] == 42
        assert len(self.rs.store) == 1
    def testFiniteFiring(self):
        rule = Rule(self.rs)
        rule.kepthead = [FreeConstraint("pred",1)]
        rule.guard = "_var_0_0 == 2"
        rule.body = "pred(42)"
        self.rs.rules = [rule]
        self.rs.addConstraint(BoundConstraint("pred",[2]))
        [res] = self.rs.findConstraint(FreeConstraint("pred",1))
        assert res.args[0] == 42
        assert len(self.rs.store) == 2
    def testGCD(self):
        rule1 = Rule(self.rs) # gcd(0) <==> pass
        rule1.removedhead = [FreeConstraint("gcd",1)]
        rule1.guard = "_var_0_0 == 0"
        rule1.body = "pass"
        rule2 = Rule(self.rs) # gcd(X) \ gcd(Y) <==> X>=Y | gcd(X-Y)
        rule2.kepthead = [FreeConstraint("gcd",1)]
        rule2.removedhead = [FreeConstraint("gcd",1)]
        rule2.guard = "_var_0_0 >= _var_1_0"
        rule2.body = "p = _var_0_0 - _var_1_0; gcd(p)"
        self.rs.rules = [rule1,rule2]
        self.rs.addConstraint(BoundConstraint("gcd",[15]))
        self.rs.addConstraint(BoundConstraint("gcd",[20]))
        [res] = self.rs.findConstraint(FreeConstraint("gcd",1))
        assert res.args[0] == 5
        assert len(self.rs.store) == 1

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(RuleSystemTest)
    unittest.TextTestRunner().run(suite)
