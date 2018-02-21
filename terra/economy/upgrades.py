from terra.piece.piecetype import PieceType
from terra.piece.pieceattributes import Attribute
from enum import Enum, auto


class UpgradeType(Enum):
    RESOURCE_PRODUCTION_1 = auto()
    RESOURCE_PRODUCTION_2 = auto()

    COLONIST_ATTACK = auto()
    COLONIST_MAX_HP = auto()
    # COLONIST_TERRAFORMING = auto()
    # COLONIST_UNCONTESTABLE = auto()
    #
    # TROOPER_ATTACK = auto()
    # TROOPER_ARMOR = auto()
    # TROOPER_REGEN = auto()
    # TROOPER_ENTRENCHMENT = auto()
    #
    # RANGER_ATTACK = auto()
    # RANGER_DISTANCE = auto()
    # RANGER_MOVEMENT = auto()
    # RANGER_UNCONTESTABLE = auto()
    #
    # GHOST_MOVEMENT = auto()
    # GHOST_STEALTH = auto()
    # GHOST_ANTI_COLONIST = auto()
    # GHOST_ANTI_PARTING_SHOTS = auto()


base_upgrades = {
    # Improves base resource yields for all buildings
    UpgradeType.RESOURCE_PRODUCTION_1: {
        "new_costs": {
            PieceType.BASE: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
        },
        "upgrade_price": (20, 20, 20),
        "tier": 1,
        "unlocks": [
            UpgradeType.RESOURCE_PRODUCTION_2
        ],
        "bought_by": PieceType.BASE
    },

    # Improves base resource yields for all buildings
    UpgradeType.RESOURCE_PRODUCTION_2: {
        "new_costs": {
            PieceType.BASE: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
        },
        "upgrade_price": (30, 30, 30),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },

    # Enables colonists to fight by giving them an attack rating
    UpgradeType.COLONIST_ATTACK: {
        "new_stat": {
            PieceType.COLONIST: {Attribute.ATTACK: 15}
        },
        "upgrade_price": (30, 30, 30),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # Gives colonists more max HP
    UpgradeType.COLONIST_MAX_HP: {
        "new_stat": {
            PieceType.COLONIST: {Attribute.MAX_HP: 20}
        },
        "upgrade_price": (20, 20, 20),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # COLONIST_TERRAFORMING
    # COLONIST_UNCONTESTABLE
}
