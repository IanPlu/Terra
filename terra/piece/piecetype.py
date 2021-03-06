from enum import Enum


# Possible piece types.
class PieceType(Enum):
    DEFAULT = 0

    # Tier 1 Units
    COLONIST = 1
    TROOPER = 2
    RANGER = 3
    GHOST = 4

    # Tier 2 Units
    GUARDIAN = 5
    BOLTCASTER = 6
    BANSHEE = 7

    # Tier 3 Units
    TITAN = 8
    EARTHRENDER = 9
    DEMON = 10

    # Buildings
    BASE = 11
    GENERATOR = 12
    BARRACKS = 13
    TOWER = 14
    TECHLAB = 15


ALL_UNITS = frozenset([
    PieceType.COLONIST,
    PieceType.TROOPER,
    PieceType.RANGER,
    PieceType.GHOST,

    PieceType.GUARDIAN,
    PieceType.BOLTCASTER,
    PieceType.BANSHEE,

    PieceType.TITAN,
    PieceType.EARTHRENDER,
    PieceType.DEMON,
])
ALL_BUILDINGS = frozenset([
    PieceType.BASE,
    PieceType.GENERATOR,
    PieceType.BARRACKS,
    PieceType.TOWER,
    PieceType.TECHLAB,
])