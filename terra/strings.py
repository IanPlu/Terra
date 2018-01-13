from terra.constants import *
from terra.event import *
from enum import Enum


class Language(Enum):
    EN_US = "US English"


menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE_N: "MOVE N",
        MENU_MOVE_E: "MOVE E",
        MENU_MOVE_S: "MOVE S",
        MENU_MOVE_W: "MOVE W",
        MENU_CANCEL_ORDER: "WAIT"
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
