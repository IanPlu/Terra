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
    # TITAN = 8
    # EARTHRENDER = 9
    # DEMON = 10

    # Buildings
    BASE = 8
    CARBON_GENERATOR = 9
    MINERAL_GENERATOR = 10
    GAS_GENERATOR = 11
    BARRACKS = 12
    TOWER = 13
    # WAYSTATION = 17
    TECHLAB = 14
