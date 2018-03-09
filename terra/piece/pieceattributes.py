from enum import Enum

from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType


# Attributes a piece has
class Attribute(Enum):
    # Basic attributes
    SUBTYPE = "subtype"                                 # Subtype - Building or Unit.
    ARCHETYPE = "archetype"                             # Class of piece, like RANGED or GENERATOR.
    MAX_HP = "max_hp"                                   # Max HP the unit has on creation.
    BUILDABLE_PIECES = "buildable_pieces"               # Pieces that can be built by this piece.
    PURCHASEABLE_UPGRADES = "purchaseable_upgrades"     # Upgrades that can be bought by this piece.
    ATTACK = "attack"                                   # Base attack rating for melee or ranged attacks.
    ATTACK_MULTIPLIER = "attack_multiplier"             # Flat multiplier for damage against each piece archetype.
    DAMAGE_TYPE = "damage_type"                         # Types of attacks this piece can make (melee or ranged).
    ARMOR = "armor"                                     # Innate damage reduction. One armor = 10% damage reduction.
    ENTRENCHMENT_MODIFIER = "entrenchment_modifier"     # Multiplier on entrenchment bonuses earned.
    MIN_RANGE = "min_range"                             # Minimum range for ranged attacks.
    MAX_RANGE = "max_range"                             # Maximum range for ranged attacks.
    MOVEMENT_TYPE = "movement_type"                     # Movement type. Affects what tiles it can traverse.
    MOVEMENT_RANGE = "movement_range"                   # Number of tiles this piece can move in a single turn.
    PRICE = "price"                                     # Price to build this piece.
    RESOURCE_PRODUCTION = "resource_production"         # How many resources this piece produces per turn.

    # Specialty attributes, used sparingly
    ARMOR_SHARE = "armor_share"                         # Amount of temp armor this piece applies to adjacent allies
    RANGED_AOE_MULTIPLIER = "ranged_aoe"                # Multiplier on ranged splash damage. 0 multiplier = 0 splash
    IGNORE_IMPEDANCE = "ignore_impedance"               # Whether this piece ignores movement blocking from enemy pieces
    CANT_ATTACK_BUILDINGS = "cant_attack_buildings"     # Whether this piece is unable to occupy buildings
    IGNORE_CONTESTING = "ignore_contesting"             # Whether this piece ignores enemies contesting its actions
    REGEN = "regen"                                     # How much health this piece regenerates at the start of turn
    TERRAFORMING = "terraforming"                       # Whether this piece is able to conduct the terraforming action
    MEDIC = "medic"                                     # How much health this piece heals allies at the start of turn
    ARMOR_PIERCING = "armor_piercing"                   # Whether this piece ignores enemy defensive bonuses
    AOE_ON_KILL = "aoe_on_kill"                         # Enemies this kills detonate in an AoE for this much damage
    KICKOFF = "kickoff"                                 # Whether this gets a movement range bonus from adjacent allies
    STEAL = "steal"                                     # How many resources this piece steals on killing an enemy
    AURA_DAMAGE = "aura_damage"                         # Multiplier on atk dealt to adjacent enemies on turn start


