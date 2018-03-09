from enum import Enum

from terra.battlephase import BattlePhase
from terra.economy.upgrades import UpgradeType
from terra.event import *
from terra.mainmenu.option import Option
from terra.piece.piecetype import PieceType
from terra.util.drawingutil import draw_text, draw_multiline_text
from terra.resources.assets import light_color, dark_color
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.movementtype import MovementType


class Language(Enum):
    EN_US = "US English"


LANGUAGE = Language.EN_US

menu_option_strings = {
    Language.EN_US: {
        MENU_MOVE: "Move",
        MENU_CANCEL_ORDER: "Cancel Order",
        MENU_RANGED_ATTACK: "Ranged",
        MENU_BUILD_PIECE: "Build",
        MENU_PURCHASE_UPGRADE: "Upgrade",
        MENU_SUBMIT_TURN: "Submit Turn",
        MENU_REVISE_TURN: "Revise Turn",
        MENU_SAVE_GAME: "Save Game",
        MENU_QUIT_BATTLE: "Quit",
        MENU_SAVE_MAP: "Save Map",
        MENU_RAISE_TILE: "Raise Tile",
        MENU_LOWER_TILE: "Lower Tile",
    }
}

menu_help_strings = {
    Language.EN_US: {
        # Normal Menu Options
        MENU_MOVE: "* Order this piece to move to a new location.",
        MENU_CANCEL_ORDER: "* Cancel current order and do nothing this turn.",
        MENU_RANGED_ATTACK: "* Conduct a ranged attack on a tile. Allies are not harmed.",
        MENU_BUILD_PIECE: "* Build a new piece on an adjacent tile.",
        MENU_PURCHASE_UPGRADE: "* Purchase an upgrade, which takes effect on the start of next turn.",
        MENU_SUBMIT_TURN: "* Submit your turn. Once all turns are submitted, orders are executed.",
        MENU_REVISE_TURN: "* Cancel turn submission and make changes to your orders.",
        MENU_SAVE_GAME: "* Save the current battle. You can resume it later.",
        MENU_QUIT_BATTLE: "* Quit this battle.",
        MENU_SAVE_MAP: "* Save this map design to a file.",
        MENU_RAISE_TILE: "* Terraform an adjacent tile. Seas -> Coasts -> Plains -> Hills -> Mountains.",
        MENU_LOWER_TILE: "* Terraform an adjacent tile. Mountains -> Hills -> Plains -> Coasts -> Seas.",

        # Pieces
        PieceType.COLONIST: "* Colonists are workers with little combat ability, but can harvest resources.",
        PieceType.TROOPER: "* Troopers are ground forces with balanced stats that form a strong front line. "
                           "Notably weak to ranged attacks.",
        PieceType.RANGER: "* Rangers are fairly fragile units that can conduct long-range attacks without being "
                          "counter attacked. They cannot defend themselves in melee and are notably weak to "
                          "high-mobility units.",
        PieceType.GHOST: "* Ghosts are high-mobility units with low defenses. They are not impeded by enemy units when "
                         "moving around, and can slip behind enemy lines. Cannot attack buildings, and are notably weak"
                         " in direct combat.",

        PieceType.GUARDIAN: "* Guardians are defensive specialty ground forces. They excel at holding ground with their"
                            " high defenses, and support nearby allies with defensive buffs. Notably weak when caught"
                            " on the move, due to their low HP.",
        PieceType.BOLTCASTER: "* Boltcasters are a high-caliber ranged unit. They have a much longer range than "
                              "Rangers, but also have a larger blind spot and low mobility. Their ranged attacks also "
                              "deal damage to tiles adjacent to their target.",
        PieceType.BANSHEE: "* Banshees are a high-mobility specialty unit. They have a very high movement range, and "
                           "can traverse (but not end the turn in) normally impassible terrain. Like Ghosts, they're "
                           "not impeded by enemies when moving. Notably low health pool-- don't get hit.",

        # PieceType.TITAN: "Titan",
        # PieceType.EARTHRENDER: "Earthrender",
        # PieceType.DEMON: "Demon",

        PieceType.BASE: "* Your Base is the only building capable of producing Colonists, and can research non-combat "
                        "unit upgrades. New units can be researched here. If destroyed, you lose!",
        PieceType.GENERATOR: "* Generators harvest resources from Resource tiles each turn.",
        PieceType.BARRACKS: "* Barracks produce combat units, and can research upgrades to your combat units.",
        PieceType.TOWER: "* Towers are immobile defensive structures. They damage all adjacent enemies at the start of "
                         "each turn, if they're not contested. Has a weak melee attack for defense.",
        # PieceType.WAYSTATION: "Waystation",
        PieceType.TECHLAB: "* Tech Labs are able to research new tiers of units. Additionally, they're a second place "
                           "to purchase upgrades of all types, including upgrades normally bought at the Base. "
                           "Tech Labs also heal adjacent allies for a small amount each turn.",

        # Upgrades
        UpgradeType.RESOURCE_PRODUCTION_1: "* Generators now produce +1 resource per turn.",
        UpgradeType.RESOURCE_PRODUCTION_2: "* Generators now produce an additional +1 resource per turn.",

        UpgradeType.COLONIST_ATTACK: "* Colonists now deal a small amount of damage in direct combat.",
        UpgradeType.COLONIST_MAX_HP: "* Colonists now have a higher max HP.",
        UpgradeType.COLONIST_TERRAFORMING: "* Colonists can now conduct terraforming actions, changing nearby terrain."
                                           "Can be used offensively by putting harmful terrain under enemies, or "
                                           "defensively to create chokepoints and cut off routes.",
        UpgradeType.COLONIST_UNCONTESTABLE: "* Colonists now cannot be interrupted during their special actions by "
                                            "enemies contesting their tile.",

        UpgradeType.TROOPER_ATTACK: "* Troopers now deal more damage in direct combat.",
        UpgradeType.TROOPER_ARMOR: "* Troopers gain a small amount of armor, reducing damage dealt to them.",
        UpgradeType.TROOPER_REGEN: "* Troopers now regenerate a small amount of health at the start of each turn.",
        UpgradeType.TROOPER_ENTRENCHMENT: "* Troopers now gain double the benefit from entrenchment.",

        UpgradeType.RANGER_ATTACK: "* Rangers now deal more damage in ranged attacks.",
        UpgradeType.RANGER_DISTANCE: "* Rangers gain more range on their ranged attacks, but their blind spot "
                                     "increases.",
        UpgradeType.RANGER_MOVEMENT: "* Rangers can now move farther in one turn.",
        UpgradeType.RANGER_UNCONTESTABLE: "* Rangers can no longer be interrupted during ranged attacks by enemies "
                                          "contesting their tile.",

        UpgradeType.GHOST_MOVEMENT: "* Ghosts can now move farther in one turn.",
        UpgradeType.GHOST_ATTACK: "* Ghosts now deal more damage in direct combat.",
        UpgradeType.GHOST_ANTI_COLONIST: "* Ghosts now deal upsetting damage to Colonists, killing them in one hit.",
        UpgradeType.GHOST_STEAL: "* Ghosts now steal some resources when killing enemies.",

        UpgradeType.RESEARCH_GUARDIAN: "* Allows building Guardians at Barracks. Guardians are powerful defensive "
                                       "ground forces.",
        UpgradeType.RESEARCH_BOLTCASTER: "* Allows building Boltcasters at Barracks. Boltcasters are powerful ranged "
                                         "specialty units.",
        UpgradeType.RESEARCH_BANSHEE: "* Allows building Banshees at Barracks. Banshees are high mobility specialty"
                                      "units.",

        UpgradeType.GUARDIAN_ENTRENCHMENT: "* Guardians now benefit even more from entrenchment bonuses.",
        UpgradeType.GUARDIAN_ARMOR: "* Guardians gain even greater armor bonuses, increasing their defense.",
        UpgradeType.GUARDIAN_MEDIC: "* Guardians now heal adjacent allies for a small amount at the start of each "
                                    "turn.",

        UpgradeType.BOLTCASTER_UNCONTESTABLE: "* Boltcasters can no longer be interrupted during ranged attacks by "
                                              "enemies contesting their tile.",
        UpgradeType.BOLTCASTER_RANGE: "* Boltcasters gain more range on their ranged attacks.",
        UpgradeType.BOLTCASTER_AP_ROUNDS: "* Boltcasters now ignore armor and defensive bonuses on their ranged "
                                          "attacks.",

        UpgradeType.BANSHEE_SABOTAGE: "* Banshees now trigger an explosion when killing enemies, dealing damage to "
                                      "enemies adjacent to the target. This effect can chain.",
        UpgradeType.BANSHEE_STRIKEFORMATION: "* Banshees now gain additional movement range for each adjacent ally.",
        UpgradeType.BANSHEE_LURK: "* Banshees are now able to move and end turn on all terrain, including normally "
                                  "impassible terrain like Seas or Mountains.",
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
        PieceType.GENERATOR: "Generator",
        PieceType.BARRACKS: "Barracks",
        PieceType.TOWER: "Tower",
        # PieceType.WAYSTATION: "Waystation",
        PieceType.TECHLAB: "Tech Lab",

    }
}

