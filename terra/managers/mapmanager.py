from pygame import Surface, SRCALPHA
import random
from io import StringIO
from os import walk

from terra.engine.gameobject import GameObject
from terra.event import is_event_type, E_TILE_TERRAFORMED
from terra.map.tile import Tile
from terra.map.tiletype import TileType, tile_height_order
from terra.piece.movementtype import movement_types, MovementAttribute
from terra.resources.assets import AssetType, get_asset, spr_tiles_mini
from terra.util.mathutil import clamp


# A single map containing tiles, organized into a grid.
class MapManager(GameObject):
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
               self.get_tile_type_at(gx, gy) in movement_types[movement_type][MovementAttribute.PASSABLE]

    # Return true if our movement type can pass over the tile, but not end movement on it
    def is_tile_traversable(self, gx, gy, movement_type):
        return 0 <= gx < self.width and 0 <= gy < self.height and \
               self.get_tile_type_at(gx, gy) in movement_types[movement_type][MovementAttribute.TRAVERSABLE]

    # From the tiles adjacent to (gx, gy), return any that are passable for the provided movement type
    def get_valid_adjacent_tiles_for_movement_type(self, gx, gy, movement_type):
        tiles_to_check = [(gx + 1, gy),
                          (gx - 1, gy),
                          (gx, gy + 1),
                          (gx, gy - 1)]

        return [(tile_x, tile_y) for tile_x, tile_y in tiles_to_check
                if self.is_tile_passable(tile_x, tile_y, movement_type)]

    # Update the tile at the specified location to the new type
    def update_tile_type(self, gx, gy, new_tile_type):
        self.tile_grid[gy][gx] = Tile(self, new_tile_type, gx, gy)

    # Terraform a tile according to an event
    def terraform_tile(self, event):
        tile_type = self.get_tile_type_at(event.gx, event.gy)
        if event.raising:
            new_tile_type_index = tile_height_order.index(tile_type) + 1
        else:
            new_tile_type_index = tile_height_order.index(tile_type) - 1

        self.update_tile_type(event.gx, event.gy, tile_height_order[clamp(new_tile_type_index, 0, len(tile_height_order) - 1)])

    # Replace all tiles with the provided tiletype.
    def fill_map_with_tile(self, new_tile_type):
        for x in range(self.width):
            for y in range(self.height):
                self.update_tile_type(x, y, new_tile_type)

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_TILE_TERRAFORMED):
            self.terraform_tile(event)

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
    for (_, _, filenames) in walk(get_asset(AssetType.MAP, "")):
        maps.extend(filenames)

    return [mapname for mapname in maps if mapname.endswith(suffix)]


# Parse a map's data out from a string representation
def parse_map_from_string(map_data):
    reading_pieces = False
    reading_teams = False
    reading_upgrades = False

    bitmap = []
    pieces = []
    teams = []
    upgrades = []

    for line in StringIO(map_data):
        if line.rstrip() == "# Pieces":
            reading_pieces = True
        elif line.rstrip() == "# Teams":
            reading_teams = True
        elif line.rstrip() == "# Upgrades":
            reading_upgrades = True
        elif reading_upgrades:
            if line.rstrip():
                # Add each line to upgrades
                upgrades.append(line.rstrip())
        elif reading_teams:
            if line.rstrip():
                # Add each line to teams
                teams.append(line.rstrip())
        elif reading_pieces:
            if line.rstrip():
                # Add each line to the piece list
                pieces.append(line.rstrip())
        else:
            # Grab all non-newline chars, convert them to ints, and add them to the line list
            bitmap.append(list(map(int, line.rstrip().split(' '))))

    return bitmap, pieces, teams, upgrades


# Load a map from the provided filename
# Generate a bitmap for the Map to use, and generate a unit list for the PieceManager to use.
def load_map_from_file(mapname):
    try:
        map_path = get_asset(AssetType.MAP, mapname)

        with open(map_path) as mapfile:
            return parse_map_from_string(mapfile.read())
    except IOError as e:
        print("Unable to load file {}. Generating new map. Exception: {}".format(mapname, e))
        return generate_map()


# Generate a default map, pieces, teams, and so on, ready for use.
def generate_map():
    bitmap = generate_bitmap(20, 16, False)
    pieces = ["0 0 RED BASE", "19 15 BLUE BASE"]
    teams = ["RED 5 5 5", "BLUE 5 5 5"]
    upgrades = ["RED|", "BLUE|"]

    return bitmap, pieces, teams, upgrades


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


# Generate a surface containing a minimap of the passed in bitmap
def generate_minimap(bitmap):
    height = len(bitmap)
    width = len(bitmap[0])

    minimap = Surface((width * 4, height * 4), SRCALPHA, 32)

    for x in range(width):
        for y in range(height):
            minimap.blit(spr_tiles_mini[bitmap[y][x]], (x * 4, y * 4))

    return minimap
