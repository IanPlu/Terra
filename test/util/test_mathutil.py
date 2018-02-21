import unittest

from terra.util.mathutil import clamp


class MathUtilTest(unittest.TestCase):
    # Input already in bounds, return the same value
    def test_in_bounds(self):
        self.assertEqual(clamp(10, 5, 15), 10)

    # Input below lower bound, return lower bound
    def test_below_bound(self):
        self.assertEqual(clamp(0, 5, 15), 5)

    # Input above upper bound, return upper bound
    def test_above_bound(self):
        self.assertEqual(clamp(20, 5, 15), 15)
