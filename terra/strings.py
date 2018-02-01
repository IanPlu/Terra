from terra.constants import *
from terra.event import *
from terra.effects.effecttype import EffectType
from terra.mainmenu.option import Option
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

notification_strings = {
    Language.EN_US: {
        EffectType.ALERT: "Orders result in stacked pieces",
        EffectType.NO_MONEY: "Not enough resources for orders",
    }
}

main_menu_strings = {
    Language.EN_US: {
        Option.START: "Start",
        Option.NEW_GAME: "New Game",
        Option.LEVEL_EDITOR: "Level Editor",
        Option.SETTINGS: "Settings",
        Option.QUIT: "Quit"
    }
}
