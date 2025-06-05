import unittest
from nova_strategy import adjust_weights


class AdjustWeightsTest(unittest.TestCase):
    def test_decay(self):
        weights = {"a": 0.5, "b": 0.5}
        stats = {"a": {"failures": 8, "total": 10}, "b": {"failures": 1, "total": 10}}
        updated = adjust_weights(weights, stats, decay_rate=0.2, threshold=0.7)
        self.assertAlmostEqual(updated["a"], 0.3)
        self.assertAlmostEqual(updated["b"], 0.5)


if __name__ == "__main__":
    unittest.main()
