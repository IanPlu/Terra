from enum import Enum


# What class of damage this unit does.
class DamageType(Enum):
    NONE = 0
    MELEE = 1
    RANGED = 2
