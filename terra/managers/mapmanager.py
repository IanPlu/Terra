import random
from enum import Enum
from io import StringIO
from os import walk

from opensimplex import OpenSimplex
from pygame import Surface, SRCALPHA

from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.map.tile import Tile
from terra.map.tiletype import tile_height_order
from terra.piece.movementtype import movement_types, MovementAttribute
from terra.resources.assetloading import AssetType, get_asset
from terra.resources.assets import spr_tiles_mini
from terra.util.mathutil import clamp


# Steps involved in reading in the map.
class MapReadingStep(Enum):
    META = "# Meta"
    UPGRADES = "# Upgrades"
    TEAMS = "# Teams"
    PIECES = "# Pieces"
    MAP = "# Map"

    # Return the enum member corresponding to the provided string, if any. Returns None if no match.
    @staticmethod
    def safe_get_from_string(str):
        for member in MapReadingStep:
            if member.value == str:
                return member

        return None


# A single map containing tiles, organized into a grid.
class MapManager(GameObject):
    def __init__(self, bitmap=None, width=10, height=10):
        super().__init__()

        # Use a provided bitmap to generate tiles, otherwise generate one of the provided size
        # These are only integers (not tiles) for faster modification.
        if bitmap:
            self.bitmap = bitmap
        else:
            self.bitmap = generate_bitmap_from_simplex_noise(width, height)

        self.height = len(self.bitmap)
        self.width = len(self.bitmap[0])

        # Serialize the map to Tile objects (from integers)
        self.tile_grid = self.convert_grid_from_bitmap(self.bitmap)

    def register_handlers(self, event_bus):
        event_bus.register_handler(EventType.E_TILE_TERRAFORMED, self.terraform_tile)

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

    # Mirror the map across the specified axes, prioritizing the top-left-most tiles.
    def mirror_map(self, mirror_x=True, mirror_y=False):
        for x in range(self.width):
            for y in range(self.height):
                mx = self.width - 1 - x if mirror_x else x
                my = self.height - 1 - y if mirror_y else y
                self.update_tile_type(mx, my, self.get_tile_type_at(x, y))

    # Render the map to the screen
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        for x in range(self.width):
            for y in range(self.height):
                self.tile_grid[y][x].render(game_screen, ui_screen)


# Return a list of filenames of loadable maps
def get_loadable_maps(asset_type=AssetType.MAP):
    maps = []
    for (_, _, filenames) in walk(get_asset(asset_type, "")):
        maps.extend(filenames)

    return maps


# Parse a map's data out from a string representation
def parse_map_from_string(map_data):
    step = MapReadingStep.MAP

    bitmap = []
    pieces = []
    teams = []
    upgrades = []
    meta = {}

    for line in StringIO(map_data):
        sline = line.rstrip()

        if MapReadingStep.safe_get_from_string(sline):
            step = MapReadingStep(sline)
        elif step == MapReadingStep.MAP:
            # Grab all non-newline chars, convert them to ints, and add them to the line list
            bitmap.append(list(map(int, sline.split(' '))))
        elif step == MapReadingStep.PIECES:
            if line.rstrip():
                # Add each line to the piece list
                pieces.append(sline)
        elif step == MapReadingStep.TEAMS:
            if sline:
                # Add each line to teams
                teams.append(sline)
        elif step == MapReadingStep.UPGRADES:
            if sline:
                # Add each line to upgrades
                upgrades.append(sline)
        elif step == MapReadingStep.META:
            if sline:
                # Split into key pairs and add to meta
                # Note that non-pairs (too many or too few items) are ignored
                values = sline.split(' ')
                if len(values) == 2:
                    meta[values[0]] = values[1]

    return bitmap, pieces, teams, upgrades, meta


# Load a map from the provided filename
# Generate a bitmap for the Map to use, and generate a unit list for the PieceManager to use.
def load_map_from_file(mapname, asset_type=AssetType.MAP):
    try:
        map_path = get_asset(asset_type, mapname)

        with open(map_path) as mapfile:
            return parse_map_from_string(mapfile.read())
    except IOError as e:
        print("Unable to load file {}. Generating new map. Exception: {}".format(mapname, e))
        return generate_map()


# Generate a default map, pieces, teams, and so on, ready for use.
def generate_map():
    bitmap = generate_bitmap_from_simplex_noise(20, 15, mirror_x=False, mirror_y=False)
    pieces = []
    teams = ["RED 5 5 5", "BLUE 5 5 5"]
    upgrades = ["RED|", "BLUE|"]
    meta = {
        "Turn": "1",
        "Phase": "START_TURN",
    }

    return bitmap, pieces, teams, upgrades, meta


# Generate a map of the required size
def generate_bitmap(width, height, random_tiles=True):
    bitmap = []
    for _ in range(height):
        row = []
        for _ in range(width):
            if random_tiles:
                tile = random.randint(1, 2)
            else:
                tile = 1
            row.append(tile)
        bitmap.append(row)

    return bitmap


# Generate a bitmap using simplex noise and some fancy footwork
# https://www.redblobgames.com/maps/terrain-from-noise/
def generate_bitmap_from_simplex_noise(width, height, mirror_x=False, mirror_y=False):
    generator = OpenSimplex(seed=random.randint(0, 100))

    # Generate a noise value from 0 to 1
    def noise(noise_x, noise_y):
        return generator.noise2d(noise_x, noise_y) / 2.0 + 0.5

    # Convert a height value to an integer representing a tile (1=SEA, 2=GRASS, etc.)
    def get_tile_from_height(t_height):
        if t_height <= 0.7:
            return 1
        elif t_height <= 1.1:
            return 2
        elif t_height <= 1.2:
            return 7
        else:
            return 5

    bitmap = []
    for y in range(height):
        row = []
        for x in range(width):
            nx = x / width - 0.5
            ny = y / height - 0.5
            elevation = 1 * noise(nx, ny) + 0.5 * noise(nx * 2, ny * 2) + 0.25 * noise(nx * 4, ny * 4)

            distance_to_center = 2 * max(abs(nx), abs(ny))
            base_height = 0.1
            edge_height = 0.4
            dropoff = 1.6

            fuzziness = random.randint(10, 20) / 10

            # Form islands
            elevation += (base_height - edge_height * pow(distance_to_center, dropoff)) * fuzziness

            tile = get_tile_from_height(round(elevation, 2))

            # Randomly add features to existing plains tiles
            if tile == 2:
                feature_chance = random.randint(0, 9)
                if feature_chance >= 9:
                    tile = 4
                elif feature_chance >= 8:
                    tile = 3

            row.append(tile)
        bitmap.append(row)

    if mirror_x or mirror_y:
        for y in range(height):
            for x in range(width):
                mx = width - 1 - x if mirror_x else x
                my = height - 1 - y if mirror_y else y

                bitmap[y][x] = bitmap[my][mx]

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