upgrade_name_strings = {
    Language.EN_US: {
        UpgradeType.RESOURCE_PRODUCTION_1: "Harvest+",
        UpgradeType.RESOURCE_PRODUCTION_2: "Harvest++",

        UpgradeType.COLONIST_ATTACK: "[C] Attack+",
        UpgradeType.COLONIST_MAX_HP: "[C] HP+",
        UpgradeType.COLONIST_TERRAFORMING: "[C] Terraforming",
        UpgradeType.COLONIST_UNCONTESTABLE: "[C] Covert Ops",

        UpgradeType.TROOPER_ATTACK: "[T] Attack+",
        UpgradeType.TROOPER_ARMOR: "[T] Armor+",
        UpgradeType.TROOPER_REGEN: "[T] Regen",
        UpgradeType.TROOPER_ENTRENCHMENT: "[T] Entrench+",

        UpgradeType.RANGER_ATTACK: "[R] Attack+",
        UpgradeType.RANGER_DISTANCE: "[R] Range+",
        UpgradeType.RANGER_MOVEMENT: "[R] Move+",
        UpgradeType.RANGER_UNCONTESTABLE: "[R] Ironsights",

        UpgradeType.GHOST_MOVEMENT: "[Gh] Move+",
        UpgradeType.GHOST_ATTACK: "[Gh] Attack+",
        UpgradeType.GHOST_ANTI_COLONIST: "[Gh] Assassin",
        UpgradeType.GHOST_STEAL: "[Gh] Steal",

        UpgradeType.RESEARCH_GUARDIAN: "Unlock Unit",
        UpgradeType.RESEARCH_BOLTCASTER: "Unlock Unit",
        UpgradeType.RESEARCH_BANSHEE: "Unlock Unit",

        UpgradeType.GUARDIAN_ENTRENCHMENT: "[Gu] Entrench+",
        UpgradeType.GUARDIAN_ARMOR: "[Gu] Armor+",
        UpgradeType.GUARDIAN_MEDIC: "[Gu] Medic",

        UpgradeType.BOLTCASTER_UNCONTESTABLE: "[Bo] Ironsights",
        UpgradeType.BOLTCASTER_RANGE: "[Bo] Range+",
        UpgradeType.BOLTCASTER_AP_ROUNDS: "[Bo] AP Rounds",

        UpgradeType.BANSHEE_SABOTAGE: "[Ba] Sabotage",
        UpgradeType.BANSHEE_STRIKEFORMATION: "[Ba] Strike",
        UpgradeType.BANSHEE_LURK: "[Ba] Lurk",
    }
}

