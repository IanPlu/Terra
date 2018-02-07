from terra.team import Team
from terra.piece.piecetype import PieceType
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType
from enum import Enum


# Attributes a piece has
class Attribute(Enum):
    SUBTYPE = "subtype"
    MAX_HP = "max_hp"
    BUILDABLE_PIECES = "buildable_pieces"
    ATTACK = "attack"
    ATTACK_MULTIPLIER = "attack_multiplier"
    DAMAGE_TYPE = "damage_type"
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
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [
            PieceType.BARRACKS,
            PieceType.CARBON_GENERATOR,
            PieceType.MINERAL_GENERATOR,
            PieceType.GAS_GENERATOR
        ],
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
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 1,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 1,
            PieceType.GHOST: 2,
            # Buildings
            PieceType.BASE: 2,
            PieceType.CARBON_GENERATOR: 2,
            PieceType.MINERAL_GENERATOR: 2,
            PieceType.GAS_GENERATOR: 2,
            PieceType.BARRACKS: 2,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.RANGER: {
        # Light units capable of a short ranged attack. They have no combat strength in melee.
        # Rangers are strong against Troopers and are able to focus down targets when in large numbers.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 1,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 2,
            PieceType.RANGER: 1,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.RANGED,
        Attribute.MIN_RANGE: 1,
        Attribute.MAX_RANGE: 2,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 2,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    PieceType.GHOST: {
        # Basic harassment and mobility unit.
        # Strong against ranged units and colonists. They are not impeded by enemy units when moving.
        Attribute.SUBTYPE: PieceSubtype.UNIT,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 1,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 2,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.MELEE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GROUND,
        Attribute.MOVEMENT_RANGE: 3,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    },
    # Buildings
    PieceType.BASE: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [PieceType.COLONIST],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (0, 0, 0),
        Attribute.RESOURCE_PRODUCTION: (20, 20, 20)
    },
    PieceType.CARBON_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (10, 0, 0)
    },
    PieceType.MINERAL_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 10, 0)
    },
    PieceType.GAS_GENERATOR: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.GENERATOR,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (10, 10, 10),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 10)
    },
    PieceType.BARRACKS: {
        Attribute.SUBTYPE: PieceSubtype.BUILDING,
        Attribute.MAX_HP: 10,
        Attribute.BUILDABLE_PIECES: [PieceType.TROOPER, PieceType.RANGER, PieceType.GHOST],
        Attribute.ATTACK: 0,
        Attribute.ATTACK_MULTIPLIER: {
            # Units
            PieceType.COLONIST: 1,
            PieceType.TROOPER: 1,
            PieceType.RANGER: 2,
            PieceType.GHOST: 1,
            # Buildings
            PieceType.BASE: 1,
            PieceType.CARBON_GENERATOR: 1,
            PieceType.MINERAL_GENERATOR: 1,
            PieceType.GAS_GENERATOR: 1,
            PieceType.BARRACKS: 1,
        },
        Attribute.DAMAGE_TYPE: DamageType.NONE,
        Attribute.MIN_RANGE: 0,
        Attribute.MAX_RANGE: 0,
        Attribute.MOVEMENT_TYPE: MovementType.BUILDING,
        Attribute.MOVEMENT_RANGE: 0,
        Attribute.PRICE: (30, 30, 30),
        Attribute.RESOURCE_PRODUCTION: (0, 0, 0)
    }
}

# Actual up to date attribute tables, specific to each team.
# Upgrades can mutate these values over the course of the game.
# TODO: Move this to the team manager
piece_attributes = {}

# Propagate base values to each team
for team in Team:
    piece_attributes[team] = base_piece_attributes
