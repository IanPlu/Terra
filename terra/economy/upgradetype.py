from enum import Enum, auto


class UpgradeType(Enum):
    # General tech + unit research
    RESOURCE_PRODUCTION_1 = auto()
    RESOURCE_PRODUCTION_2 = auto()
    RESEARCH_GUARDIAN = auto()
    RESEARCH_BOLTCASTER = auto()
    RESEARCH_BANSHEE = auto()

    # Colonist
    COLONIST_ATTACK = auto()
    COLONIST_MAX_HP = auto()
    COLONIST_TERRAFORMING = auto()
    COLONIST_UNCONTESTABLE = auto()

    # Trooper
    TROOPER_ATTACK = auto()
    TROOPER_ARMOR = auto()
    TROOPER_REGEN = auto()
    TROOPER_ENTRENCHMENT = auto()

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
    GUARDIAN_ENTRENCHMENT = auto()
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