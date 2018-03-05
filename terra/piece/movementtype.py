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
    RAISE = 6
    LOWER = 7


class MovementAttribute(Enum):
    PASSABLE = "PASSABLE"
    TRAVERSABLE = "TRAVERSABLE"


# Sets of terrain types each movement type allows traversal over
movement_types = {
    # No movement type. Used for ranged attacks.
    None: {
        MovementAttribute.PASSABLE: set(TileType),
        MovementAttribute.TRAVERSABLE: {},
    },
    # Default groundbound movement type. Most pieces use this.
    MovementType.GROUND: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {},
    },
    # Banshee-specific pseudo-flying movement type. Can traverse SEA and HILLs but not stop on them.
    MovementType.BANSHEE: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {TileType.SEA, TileType.HILL},
    },
    # Flying movement type. Able to occupy any type of tile.
    MovementType.FLYING: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE, TileType.SEA, TileType.HILL},
        MovementAttribute.TRAVERSABLE: {}
    },
    # 'Movement' type used by buildings. Used for determining placement, i.e. only on grassland.
    MovementType.BUILDING: {
        MovementAttribute.PASSABLE: {TileType.GRASS},
        MovementAttribute.TRAVERSABLE: {},
    },
    # 'Movement' type used by generator buildings. Used for determining placement, i.e. only over resource tiles.
    MovementType.GENERATOR: {
        MovementAttribute.PASSABLE: {TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {},
    },
    # 'Movement' type used for terraforming. Controls which tiles can be raised.
    MovementType.RAISE: {
        MovementAttribute.PASSABLE: {TileType.SEA, TileType.GRASS},
        MovementAttribute.TRAVERSABLE: {},
    },
    # 'Movement' type used for terraforming. Controls which tiles can be lowered.
    MovementType.LOWER: {
        MovementAttribute.PASSABLE: {TileType.HILL, TileType.GRASS},
        MovementAttribute.TRAVERSABLE: {},
    },
}