notification_strings = {
    Language.EN_US: {
        E_INVALID_MOVE_ORDERS: "Orders result in stacked pieces",
        E_INVALID_BUILD_ORDERS: "Not enough resources for orders",
        E_INVALID_UPGRADE_ORDERS: "Can't buy the same upgrade twice",
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

attribute_value_strings = {
    Language.EN_US: {
        MovementType.GROUND: "Ground",
        MovementType.HEAVY: "Heavy",
        MovementType.HOVER: "Hover",
        MovementType.FLYING: "Flying",
        MovementType.BUILDING: "Building",
        MovementType.GENERATOR: "Building",

        PieceArchetype.WORKER: "Worker",
        PieceArchetype.GROUND: "Ground",
        PieceArchetype.RANGED: "Ranged",
        PieceArchetype.MOBILITY: "Mobility",
        PieceArchetype.GENERATOR: "Generator",
        PieceArchetype.UTILITY: "Utility",
    }
}

# Cached copies of text surfaces
text_objects = {}
multiline_text_objects = {}


# Return a surface containing the provided string.
def get_text(string_type, string_name, light=True):
    string = string_type[LANGUAGE][string_name]
    color = light_color if light else dark_color
    background = dark_color if light else light_color

    if text_objects.get((string, color), None):
        return text_objects[(string, color)]
    else:
        new_text = draw_text(string, color, background)
        text_objects[(string, color)] = new_text
        return new_text


# Return a surface containing the provided string, broken out over multiple lines as appropriate.
def get_multiline_text(string_type, string_name, light=True, width=192, height=192):
    string = string_type[LANGUAGE][string_name]
    color = light_color if light else dark_color
    background = dark_color if light else light_color

    if multiline_text_objects.get((string, color, width, height), None):
        return multiline_text_objects[(string, color, width, height)]
    else:
        new_text = draw_multiline_text(string, color, background, width, height)
        multiline_text_objects[(string, color, width, height)] = new_text
        return new_text

