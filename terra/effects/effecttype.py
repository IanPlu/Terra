from enum import Enum, auto


# Identifiers for different animated effects.
class EffectType(Enum):
    ALERT = auto()
    PIECE_DESTROYED = auto()
    NO_MONEY = auto()
    ORDER_BLOCKED = auto()
    ARMOR_GRANTED = auto()
    HP_HEALED = auto()
    DUPLICATE_UPGRADE = auto()
    DEATH_AOE = auto()
    MONEY_LOST = auto()
    PIECE_CONFLICT = auto()
