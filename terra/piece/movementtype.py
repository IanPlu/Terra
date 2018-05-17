from enum import Enum, auto

from terra.map.tiletype import TileType


# Each possible movement type. Controls how a piece can move or target.
class MovementType(Enum):
    NONE = auto()
    GROUND = auto()
    HEAVY = auto()
    HOVER = auto()
    FLYING = auto()
    BUILDING = auto()
    GENERATOR = auto()
    MINE = auto()

    def __str__(self):
        from terra.strings import attribute_value_strings, get_string
        return get_string(attribute_value_strings, self)


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
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE, TileType.COAST, TileType.HILL},
        MovementAttribute.TRAVERSABLE: {},
    },
    # Heavier groundbound movement type. Doesn't allow stopping in rougher terrain like coasts or hills.
    MovementType.HEAVY: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE},
        MovementAttribute.TRAVERSABLE: {TileType.COAST, TileType.HILL},
    },
    # Banshee-specific pseudo-flying movement type. Can traverse SEA and HILLs but not stop on them.
    MovementType.HOVER: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE, TileType.COAST, TileType.HILL},
        MovementAttribute.TRAVERSABLE: {TileType.SEA, TileType.MOUNTAIN},
    },
    # Flying movement type. Able to occupy any type of tile.
    MovementType.FLYING: {
        MovementAttribute.PASSABLE: {TileType.GRASS, TileType.WOODS, TileType.RESOURCE, TileType.COAST,
                                     TileType.SEA, TileType.MOUNTAIN, TileType.HILL},
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
    # 'Movement' type used for mining. Controls which tiles can be raised.
    MovementType.MINE: {
        MovementAttribute.PASSABLE: {TileType.METEOR},
        MovementAttribute.TRAVERSABLE: {},
    },
}
