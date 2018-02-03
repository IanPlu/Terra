from enum import Enum

from terra.battlephase import BattlePhase
from terra.effects.effecttype import EffectType
from terra.event import *
from terra.mainmenu.option import Option
from terra.piece.unit.unittype import UnitType


class Language(Enum):
    EN_US = "US English"


menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE: "Move",
        MENU_CANCEL_ORDER: "Wait",
        MENU_RANGED_ATTACK: "Ranged",
        MENU_BUILD_UNIT: "Build",
        MENU_BUILD_CARBON_GENERATOR: "Harvest",
        MENU_BUILD_MINERAL_GENERATOR: "Harvest",
        MENU_BUILD_GAS_GENERATOR: "Harvest",
        MENU_BUILD_BARRACKS: "Barracks",
        MENU_SUBMIT_TURN: "Submit Turn",
        MENU_SAVE_GAME: "Save Game",
        MENU_QUIT_BATTLE: "Quit Battle"
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
        Option.LOAD_GAME: "Load Game",
        Option.LEVEL_EDITOR: "Level Editor",
        Option.SETTINGS: "Settings",
        Option.QUIT: "Quit"
    }
}
