import unittest
from maps.bounding_box import BoundingBox

class BoundingBoxTest(unittest.TestCase):

    def test_get_area(self):
        self.assertEqual(BoundingBox(0, 0, 3, 3).get_area(), 9)
        self.assertEqual(BoundingBox(0, 0, 0, 0).get_area(), 0)
        self.assertEqual(BoundingBox(3, 1, 4, 3).get_area(), 2)