import unittest

from terra.util.collectionutil import safe_get_from_list


class CollectionUtilTest(unittest.TestCase):
    l = [0, 1, 2, 3, 4]

    # Normal gets should return the value
    def test_in_bounds_get(self):
        self.assertEqual(safe_get_from_list(self.l, 3), 3)

    # Out of bound gets should return None
    def test_out_of_bounds_get(self):
        self.assertEqual(safe_get_from_list(self.l, 10), None)
