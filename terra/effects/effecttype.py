from enum import Enum


class EffectType(Enum):
    ALERT = 0
    PIECE_DESTROYED = 1
    NO_MONEY = 2
    ORDER_BLOCKED = 3
