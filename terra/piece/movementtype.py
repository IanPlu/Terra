from enum import Enum

from terra.map.tiletype import TileType


# Each possible movement type. Controls how a piece can move or target.
class MovementType(Enum):
    NONE = 0
    GROUND = 1
    BANSHEE = 2
    FLYING = 3
    BUILDING = 4
    GENERATOR = 5


class MovementAttribute(Enum):
    PASSABLE = "PASSABLE"
    TRAVERSABLE = "TRAVERSABLE"


# Sets of terrain types each movement type allows traversal over
movement_types = {
    None: {
        MovementAttribute.PASSABLE: set(TileType),
        MovementAttribute.TRAVERSABLE: {},
    },
    MovementType.GROUND: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {},
    },
    MovementType.BANSHEE: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {TileType.SEA, TileType.HILL},
    },
    MovementType.FLYING: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE, TileType.SEA, TileType.HILL},
        MovementAttribute.TRAVERSABLE: {}
    },
    MovementType.BUILDING: {
        MovementAttribute.PASSABLE: {TileType.GRASS},
        MovementAttribute.TRAVERSABLE: {},
    },
    MovementType.GENERATOR: {
        MovementAttribute.PASSABLE: {TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {},
    },
}
