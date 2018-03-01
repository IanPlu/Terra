from enum import Enum, auto


class EffectType(Enum):
    ALERT = auto()
    PIECE_DESTROYED = auto()
    NO_MONEY = auto()
    ORDER_BLOCKED = auto()
    ARMOR_GRANTED = auto()
