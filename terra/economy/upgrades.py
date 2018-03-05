from enum import Enum, auto

from terra.piece.movementtype import MovementType
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.pieceattributes import Attribute
from terra.piece.piecetype import PieceType


class UpgradeType(Enum):
    # General tech + unit research
    RESOURCE_PRODUCTION_1 = auto()
    RESOURCE_PRODUCTION_2 = auto()
    RESEARCH_GUARDIAN = auto()
    RESEARCH_BOLTCASTER = auto()
    RESEARCH_BANSHEE = auto()

    # Colonist
    COLONIST_ATTACK = auto()
    COLONIST_MAX_HP = auto()
    COLONIST_TERRAFORMING = auto()
    COLONIST_UNCONTESTABLE = auto()

    # Trooper
    TROOPER_ATTACK = auto()
    TROOPER_ARMOR = auto()
    TROOPER_REGEN = auto()
    TROOPER_ENTRENCHMENT = auto()

    # Ranger
    RANGER_ATTACK = auto()
    RANGER_DISTANCE = auto()
    RANGER_MOVEMENT = auto()
    RANGER_UNCONTESTABLE = auto()

    # Ghost
    GHOST_MOVEMENT = auto()
    GHOST_ATTACK = auto()
    GHOST_ANTI_COLONIST = auto()
    GHOST_STEAL = auto()

    # Guardian
    GUARDIAN_ENTRENCHMENT = auto()
    GUARDIAN_ARMOR = auto()
    GUARDIAN_MEDIC = auto()

    # Boltcaster
    BOLTCASTER_UNCONTESTABLE = auto()
    BOLTCASTER_RANGE = auto()
    BOLTCASTER_AP_ROUNDS = auto()

    # Banshee
    BANSHEE_SABOTAGE = auto()
    BANSHEE_STRIKEFORMATION = auto()
    BANSHEE_LURK = auto()


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
            PieceType.BASE: {Attribute.RESOURCE_PRODUCTION: (1, 1, 1)},
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (1, 0, 0)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 1, 0)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 0, 1)},
        },
        "upgrade_price": (5, 5, 5),
        "tier": 1,
        "unlocks": [
            UpgradeType.RESOURCE_PRODUCTION_2
        ],
        "bought_by": PieceType.BASE
    },
    # Improves base resource yields for all buildings
    UpgradeType.RESOURCE_PRODUCTION_2: {
        "new_costs": {
            PieceType.BASE: {Attribute.RESOURCE_PRODUCTION: (1, 1, 1)},
            PieceType.CARBON_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (1, 0, 0)},
            PieceType.MINERAL_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 1, 0)},
            PieceType.GAS_GENERATOR: {Attribute.RESOURCE_PRODUCTION: (0, 0, 1)},
        },
        "upgrade_price": (8, 8, 8),
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
    # Enables Colonists to conduct RAISE and LOWER actions, changing a tile around them to a different type
    UpgradeType.COLONIST_TERRAFORMING: {
        "new_type": {
            PieceType.COLONIST: {Attribute.TERRAFORMING: True}
        },
        "upgrade_price": (5, 5, 5),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },
    # Colonists now cannot be contested, allowing them to always complete build orders (unless they die)
    UpgradeType.COLONIST_UNCONTESTABLE: {
        "new_type": {
            PieceType.COLONIST: {Attribute.IGNORE_CONTESTING: True}
        },
        "upgrade_price": (2, 6, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BASE
    },

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
        "new_type": {
            PieceType.TROOPER: {Attribute.ARMOR: 1}
        },
        "upgrade_price": (4, 6, 2),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Troopers now regenerate a small amount of health at the start of each turn
    UpgradeType.TROOPER_REGEN: {
        "new_type": {
            PieceType.TROOPER: {Attribute.REGEN: 10}
        },
        "upgrade_price": (4, 4, 8),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Doubles the entrenchment bonuses Troopers gain.
    UpgradeType.TROOPER_ENTRENCHMENT: {
        "new_type": {
            PieceType.TROOPER: {Attribute.ENTRENCHMENT_MODIFIER: 2}
        },
        "upgrade_price": (4, 6, 4),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },

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
    # Allows Rangers to ignore enemies contesting their tile, ensuring their ranged attacks execute (if they survive)
    UpgradeType.RANGER_UNCONTESTABLE: {
        "new_type": {
            PieceType.RANGER: {Attribute.IGNORE_CONTESTING: True}
        },
        "upgrade_price": (4, 6, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },

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
    # Gives Ghosts a stronger base attack
    UpgradeType.GHOST_ATTACK: {
        "new_stat": {
            PieceType.GHOST: {Attribute.ATTACK: 10}
        },
        "upgrade_price": (2, 3, 4),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
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
    # Ghosts now steal resources when killing enemies
    UpgradeType.GHOST_STEAL: {
        "new_type": {
            PieceType.GHOST: {Attribute.STEAL: 1}
        },
        "upgrade_price": (4, 4, 6),
        "tier": 1,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },

    # Allows building Guardian units.
    UpgradeType.RESEARCH_GUARDIAN: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.GUARDIAN]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [
            UpgradeType.GUARDIAN_ENTRENCHMENT,
            UpgradeType.GUARDIAN_ARMOR,
            UpgradeType.GUARDIAN_MEDIC
        ],
        "bought_by": PieceType.BASE
    },
    # Allows building Boltcaster units.
    UpgradeType.RESEARCH_BOLTCASTER: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.BOLTCASTER]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [
            UpgradeType.BOLTCASTER_UNCONTESTABLE,
            UpgradeType.BOLTCASTER_RANGE,
            UpgradeType.BOLTCASTER_AP_ROUNDS
        ],
        "bought_by": PieceType.BASE
    },
    # Allows building Banshee units.
    UpgradeType.RESEARCH_BANSHEE: {
        "new_buildable": {
            PieceType.BARRACKS: [PieceType.BANSHEE]
        },
        "upgrade_price": (6, 6, 6),
        "tier": 1,
        "unlocks": [
            UpgradeType.BANSHEE_SABOTAGE,
            UpgradeType.BANSHEE_STRIKEFORMATION,
            UpgradeType.BANSHEE_LURK
        ],
        "bought_by": PieceType.BASE
    },

    # Grants even greater entrenchment bonuses to Guardians.
    UpgradeType.GUARDIAN_ENTRENCHMENT: {
        "new_type": {
            PieceType.GUARDIAN: {Attribute.ENTRENCHMENT_MODIFIER: 3}
        },
        "upgrade_price": (6, 8, 6),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Grants even greater armor bonuses to Guardians.
    UpgradeType.GUARDIAN_ARMOR: {
        "new_type": {
            PieceType.GUARDIAN: {Attribute.ARMOR: 3}
        },
        "upgrade_price": (6, 8, 4),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Guardians now heal adjacent allies for a small amount each turn.
    UpgradeType.GUARDIAN_MEDIC: {
        "new_type": {
            PieceType.GUARDIAN: {Attribute.MEDIC: 10}
        },
        "upgrade_price": (8, 4, 8),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },

    # Boltcasters ignore enemies contesting their tile, ensuring their ranged attacks execute (if they survive)
    UpgradeType.BOLTCASTER_UNCONTESTABLE: {
        "new_type": {
            PieceType.BOLTCASTER: {Attribute.IGNORE_CONTESTING: True}
        },
        "upgrade_price": (6, 8, 8),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Boltcasters can now shoot targets even further away.
    UpgradeType.BOLTCASTER_RANGE: {
        "new_stat": {
            PieceType.BOLTCASTER: {Attribute.MAX_RANGE: 1},
        },
        "upgrade_price": (8, 2, 4),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Boltcaster shots now ignore armor and defensive bonuses.
    UpgradeType.BOLTCASTER_AP_ROUNDS: {
        "new_type": {
            PieceType.BOLTCASTER: {Attribute.ARMOR_PIERCING: True}
        },
        "upgrade_price": (8, 4, 8),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },

    # Banshees now trigger an AoE explosion on killing blows, centered on the target.
    UpgradeType.BANSHEE_SABOTAGE: {
        "new_type": {
            PieceType.BANSHEE: {Attribute.AOE_ON_KILL: 30}
        },
        "upgrade_price": (2, 2, 8),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Banshees now gain additional movement range for starting the turn adjacent to allies, per ally.
    UpgradeType.BANSHEE_STRIKEFORMATION: {
        "new_type": {
            PieceType.BANSHEE: {Attribute.KICKOFF: True}
        },
        "upgrade_price": (2, 4, 6),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    },
    # Banshees gain the Flying movement type, allowing them to end turn on impassible terrain like SEAs.
    UpgradeType.BANSHEE_LURK: {
        "new_type": {
            PieceType.BANSHEE: {Attribute.MOVEMENT_TYPE: MovementType.FLYING}
        },
        "upgrade_price": (2, 4, 4),
        "tier": 2,
        "unlocks": [],
        "bought_by": PieceType.BARRACKS
    }

}
