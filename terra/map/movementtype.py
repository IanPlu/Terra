from enum import Enum

from terra.map.tiletype import TileType


# Each possible movement type. Controls how a piece can move or target.
class MovementType(Enum):
    NONE = 0
    GROUND = 1
    GHOST = 2
    BUILD_BARRACKS = 3
    BUILD_GENERATOR = 4


# Impassible terrain types per movement type
# TODO: Invert this
impassible_terrain_types = {
    None: [],
    MovementType.GROUND: [TileType.SEA],
    MovementType.GHOST: [TileType.SEA],
    MovementType.BUILD_BARRACKS: [TileType.SEA, TileType.WOODS, TileType.RESOURCE],
    MovementType.BUILD_GENERATOR: [TileType.SEA, TileType.GRASS, TileType.WOODS]
}
