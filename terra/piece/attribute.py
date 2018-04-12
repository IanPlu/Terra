from enum import Enum


# Attributes a piece has
class Attribute(Enum):
    # Basic attributes
    SUBTYPE = "subtype"                                 # Subtype - Building or Unit.
    ARCHETYPE = "archetype"                             # Class of piece, like RANGED or GENERATOR.
    MAX_HP = "max_hp"                                   # Max HP the unit has on creation.
    BUILDABLE_PIECES = "buildable_pieces"               # Pieces that can be built by this piece.
    PURCHASEABLE_UPGRADES = "purchaseable_upgrades"     # Upgrades that can be bought by this piece.
    ATTACK = "attack"                                   # Base attack rating for melee or ranged attacks.
    ATTACK_MULTIPLIER = "attack_multiplier"             # Flat multiplier for damage against each piece archetype.
    DAMAGE_TYPE = "damage_type"                         # Types of attacks this piece can make (melee or ranged).
    ARMOR = "armor"                                     # Innate damage reduction. One armor = 10% damage reduction.
    ENTRENCHMENT_MODIFIER = "entrenchment_modifier"     # Multiplier on entrenchment bonuses earned.
    MIN_RANGE = "min_range"                             # Minimum range for ranged attacks.
    MAX_RANGE = "max_range"                             # Maximum range for ranged attacks.
    MOVEMENT_TYPE = "movement_type"                     # Movement type. Affects what tiles it can traverse.
    MOVEMENT_RANGE = "movement_range"                   # Number of tiles this piece can move in a single turn.
    PRICE = "price"                                     # Price to build this piece.
    RESOURCE_PRODUCTION = "resource_production"         # How many resources this piece produces per turn.

    # Specialty attributes, used sparingly
    ARMOR_SHARE = "armor_share"                         # Amount of temp armor this piece applies to adjacent allies
    RANGED_AOE_MULTIPLIER = "ranged_aoe"                # Multiplier on ranged splash damage. 0 multiplier = 0 splash
    IGNORE_IMPEDANCE = "ignore_impedance"               # Whether this piece ignores movement blocking from enemy pieces
    CANT_ATTACK_BUILDINGS = "cant_attack_buildings"     # Whether this piece is unable to occupy buildings
    IGNORE_CONTESTING = "ignore_contesting"             # Whether this piece ignores enemies contesting its actions
    REGEN = "regen"                                     # How much health this piece regenerates at the start of turn
    TERRAFORMING = "terraforming"                       # Whether this piece is able to conduct the terraforming action
    MEDIC = "medic"                                     # How much health this piece heals allies at the start of turn
    ARMOR_PIERCING = "armor_piercing"                   # Whether this piece ignores enemy defensive bonuses
    AOE_ON_KILL = "aoe_on_kill"                         # Enemies this kills detonate in an AoE for this much damage
    KICKOFF = "kickoff"                                 # Whether this gets a movement range bonus from adjacent allies
    STEAL = "steal"                                     # How many resources this piece steals on killing an enemy
    AURA_DAMAGE = "aura_damage"                         # Multiplier on atk dealt to adjacent enemies on turn start
    HEAL_POWER = "heal_power"                           # How much this HP piece can heal itself with the heal action
    PORTAL = "portal"                                   # If true, acts as an adjacent tile for movement to the HQ.
    LIFESTEAL = "lifesteal"                             # What portion of damage dealt comes back as health (dmg * this)
    CRATERING = "cratering"                             # If true, ranged attacks will terraform-LOWER terrain
