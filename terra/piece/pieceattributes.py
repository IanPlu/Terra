from enum import Enum

from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType


# Attributes a piece has
class Attribute(Enum):
    SUBTYPE = "subtype"
    MAX_HP = "max_hp"
    BUILDABLE_PIECES = "buildable_pieces"
    PURCHASEABLE_UPGRADES = "purchaseable_upgrades"
    ATTACK = "attack"
    ATTACK_MULTIPLIER = "attack_multiplier"
    DAMAGE_TYPE = "damage_type"
    ARMOR = "armor"
    MIN_RANGE = "min_range"
    MAX_RANGE = "max_range"
    MOVEMENT_TYPE = "movement_type"
    MOVEMENT_RANGE = "movement_range"
    PRICE = "price"
    RESOURCE_PRODUCTION = "resource_production"


# Base table of attributes for all units.
# Contains data on movement type, attack damage, abilities, etc.
base_piece_attributes = {
    # Units
    PieceType.COLONIST: {
        # Basic worker unit.
        # Colonists have limited combat capabilities and are mainly for building and gathering resources.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [
            PieceType.BARRACKS,
            PieceType.CARBON_GENERATOR,
            PieceType.MINERAL_GENERATOR,
            PieceType.GAS_GENERATOR
        ],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 3,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.TROOPER: {
        # General purpose close-range combat units.
        # Troopers excel at destroying buildings and Ghost units, and are good at forming a front line.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1.5,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1.5,
            PieceType.MINERAL_GENERATOR: 1.5,
            PieceType.GAS_GENERATOR: 1.5,
            PieceType.BARRACKS: 1.5,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (10, 15, 5),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.RANGER: {
        # Light units capable of a short ranged attack. They have no combat strength in melee.
        # Rangers are strong against Troopers and are able to focus down targets when in large numbers.
        # Rangers notably do very little damage to Ghosts.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1.5,
            PieceType.RANGER: 1,
            PieceType.GHOST: 0.5,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.RANGED,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 1,
        Attribute.MAX_RANGE: 2,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (15, 5, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.GHOST: {
        # Basic harassment and mobility unit.
        # Strong against ranged units and colonists. They are not impeded by enemy units when moving.
        # Ghosts cannot attack enemy buildings-- they are strictly unit assassins.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 70,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 30,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1.5,
            PieceType.TROOPER: 0.5,
            PieceType.RANGER: 1.5,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 0,
            PieceType.CARBON_GENERATOR: 0,
            PieceType.MINERAL_GENERATOR: 0,
            PieceType.GAS_GENERATOR: 0,
            PieceType.BARRACKS: 0,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GHOST,
        Attribute.MOVEMENT_RANGE: 3,
        Attribute.PRICE: (5, 10, 15),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    # Buildings
    PieceType.BASE: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [PieceType.COLONIST],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (0, 0, 0),
        Attribute.RESOURCE_PRODUCTION: (20, 20, 20)
    },
    PieceType.CARBON_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (5, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (10, 0, 0)
    },
    PieceType.MINERAL_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (10, 5, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 10, 0)
    },
    PieceType.GAS_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (10, 10, 5),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 10)
    },
    PieceType.BARRACKS: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 100,
        Attribute.BUILDABLE_PIECES: [PieceType.TROOPER, PieceType.RANGER, PieceType.GHOST],
        Attribute.PURCHASEABLE_UPGRADES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.ARMOR: 0,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (25, 25, 25),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    }
}
