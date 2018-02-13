import unittest

from terra.managers.mapmanager import *


class MapManagerTest(unittest.TestCase):
    # Expected attributes of the test map
    test_map_name = "test_map.map"
    expected_bitmap = [
        [1, 1, 1, 1, 1],
        [2, 2, 2, 2, 2],
        [3, 3, 3, 3, 3],
        [4, 4, 4, 4, 4],
        [1, 2, 3, 4, 1]
    ]
    expected_pieces = [
        "1 1 RED BASE",
        "2 2 RED BARRACKS",
        "3 3 BLUE BASE",
        "4 4 BLUE BARRACKS"
    ]
    expected_teams = [
        "RED 10 20 30",
        "BLUE 10 10 10"
    ]

    # Getting loadable maps should return a list of map file names
    def test_get_loadable_maps(self):
        maps = get_loadable_maps()
        self.assertTrue(len(maps) > 0)

    # Getting loadable save files should return a list of save file names
    def test_get_loadable_save_files(self):
        saves = get_loadable_maps(".sav")
        self.assertTrue(len(saves) > 0)

    # Loading a map from a file should properly get a bitmap, lists of pieces, etc
    def test_load_map_from_file(self):
        bitmap, pieces, teams = load_map_from_file(self.test_map_name)

        self.assertEqual(bitmap, self.expected_bitmap)
        self.assertEqual(pieces, self.expected_pieces)
        self.assertEqual(teams, self.expected_teams)

    # Loading a map from a file should generate a new map when an exception occurs
    def test_load_map_from_file_with_error(self):
        bitmap, pieces, teams = load_map_from_file("garbage map name that doesn't exist")

        self.assertEqual(len(bitmap), 15)
        self.assertEqual(len(bitmap[0]), 20)

        expected_pieces = ["0 0 RED BASE", "20 15 BLUE BASE"]
        self.assertEqual(pieces, expected_pieces)

        expected_teams = ["RED 0 0 0", "BLUE 0 0 0"]
        self.assertEqual(teams, expected_teams)

    # Generated bitmaps should be of the provided width and height
    def test_generate_bitmap_check_size(self):
        width, height = 4, 3
        bitmap = generate_bitmap(width, height)
        self.assertEqual(len(bitmap), height)
        self.assertEqual(len(bitmap[0]), width)

    # Generated bitmaps should be of the SEA tile type if random is off
    def test_generate_bitmap_nonrandom_tiles(self):
        bitmap = generate_bitmap(3, 3, random_tiles=False)
        for row in bitmap:
            for column in row:
                if not column == 1:
                    self.fail("Wanted tile type 1, found {}".format(column))

    # A MapManager should be able to convert a bitmap to a structure of Tile objects
    def test_convert_grid_from_bitmap(self):
        bitmap, _, _ = load_map_from_file("test_map.map")
        manager = MapManager(bitmap)

        y = 0
        for row in manager.tile_grid:
            x = 0
            for column in row:
                if not column.tile_type.value == self.expected_bitmap[y][x]:
                    self.fail("Wanted tile type {}, found {}".format(column.tile_type, self.expected_bitmap[y][x]))
                x += 1
            y += 1

    # A MapManager should be able to serialize itself back into a bitmap for saving
    def test_convert_bitmap_from_grid(self):
        bitmap, _, _ = load_map_from_file("test_map.map")
        manager = MapManager(bitmap)

        converted_bitmap = manager.convert_bitmap_from_grid()
        self.assertEqual(bitmap, converted_bitmap)

    # A MapManager should be able to return the tile at the specified position
    def test_get_tile_at(self):
        bitmap, _, _ = load_map_from_file("test_map.map")
        manager = MapManager(bitmap)

        self.assertEqual(manager.get_tile_at(1, 1).tile_type.value, 2)
        self.assertEqual(manager.get_tile_at(3, 2).tile_type.value, 3)
        self.assertEqual(manager.get_tile_at(4, 4).tile_type.value, 1)
