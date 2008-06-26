import unittest
from rulesystem import *

class RuleSystemTest(unittest.TestCase):
    def setUp(self):
        self.rs = RuleSystem(["pred"])
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

if __name__ == "__main__":
    unittest.main()
