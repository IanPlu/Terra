from enum import Enum

from terra.map.tiletype import TileType


# Each possible movement type. Controls how a piece can move or target.
class MovementType(Enum):
    NONE = 0
    GROUND = 1
    GHOST = 2
    BUILDING = 3
    GENERATOR = 4


# Sets of terrain types each movement type allows traversal over
passable_terrain_types = {
    None: set(TileType),
    MovementType.GROUND: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
    MovementType.GHOST: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
    MovementType.BUILDING: {TileType.GRASS},
    MovementType.GENERATOR: {TileType.RESOURCE},
}
