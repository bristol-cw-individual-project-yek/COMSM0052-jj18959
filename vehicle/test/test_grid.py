import unittest
import vehicle.grid as grid

class TestGrid(unittest.TestCase):

    def test_position_to_grid_square(self):
        self.assertEqual(grid.GRID_SQUARE_LENGTH, 10)

        self.assertEqual(grid.position_to_grid_square((0, 0)), (0, 0))
        self.assertEqual(grid.position_to_grid_square((0, 5)), (0, 0))
        self.assertEqual(grid.position_to_grid_square((10, 15)), (1, 1))
        self.assertEqual(grid.position_to_grid_square((-1, -10)), (-1, -1))
        self.assertEqual(grid.position_to_grid_square((-1, -10.000000000001)), (-1, -2))
        self.assertEqual(grid.position_to_grid_square((-22, 100)), (-3, 10))
        self.assertEqual(grid.position_to_grid_square((-11.3, 152.5)), (-2, 15))