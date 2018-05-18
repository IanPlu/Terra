import random
from enum import Enum
from io import StringIO
from os import walk

from opensimplex import OpenSimplex

from terra.resources.assetloading import AssetType, get_asset


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


# Return true if the provided map exists
def map_exists(mapname, asset_type=AssetType.MAP):
    try:
        map_path = get_asset(asset_type, mapname)
        with open(map_path):
            return True
    except IOError:
        return False


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
