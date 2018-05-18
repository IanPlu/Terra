from enum import Enum, auto


# Constants for upgrade names.
class UpgradeType(Enum):
    # General tech + unit research
    RESOURCE_PRODUCTION = auto()
    BUILDING_ARMOR = auto()

    RESEARCH_GUARDIAN = auto()
    RESEARCH_BOLTCASTER = auto()
    RESEARCH_BANSHEE = auto()

    RESEARCH_TITAN = auto()
    RESEARCH_EARTHRENDER = auto()
    RESEARCH_DEMON = auto()

    # Colonist
    COLONIST_ATTACK = auto()
    COLONIST_MAX_HP = auto()
    COLONIST_MINING = auto()
    COLONIST_UNCONTESTABLE = auto()

    # Trooper
    TROOPER_ATTACK = auto()
    TROOPER_ARMOR = auto()
    TROOPER_REGEN = auto()
    TROOPER_COST = auto()

    # Ranger
    RANGER_ATTACK = auto()
    RANGER_DISTANCE = auto()
    RANGER_MOVEMENT = auto()
    RANGER_UNCONTESTABLE = auto()

    # Ghost
    GHOST_MOVEMENT = auto()
    GHOST_ATTACK = auto()
    GHOST_ANTI_COLONIST = auto()
    GHOST_STEAL = auto()

    # Guardian
    GUARDIAN_ARMOR_SHARE = auto()
    GUARDIAN_ARMOR = auto()
    GUARDIAN_MEDIC = auto()

    # Boltcaster
    BOLTCASTER_UNCONTESTABLE = auto()
    BOLTCASTER_RANGE = auto()
    BOLTCASTER_AP_ROUNDS = auto()

    # Banshee
    BANSHEE_SABOTAGE = auto()
    BANSHEE_STRIKEFORMATION = auto()
    BANSHEE_LURK = auto()

    # Titan
    TITAN_LIFESTEAL = auto()
    TITAN_AURA_DAMAGE = auto()

    # Earthrender
    EARTHRENDER_CHAIN = auto()
    EARTHRENDER_DAMAGE = auto()

    # Demon
    DEMON_CAN_BUILD = auto()
    DEMON_BASE_ATTACK = auto()


unit_research = {
    UpgradeType.RESEARCH_GUARDIAN,
    UpgradeType.RESEARCH_BOLTCASTER,
    UpgradeType.RESEARCH_BANSHEE,
    UpgradeType.RESEARCH_TITAN,
    UpgradeType.RESEARCH_EARTHRENDER,
    UpgradeType.RESEARCH_DEMON,
}
