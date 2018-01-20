from terra.constants import *
from terra.event import *
from enum import Enum


class Language(Enum):
    EN_US = "US English"


menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE: "MOVE",
        MENU_CANCEL_ORDER: "WAIT",
        MENU_RANGED_ATTACK: "RANGED",
        MENU_BUILD_UNIT: "BUILD",
        MENU_BUILD_CARBON_GENERATOR: "HARVEST",
        MENU_BUILD_MINERAL_GENERATOR: "HARVEST",
        MENU_BUILD_GAS_GENERATOR: "HARVEST",
        MENU_BUILD_BARRACKS: "BARRACKS"
    }
}

phase_strings = {
    Language.EN_US: {
        BattlePhase.START_TURN: "Start Turn",
        BattlePhase.ORDERS: "Issue Orders",
        BattlePhase.EXECUTE_BUILD: "Build",
        BattlePhase.EXECUTE_MOVE: "Move",
        BattlePhase.EXECUTE_COMBAT: "Combat",
        BattlePhase.EXECUTE_RANGED: "Ranged",
        BattlePhase.EXECUTE_SPECIAL: "Special"
    }
}

unit_name_strings = {
    Language.EN_US: {
        UnitType.UNIT: "Unknown",
        UnitType.COLONIST: "Colonist",
        UnitType.TROOPER: "Trooper",
        UnitType.RANGER: "Ranger",
        UnitType.GHOST: "Ghost"
    }
}