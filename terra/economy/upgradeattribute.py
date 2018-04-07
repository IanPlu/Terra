from enum import Enum, auto


# Attributes common to most upgrades. Names for the price, unlockables, effects of an upgrade, and so on.
#   - NEW_STAT: Adds the new stat to the existing stat. Allows for stacking buffs.
#   - NEW_TYPE: Overwrites the attribute with the provided new attribute. Allows for mutating types.
#   - NEW_ATTACK_MULTIPLIER: Sets the attack multiplier vs. the specified unit to the new value.
#   - NEW_BUILDABLE: Adds the provided piece(s) to the buildable list for the specified piece.
#   - TIER: Depth in the tech tree. Tier 0 upgrades are available from the start, without any prereqs.
#   - UNLOCKS: List of other upgrades that will be unlocked upon researching this upgrade.
#   - BOUGHT_BY: What piece is able to research this upgrade as an action. Usually a building.
class UpgradeAttribute(Enum):
    NEW_STAT = auto()
    NEW_TYPE = auto()
    NEW_ATTACK_MULTIPLIER = auto()
    NEW_BUILDABLE = auto()
    UPGRADE_PRICE = auto()
    TIER = auto()
    UNLOCKS = auto()
    BOUGHT_BY = auto()