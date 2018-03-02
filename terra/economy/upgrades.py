from terra.piece.piecearchetype import PieceArchetype
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
    TROOPER_ATTACK = auto()
    TROOPER_ARMOR = auto()
    # TROOPER_REGEN = auto()
    # TROOPER_ENTRENCHMENT = auto()
    #
    RANGER_ATTACK = auto()
    RANGER_DISTANCE = auto()
    RANGER_MOVEMENT = auto()
    # RANGER_UNCONTESTABLE = auto()
    #
    GHOST_MOVEMENT = auto()
    # GHOST_STEALTH = auto()
    GHOST_ANTI_COLONIST = auto()
    # GHOST_ANTI_PARTING_SHOTS = auto()

    RESEARCH_GUARDIAN = auto()
    RESEARCH_BOLTCASTER = auto()
    RESEARCH_BANSHEE = auto()


# All upgrades available for purchase, including prereqs, price, effect, etc.
#   - new_stat: Adds the new stat to the existing stat. Allows for stacking buffs.
#   - new_type: Overwrites the attribute with the provided new attribute. Allows for mutating types.
#   - new_costs: Adds the new price-like stat to the existing price-like stat. Allows for stacking buffs.
#   - new_attack_multiplier: Sets the attack multiplier vs. the specified unit to the new value.
#   - new_buildable: Adds the provided piece(s) to the buildable list for the specified piece.
base_upgrades = {
    # Improves base resource yields for all buildings
    UpgradeType.RESOURCE_PRODUCTION_1: {
        "new_costs": {
            PieceType.BASE: {Attribute.RESOURCE_PRODUCTION: (5, 5, 5)},
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 0, 0)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 5, 0)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 0, 5)},
        },
        "upgrade_price": (4, 4, 4),
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
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (5, 0, 0)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 5, 0)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 0, 5)},
        },
        "upgrade_price": (6, 6, 6),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },

    # Enables colonists to fight by giving them an attack rating
    UpgradeType.COLONIST_ATTACK: {
        "new_stat": {
            PieceType.COLONIST: {Attribute.ATTACK: 15}
        },
        "upgrade_price": (2, 2, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # Gives colonists more max HP
    UpgradeType.COLONIST_MAX_HP: {
        "new_stat": {
            PieceType.COLONIST: {Attribute.MAX_HP: 20}
        },
        "upgrade_price": (2, 2, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # COLONIST_TERRAFORMING
    # COLONIST_UNCONTESTABLE

    # Gives troopers a stronger base attack
    UpgradeType.TROOPER_ATTACK: {
        "new_stat": {
            PieceType.TROOPER: {Attribute.ATTACK: 10}
        },
        "upgrade_price": (3, 4, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Gives troopers a bit of armor, giving them innate defense + damage reduction
    UpgradeType.TROOPER_ARMOR: {
        "new_stat": {
            PieceType.TROOPER: {Attribute.ARMOR: 1}
        },
        "upgrade_price": (4, 6, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # TROOPER_REGEN
    # TROOPER_ENTRENCHMENT

    # Gives Rangers a stronger base attack
    UpgradeType.RANGER_ATTACK: {
        "new_stat": {
            PieceType.RANGER: {Attribute.ATTACK: 10}
        },
        "upgrade_price": (4, 2, 3),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Increases both the max and min range that Rangers can conduct ranged attacks from.
    UpgradeType.RANGER_DISTANCE: {
        "new_stat": {
            PieceType.RANGER: {
                Attribute.MIN_RANGE: 1,
                Attribute.MAX_RANGE: 1,
            },
        },
        "upgrade_price": (6, 1, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Allows Rangers to move farther in one turn.
    UpgradeType.RANGER_MOVEMENT: {
        "new_stat": {
            PieceType.RANGER: {Attribute.MOVEMENT_RANGE: 1},
        },
        "upgrade_price": (2, 4, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # RANGER_UNCONTESTABLE

    # Allows Ghosts to move even farther in one turn.
    UpgradeType.GHOST_MOVEMENT: {
        "new_stat": {
            PieceType.GHOST: {Attribute.MOVEMENT_RANGE: 1},
        },
        "upgrade_price": (2, 3, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # GHOST_STEALTH
    # Ghosts now deal upsetting amounts of damage to Colonists, killing them in one hit.
    UpgradeType.GHOST_ANTI_COLONIST: {
        "new_attack_multiplier": {
            PieceType.GHOST: {
                PieceArchetype.WORKER: 25
            },
        },
        "upgrade_price": (2, 4, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # GHOST_ANTI_PARTING_SHOTS

    # Allows building Guardian units.
    UpgradeType.RESEARCH_GUARDIAN: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.GUARDIAN]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # Allows building Boltcaster units.
    UpgradeType.RESEARCH_BOLTCASTER: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.BOLTCASTER]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # Allows building Banshee units.
    UpgradeType.RESEARCH_BANSHEE: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.BANSHEE]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
}
