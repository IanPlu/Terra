from terra.map.movementtype import MovementType
from terra.map.tile import Tile
from terra.map.tiletype import TileType
from terra.engine.gameobject import GameObject
from terra.constants import Team
from os import walk
import random

impassible_terrain_types = {
    None: [],
    MovementType.GROUND: [TileType.SEA],
    MovementType.GHOST: [TileType.SEA],
    MovementType.BUILD_BARRACKS: [TileType.SEA, TileType.WOODS, TileType.RESOURCE],
    MovementType.BUILD_GENERATOR: [TileType.SEA, TileType.GRASS, TileType.WOODS]
}


# A single map containing tiles, organized into a grid.
class Map(GameObject):
    def __init__(self, bitmap=None, width=10, height=10):
        super().__init__()

        # Use a provided bitmap to generate tiles, otherwise generate one of the provided size
        # These are only integers (not tiles) for faster modification.
        if bitmap:
            self.bitmap = bitmap
        else:
            self.bitmap = generate_bitmap(width, height)

        self.height = len(self.bitmap)
        self.width = len(self.bitmap[0])

        # Serialize the map to Tile objects (from integers)
        self.tile_grid = self.convert_grid_from_bitmap(self.bitmap)

    # Given a 2D array of ints, convert it to a 2D array of Tile objects
    def convert_grid_from_bitmap(self, bitmap):
        grid = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = Tile(self, bitmap[y][x], x, y)
                row.append(tile)
            grid.append(row)

        return grid

    # Serialize ourselves into a bitmap
    def convert_bitmap_from_grid(self):
        bitmap = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                row.append(tile.tile_type.value)
            bitmap.append(row)

        return bitmap

    # Return the tile at the specified grid location.
    def get_tile_at(self, gx, gy):
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.tile_grid[gy][gx]
        else:
            return None

    # Return the tile type at the specified grid location.
    def get_tile_type_at(self, gx, gy):
        return getattr(self.get_tile_at(gx, gy), 'tile_type', None)

    # Return True if the tile is passable for the provided movement type. Tiles out of bounds are impassible.
    def is_tile_passable(self, gx, gy, movement_type):
        return 0 <= gx < self.width and 0 <= gy < self.height and \
               not self.get_tile_type_at(gx, gy) in impassible_terrain_types[movement_type]

    def update_tile_type(self, gx, gy, new_tile_type):
        self.tile_grid[gy][gx] = Tile(self, new_tile_type, gx, gy)

    def step(self, event):
        super().step(event)

    # Render the map to the screen
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        for x in range(self.width):
            for y in range(self.height):
                # print("x: {}, y: {}".format(x, y))
                self.tile_grid[y][x].render(game_screen, ui_screen)


# Return a list of filenames of loadable maps
def get_loadable_maps(suffix=".map"):
    maps = []
    for (_, _, filenames) in walk("resources/maps/"):
        maps.extend(filenames)

    return [mapname for mapname in maps if mapname.endswith(suffix)]


# Load a map from the provided filename
# Generate a bitmap for the Map to use, and generate a unit list for the PieceManager to use.
def load_map_from_file(mapname):
    reading_units = False
    reading_buildings = False
    reading_teams = False

    try:
        with open("resources/maps/" + mapname) as mapfile:
            bitmap = []
            roster = []
            buildings = []
            teams = []
            for line in mapfile:
                if line.rstrip() == "# Units":
                    reading_units = True
                elif line.rstrip() == "# Buildings":
                    reading_buildings = True
                elif line.rstrip() == "# Teams":
                    reading_teams = True
                elif reading_teams:
                    if line.rstrip():
                        # Add each line to teams
                        teams.append(line.rstrip())
                elif reading_buildings:
                    if line.rstrip():
                        # Add each line to the buildings
                        buildings.append(line.rstrip())
                elif reading_units:
                    if line.rstrip():
                        # Add each line to the roster
                        roster.append(line.rstrip())
                else:
                    # Grab all non-newline chars, convert them to ints, and add them to the line list
                    bitmap.append(list(map(int, line.rstrip().split(' '))))
    except IOError as e:
        print("Unable to load file {}. Generating new map. Exception: {}".format(mapname, e))
        bitmap = generate_bitmap(20, 15, False)
        roster = []
        buildings = ["0 0 RED BASE", "20 15 BLUE BASE"]
        teams = []

    return bitmap, roster, buildings, teams


# Generate a map of the required size
def generate_bitmap(width, height, random_tiles=True):
    bitmap = []
    for _ in range(height):
        row = []
        for _ in range(width):
            if random_tiles:
                tile = random.randint(1, len(TileType) - 1)
            else:
                tile = 1
            row.append(tile)
        bitmap.append(row)

    return bitmap
