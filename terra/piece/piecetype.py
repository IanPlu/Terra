from enum import Enum


# Possible piece types.
# Values give that type an ID, as well as a subtype -- BUILDING or UNIT.
class PieceType(Enum):
    COLONIST = 0
    TROOPER = 1
    RANGER = 2
    GHOST = 3

    BASE = 4
    CARBON_GENERATOR = 5
    MINERAL_GENERATOR = 6
    GAS_GENERATOR = 7
    BARRACKS = 8
