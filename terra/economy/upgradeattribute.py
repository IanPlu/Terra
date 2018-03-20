from enum import Enum, auto


# Attributes common to most upgrades
class UpgradeAttribute(Enum):
    NEW_STAT = auto()
    NEW_TYPE = auto()
    NEW_ATTACK_MULTIPLIER = auto()
    NEW_BUILDABLE = auto()
    UPGRADE_PRICE = auto()
    TIER = auto()
    UNLOCKS = auto()
    BOUGHT_BY = auto()