# Base table of attributes for all units.
# Contains data on movement type, attack damage, abilities, etc.
base_piece_attributes = {
    PieceType.DEFAULT: {
        # Base attributes for all pieces.
        # When a piece doesn't have an attribute defined, it defaults to using these attributes.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.GROUND,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.ARMOR: 0,
        Attribute.ENTRENCHMENT_MODIFIER: 1,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 1,
        Attribute.PRICE: (0, 0, 0),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0),

        # Specialty
        Attribute.STEAL: 0,
        Attribute.ARMOR_SHARE: 0,
        Attribute.RANGED_AOE_MULTIPLIER: 0,
        Attribute.IGNORE_IMPEDANCE: False,
        Attribute.CANT_ATTACK_BUILDINGS: False,
        Attribute.IGNORE_CONTESTING: False,
        Attribute.REGEN: 0,
        Attribute.TERRAFORMING: False,
        Attribute.MEDIC: 0,
        Attribute.ARMOR_PIERCING: False,
        Attribute.AOE_ON_KILL: 0,
        Attribute.KICKOFF: False,
        Attribute.AURA_DAMAGE: 0,
    },

    # Tier 1 Units
    PieceType.COLONIST: {
        # Basic worker unit.
        # Colonists have limited combat capabilities and are mainly for building and gathering resources.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.WORKER,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [
            PieceType.BARRACKS,
            PieceType.TOWER,
            PieceType.TECHLAB,
            PieceType.CARBON_GENERATOR,
            PieceType.MINERAL_GENERATOR,
            PieceType.GAS_GENERATOR
        ],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 3,
        Attribute.PRICE: (2, 2, 2),
    },
    PieceType.TROOPER: {
        # General purpose close-range combat units.
        # Troopers excel at destroying buildings and Ghost units, and are good at forming a front line.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.GROUND,
        Attribute.MAX_HP: 100,
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1.5,

            # Buildings
            PieceArchetype.GENERATOR: 1.5,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (2, 3, 1),
    },
    PieceType.RANGER: {
        # Light units capable of a short ranged attack. They have no combat strength in melee.
        # Rangers are strong against Troopers and are able to focus down targets when in large numbers.
        # Rangers notably do very little damage to Ghosts.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.RANGED,
        Attribute.MAX_HP: 90,
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1.5,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 0.75,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.RANGED,
        Attribute.MIN_RANGE: 1,
        Attribute.MAX_RANGE: 2,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (3, 1, 2),
    },
    PieceType.GHOST: {
        # Basic harassment and mobility unit.
        # Strong against ranged units and colonists. They are not impeded by enemy units when moving.
        # Ghosts cannot attack enemy buildings-- they are strictly unit assassins.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.MOBILITY,
        Attribute.MAX_HP: 80,
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1.5,
            PieceArchetype.GROUND: 0.5,
            PieceArchetype.RANGED: 1.5,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 0,
            PieceArchetype.UTILITY: 0,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 3,
        Attribute.PRICE: (1, 2, 3),
        Attribute.IGNORE_IMPEDANCE: True,
        Attribute.CANT_ATTACK_BUILDINGS: True,
    },

    # Tier 2 Units
    PieceType.GUARDIAN: {
        # Defensive specialty unit.
        # Guardians excel at holding an area with their high defenses, and support nearby units with defensive buffs.
        # Notably weak when they're in motion and don't have entrenchment bonuses.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.GROUND,
        Attribute.MAX_HP: 80,
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 2,

            # Buildings
            PieceArchetype.GENERATOR: 1.2,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.ARMOR: 2,
        Attribute.ENTRENCHMENT_MODIFIER: 2,
        Attribute.MOVEMENT_TYPE: MovementType.HEAVY,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (4, 6, 2),
        # Specialty
        Attribute.ARMOR_SHARE: 1,
    },
    PieceType.BOLTCASTER: {
        # Ranged specialty unit.
        # Has a longer range than Rangers, but a wider blind spot. Boltcaster projectiles deal damage in an area,
        # with reduced damage to tiles adjacent to the target.
        # Notably brittle in direct combat, and has a small movement range.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.RANGED,
        Attribute.MAX_HP: 60,
        Attribute.ATTACK: 40,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1.5,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 0.75,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.RANGED,
        Attribute.MIN_RANGE: 3,
        Attribute.MAX_RANGE: 5,
        Attribute.MOVEMENT_TYPE: MovementType.HEAVY,
        Attribute.MOVEMENT_RANGE: 1,
        Attribute.PRICE: (6, 2, 4),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0),
        # Specialty
        Attribute.RANGED_AOE_MULTIPLIER: 0.75
    },
    PieceType.BANSHEE: {
        # Mobility specialty unit.
        # Extremely high movement range, and can traverse (but not end turn in) normally impassible terrain.
        # Very low health pool.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.ARCHETYPE: PieceArchetype.MOBILITY,
        Attribute.MAX_HP: 40,
        Attribute.ATTACK: 40,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 2,
            PieceArchetype.GROUND: 0.5,
            PieceArchetype.RANGED: 2,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 0,
            PieceArchetype.UTILITY: 0,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MOVEMENT_TYPE: MovementType.HOVER,
        Attribute.MOVEMENT_RANGE: 4,
        Attribute.PRICE: (2, 4, 6),
        Attribute.IGNORE_IMPEDANCE: True,
        Attribute.CANT_ATTACK_BUILDINGS: True,
    },

    # Buildings
    PieceType.BASE: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.UTILITY,
        Attribute.MAX_HP: 150,
        Attribute.BUILDABLE_PIECES: [PieceType.COLONIST],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (0, 0, 0),
        Attribute.RESOURCE_PRODUCTION: (3, 3, 3),
        Attribute.ARMOR: 1,
    },
    PieceType.CARBON_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.GENERATOR,
        Attribute.MAX_HP: 100,
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (1, 2, 2),
        Attribute.RESOURCE_PRODUCTION: (2, 0, 0)
    },
    PieceType.MINERAL_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.GENERATOR,
        Attribute.MAX_HP: 100,
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (2, 1, 2),
        Attribute.RESOURCE_PRODUCTION: (0, 2, 0)
    },
    PieceType.GAS_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.GENERATOR,
        Attribute.MAX_HP: 100,
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (2, 2, 1),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 2)
    },
    PieceType.BARRACKS: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.UTILITY,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [PieceType.TROOPER, PieceType.RANGER, PieceType.GHOST],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (5, 5, 5),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.TOWER: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.UTILITY,
        Attribute.MAX_HP: 50,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 10,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1.5,

            # Buildings
            PieceArchetype.GENERATOR: 0,
            PieceArchetype.UTILITY: 0,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (3, 3, 3),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0),
        Attribute.AURA_DAMAGE: 3,
        Attribute.ARMOR: 1,
    },
    PieceType.TECHLAB: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.ARCHETYPE: PieceArchetype.UTILITY,
        Attribute.MAX_HP: 50,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceArchetype.WORKER: 1,
            PieceArchetype.GROUND: 1,
            PieceArchetype.RANGED: 1,
            PieceArchetype.MOBILITY: 1,

            # Buildings
            PieceArchetype.GENERATOR: 1,
            PieceArchetype.UTILITY: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (2, 2, 2),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0),
    },
}
