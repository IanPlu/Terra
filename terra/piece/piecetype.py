from enum import Enum, auto


# Possible piece types.
class PieceType(Enum):
    DEFAULT = auto()

    # Tier 1 Units
    COLONIST = auto()
    TROOPER = auto()
    RANGER = auto()
    GHOST = auto()

    # Tier 2 Units
    GUARDIAN = auto()
    BOLTCASTER = auto()
    # BANSHEE = auto()

    # Tier 3 Units
    # TITAN = auto()
    # EARTHRENDER = auto()
    # DEMON = auto()

    # Buildings
    BASE = auto()
    CARBON_GENERATOR = auto()
    MINERAL_GENERATOR = auto()
    GAS_GENERATOR = auto()
    BARRACKS = auto()
    # TOWER = auto()
    # WAYSTATION = auto()
    # TECHLAB = auto()
