from enum import Enum

from terra.battlephase import BattlePhase
from terra.effects.effecttype import EffectType
from terra.event import *
from terra.mainmenu.option import Option
from terra.piece.piecetype import PieceType


class Language(Enum):
    EN_US = "US English"


menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE: "Move",
        MENU_CANCEL_ORDER: "Wait",
        MENU_RANGED_ATTACK: "Ranged",
        MENU_BUILD_PIECE: "Build",
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

piece_name_strings = {
    Language.EN_US: {
        PieceType.COLONIST: "Colonist",
        PieceType.TROOPER: "Trooper",
        PieceType.RANGER: "Ranger",
        PieceType.GHOST: "Ghost",

        PieceType.BASE: "Base",
        PieceType.CARBON_GENERATOR: "Carbon Gen",
        PieceType.MINERAL_GENERATOR: "Mineral Gen",
        PieceType.GAS_GENERATOR: "Gas Gen",
        PieceType.BARRACKS: "Barracks",

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
        Option.QUIT: "Quit",
        Option.LOCAL: "Local Play",
        Option.NETWORK: "Network Play",
        Option.JOIN_GAME: "Join Game",
        Option.HOST_GAME: "Host Game",
        Option.NEW_NETWORK_GAME: "New Network Game",
        Option.LOAD_NETWORK_GAME: "Load Network Game"
    }
}
