from enum import Enum

from terra.battlephase import BattlePhase
from terra.effects.effecttype import EffectType
from terra.event import *
from terra.mainmenu.option import Option
from terra.piece.piecetype import PieceType
from terra.economy.upgrades import UpgradeType


class Language(Enum):
    EN_US = "US English"


menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE: "Move",
        MENU_CANCEL_ORDER: "Cancel Order",
        MENU_RANGED_ATTACK: "Ranged",
        MENU_BUILD_PIECE: "Build",
        MENU_PURCHASE_UPGRADE: "Upgrade",
        MENU_SUBMIT_TURN: "Submit Turn",
        MENU_SAVE_GAME: "Save Game",
        MENU_QUIT_BATTLE: "Quit Battle",
        MENU_SAVE_MAP: "Save Map",
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
        PieceType.DEFAULT: "Unknown",

        PieceType.COLONIST: "Colonist",
        PieceType.TROOPER: "Trooper",
        PieceType.RANGER: "Ranger",
        PieceType.GHOST: "Ghost",

        PieceType.GUARDIAN: "Guardian",
        PieceType.BOLTCASTER: "Boltcaster",
        PieceType.BANSHEE: "Banshee",

        # PieceType.TITAN: "Titan",
        # PieceType.EARTHRENDER: "Earthrender",
        # PieceType.DEMON: "Demon",

        PieceType.BASE: "Base",
        PieceType.CARBON_GENERATOR: "Carbon Gen",
        PieceType.MINERAL_GENERATOR: "Mineral Gen",
        PieceType.GAS_GENERATOR: "Gas Gen",
        PieceType.BARRACKS: "Barracks",
        # PieceType.TOWER: "Tower",
        # PieceType.WAYSTATION: "Waystation",
        # PieceType.TECHLAB: "Tech Lab",

    }
}

upgrade_name_strings = {
    Language.EN_US: {
        UpgradeType.RESOURCE_PRODUCTION_1: "Harvest+",
        UpgradeType.RESOURCE_PRODUCTION_2: "Harvest++",

        UpgradeType.COLONIST_ATTACK: "(C) Attack+",
        UpgradeType.COLONIST_MAX_HP: "(C) HP+",
        # UpgradeType.COLONIST_TERRAFORMING: "(C) Terraforming",
        # UpgradeType.COLONIST_UNCONTESTABLE: "(C) Covert Ops",

        UpgradeType.TROOPER_ATTACK: "(T) Attack+",
        UpgradeType.TROOPER_ARMOR: "(T) Armor+",
        # UpgradeType.TROOPER_REGEN: "(T) Regen",
        # UpgradeType.TROOPER_ENTRENCHMENT: "(T) Entrench+",

        UpgradeType.RANGER_ATTACK: "(R) Attack+",
        UpgradeType.RANGER_DISTANCE: "(R) Range+",
        UpgradeType.RANGER_MOVEMENT: "(R) Move+",
        # UpgradeType.RANGER_UNCONTESTABLE: "(R) Ironsights",

        UpgradeType.GHOST_MOVEMENT: "(G) Move+",
        # UpgradeType.GHOST_STEALTH: "(G) Stealth",
        UpgradeType.GHOST_ANTI_COLONIST: "(G) Assassin",
        # UpgradeType.GHOST_ANTI_PARTING_SHOTS: "(G) Escapist",

        UpgradeType.RESEARCH_GUARDIAN: "Unlock Unit",
        UpgradeType.RESEARCH_BOLTCASTER: "Unlock Unit",
        UpgradeType.RESEARCH_BANSHEE: "Unlock Unit",
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
        Option.LOAD_NETWORK_GAME: "Load Network Game",
        Option.NEW_MAP: "New Map",
        Option.LOAD_MAP: "Load Map"
    }
}
