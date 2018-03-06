from enum import Enum


# Possible types of tiles. Determines movement capability, building placement, and so on.
class TileType(Enum):
    SEA = 1
    GRASS = 2
    WOODS = 3
    RESOURCE = 4
    MOUNTAIN = 5
    COAST = 6
    HILL = 7


# List detailing the height sequence for tiles when terraforming.
# To raise a tile, move one step to the right, and to lower it, move one step to the left.
tile_height_order = [TileType.SEA, TileType.COAST, TileType.GRASS, TileType.HILL, TileType.MOUNTAIN]
