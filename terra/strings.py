from enum import Enum

from terra.turn.battlephase import BattlePhase
from terra.economy.upgradetype import UpgradeType
from terra.event.event import EventType
from terra.managers.statmanager import Stat
from terra.menu.option import Option
from terra.piece.attribute import Attribute
from terra.piece.movementtype import MovementType
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecetype import PieceType
from terra.resources.assets import light_color, dark_color
from terra.settings import Setting
from terra.team.team import Team
from terra.util.drawingutil import draw_text, draw_multiline_text


class Language(Enum):
    EN_US = "US English"


LANGUAGE = Language.EN_US

menu_option_strings = {
    Language.EN_US: {
        Option.MENU_MOVE: "Move",
        Option.MENU_CANCEL_ORDER: "Cancel Order",
        Option.MENU_RANGED_ATTACK: "Ranged",
        Option.MENU_BUILD_PIECE: "Build",
        Option.MENU_PURCHASE_UPGRADE: "Upgrade",
        Option.MENU_SUBMIT_TURN: "Submit Turn",
        Option.MENU_REVISE_TURN: "Revise Turn",
        Option.MENU_SAVE_GAME: "Save Game",
        Option.MENU_QUIT_BATTLE: "Quit",
        Option.MENU_SAVE_MAP: "Save Map",
        Option.MENU_RAISE_TILE: "Raise Tile",
        Option.MENU_LOWER_TILE: "Lower Tile",
        Option.MENU_DEMOLISH_SELF: "Demolish",
        Option.MENU_HEAL_SELF: "Repair",
        Option.MENU_FILL_WITH_CURRENT_TILE: "Fill Map",
        Option.MENU_CONCEDE: "Concede",
        Option.MENU_MIRROR_X: "Mirror (H)",
        Option.MENU_MIRROR_Y: "Mirror (V)",
        Option.MENU_SWAP_ACTIVE_PLAYER: "Swap Player",
    }
}

menu_help_strings = {
    Language.EN_US: {
        # Normal Menu Options
        Option.MENU_MOVE: "* Order this piece to move to a new location.",
        Option.MENU_CANCEL_ORDER: "* Cancel current order and do nothing this turn.",
        Option.MENU_RANGED_ATTACK: "* Conduct a ranged attack on a tile. Allies are not harmed.",
        Option.MENU_BUILD_PIECE: "* Build a new piece on an adjacent tile.",
        Option.MENU_PURCHASE_UPGRADE: "* Purchase an upgrade, which takes effect on the start of next turn.",
        Option.MENU_SUBMIT_TURN: "* Submit your turn. Once all turns are submitted, orders are executed.",
        Option.MENU_REVISE_TURN: "* Cancel turn submission and make changes to your orders.",
        Option.MENU_SAVE_GAME: "* Save the current battle. You can resume it later.",
        Option.MENU_QUIT_BATTLE: "* Quit this battle.",
        Option.MENU_SAVE_MAP: "* Save this map design to a file.",
        Option.MENU_RAISE_TILE: "* Terraform an adjacent tile. Seas -> Coasts -> Plains -> Hills -> Mountains.",
        Option.MENU_LOWER_TILE: "* Terraform an adjacent tile. Mountains -> Hills -> Plains -> Coasts -> Seas.",
        Option.MENU_DEMOLISH_SELF: "* Destroy this piece at the end of the turn, freeing space for other pieces later.",
        Option.MENU_HEAL_SELF: "* Order this piece to heal itself a small amount.",
        Option.MENU_FILL_WITH_CURRENT_TILE: "* Fill the map design with the currently selected tile type.",
        Option.MENU_CONCEDE: "* Concede the game. Your opponent wins!",
        Option.MENU_SWAP_ACTIVE_PLAYER: "* Swap the currently active player in hotseat mode, without passing the turn.",

        # Pieces
        PieceType.COLONIST: "* Colonists are workers with little combat ability, but can harvest resources and build "
                            "buildings. Build orders are canceled if an enemy contests this unit's tile. ",
        PieceType.TROOPER: "* Troopers are ground forces with balanced stats that form a strong front line. "
                           "Notably weak to ranged attacks.",
        PieceType.RANGER: "* Rangers are fairly fragile units that can conduct long-range attacks without being "
                          "counter attacked. They cannot defend themselves in melee and are notably weak to "
                          "high-mobility units. Their ranged attack is canceled if an enemy contests their tile. ",
        PieceType.GHOST: "* Ghosts are high-mobility units with low defenses. They are not impeded by enemy units when "
                         "moving around, and can slip behind enemy lines. Cannot attack or contest buildings, and are "
                         "notably weak in direct combat.",

        PieceType.GUARDIAN: "* Guardians are defensive specialty ground forces. They excel at holding ground with their"
                            " high defenses, and support nearby allies with defensive buffs. Notably weak when caught"
                            " on the move, due to their low HP.",
        PieceType.BOLTCASTER: "* Boltcasters are a high-caliber ranged unit. They have a much longer range than "
                              "Rangers, but also have a larger blind spot and low mobility. Their ranged attacks also "
                              "deal damage to tiles adjacent to their target.",
        PieceType.BANSHEE: "* Banshees are a high-mobility specialty unit. They have a very high movement range, and "
                           "can traverse (but not end the turn in) normally impassible terrain. Like Ghosts, they're "
                           "not impeded by enemies when moving. Notably low health pool.",

        PieceType.TITAN: "* Titans are defensive super units. They have a wealth of health and armor, and provide"
                         " healing and bonus armor to adjacent allies every turn. Adjacent enemies take damage as well.",
        PieceType.EARTHRENDER: "* Earthrenders are ranged super units. They have an extremely far effective range, deal"
                               " damage in an area, and cannot be interrupted when firing. ",
        PieceType.DEMON: "* Demons are mobility super units. They have a very high movement range, and ignore terrain. "
                         "Like Ghosts, they can't attack buildings. Demons function as a portal-- allies can "
                         "travel to a Demon's tile as if it were adjacent to the Base. ",

        PieceType.BASE: "* Your Base is the only building capable of producing Colonists, and can research non-combat "
                        "unit upgrades. If destroyed, you lose!",
        PieceType.GENERATOR: "* Generators harvest resources from Resource tiles each turn.",
        PieceType.BARRACKS: "* Barracks produce combat units, and can research upgrades to your combat units.",
        PieceType.TOWER: "* Towers are immobile defensive structures. They damage all adjacent enemies at the start of "
                         "each turn, if they're not contested. Has a weak melee attack for defense.",
        PieceType.TECHLAB: "* Tech Labs are able to research new tiers of units. Additionally, they're a second place "
                           "to purchase upgrades of all types, including upgrades normally bought at the Base. "
                           "Tech Labs heal adjacent allies for a small amount each turn.",

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
        UpgradeType.RESEARCH_BANSHEE: "* Allows building Banshees at Barracks. Banshees are high mobility specialty "
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

        UpgradeType.RESEARCH_TITAN: "* Allows building Titans at Barracks. Titans are defensive super units.",
        UpgradeType.RESEARCH_EARTHRENDER: "* Allows building Earthrenders at Barracks. Earthrenders are ranged "
                                          "super units.",
        UpgradeType.RESEARCH_DEMON: "* Allows building Demons at Barracks. Demons are mobility super units.",

        UpgradeType.TITAN_LIFESTEAL: "* Titans now heal for a portion of damage they deal with their normal attack. ",
        UpgradeType.TITAN_AURA_DAMAGE: "* Titans now deal more damage to adjacent enemies at the end of turn. ",

        UpgradeType.EARTHRENDER_CRATERING: "* Earthrenders now LOWER the tile they target with ranged attacks. ",
        UpgradeType.EARTHRENDER_DAMAGE: "* Earthrenders now do significantly more damage, and have a longer range. ",

        UpgradeType.DEMON_CAN_BUILD: "* Demons now gain the ability to construct T1 units. ",
        UpgradeType.DEMON_BASE_ATTACK: "* Demons gain the ability to attack buildings. ",
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

team_name_strings = {
    Language.EN_US: {
        Team.RED: "RED",
        Team.BLUE: "BLUE",
        Team.GREEN: "GREEN",
        Team.YELLOW: "YELLOW",
        Team.NONE: "???",
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

        PieceType.TITAN: "Titan",
        PieceType.EARTHRENDER: "Earthrender",
        PieceType.DEMON: "Demon",

        PieceType.BASE: "Base",
        PieceType.GENERATOR: "Generator",
        PieceType.BARRACKS: "Barracks",
        PieceType.TOWER: "Tower",
        PieceType.TECHLAB: "Tech Lab",

    }
}

upgrade_name_strings = {
    Language.EN_US: {
        UpgradeType.RESOURCE_PRODUCTION_1: "Harvest+",
        UpgradeType.RESOURCE_PRODUCTION_2: "Harvest++",

        UpgradeType.COLONIST_ATTACK: "[C] Attack+",
        UpgradeType.COLONIST_MAX_HP: "[C] HP+",
        UpgradeType.COLONIST_TERRAFORMING: "[C] Terraform",
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

        UpgradeType.RESEARCH_TITAN: "Unlock Unit",
        UpgradeType.RESEARCH_EARTHRENDER: "Unlock Unit",
        UpgradeType.RESEARCH_DEMON: "Unlock Unit",

        UpgradeType.TITAN_LIFESTEAL: "[Ti] Flux Engine",
        UpgradeType.TITAN_AURA_DAMAGE: "[Ti] Devastation",

        UpgradeType.EARTHRENDER_CRATERING: "[Ea] Meteor",
        UpgradeType.EARTHRENDER_DAMAGE: "[Ea] Long Gun",

        UpgradeType.DEMON_CAN_BUILD: "[De] Summoning",
        UpgradeType.DEMON_BASE_ATTACK: "[De] Regicide",
    }
}

notification_strings = {
    Language.EN_US: {
        EventType.E_INVALID_MOVE_ORDERS: "Orders result in stacked pieces",
        EventType.E_INVALID_BUILD_ORDERS: "Not enough resources for orders",
        EventType.E_INVALID_UPGRADE_ORDERS: "Can't buy the same upgrade twice",
        EventType.NETWORK_CLIENT_CONNECTED: "{} connected",
        EventType.NETWORK_CLIENT_DISCONNECTED: "{} disconnected",
        EventType.NETWORK_CONNECTED_TO_HOST: "Connected to host",
        EventType.NETWORK_DISCONNECTED_FROM_HOST: "Disconnected from host",
    }
}

main_menu_strings = {
    Language.EN_US: {
        Option.START: "Main Menu",
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
        Option.LOAD_MAP: "Load Map",
        Option.SAVE_SETTINGS: "Apply Settings",

        Option.LEAVE_LOBBY: "Leave Lobby",
        Option.START_BATTLE: "Start Battle",
    }
}

attribute_label_strings = {
    Language.EN_US: {
        Attribute.SUBTYPE: "Subtype",
        Attribute.ARCHETYPE: "Class",
        Attribute.MAX_HP: "Max HP",
        Attribute.BUILDABLE_PIECES: "Buildable Pieces",
        Attribute.ATTACK: "Attack",
        Attribute.ATTACK_MULTIPLIER: "Attack Multiplier",
        Attribute.DAMAGE_TYPE: "Damage Type",
        Attribute.ARMOR: "Armor",
        Attribute.ENTRENCHMENT_MODIFIER: "Entrenchment Modifier",
        Attribute.MIN_RANGE: "Minimum Range",
        Attribute.MAX_RANGE: "Maximum Range",
        Attribute.MOVEMENT_TYPE: "Movement Type",
        Attribute.MOVEMENT_RANGE: "Movement Range",
        Attribute.PRICE: "Price",
        Attribute.RESOURCE_PRODUCTION: "Resource Production",

        Attribute.ARMOR_SHARE: "Armor Share",
        Attribute.RANGED_AOE_MULTIPLIER: "Ranged AOE Multiplier",
        Attribute.IGNORE_IMPEDANCE: "Ignore Impedance",
        Attribute.CANT_ATTACK_BUILDINGS: "Can't Attack Buildings",
        Attribute.IGNORE_CONTESTING: "Ignore Enemies Contesting",
        Attribute.REGEN: "Regeneration",
        Attribute.TERRAFORMING: "Can Terraform",
        Attribute.MEDIC: "Heal Allies",
        Attribute.ARMOR_PIERCING: "Pierces Armor",
        Attribute.AOE_ON_KILL: "AOE Damage on Kill",
        Attribute.KICKOFF: "+1 Movement Per Ally",
        Attribute.STEAL: "Resources Stolen on Kill",
        Attribute.AURA_DAMAGE: "Aura Damage",
        Attribute.HEAL_POWER: "Healing Power",
        Attribute.PORTAL: "Acts as a Portal",
        Attribute.LIFESTEAL: "Lifesteal",
        Attribute.CRATERING: "Ranged attacks Terraform",
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

label_strings = {
    Language.EN_US: {
        "IP_INPUT": "Enter ip address to connect to:",
        "NICKNAME_INPUT": "Enter a new nickname:",
        "MAPNAME_INPUT": "Enter new map name:",
        "RESULTS_PROMPT": "Press the CONFIRM key to continue",
        "OPEN_TEAM": "-OPEN-",
    }
}

# Strings that are required to be used with string.format() before use
formatted_strings = {
    Language.EN_US: {
        "NEW_TURN_MESSAGE": "TURN {}",
        "RESULTS_HEADER": "{} team won!",
        "QUANTITY": "{}x",

        Setting.SCREEN_SCALE: "Screen Scale: {}x",
        Setting.SFX_VOLUME: "Sound Volume: {}%",
        Setting.BGM_VOLUME: "Music Volume: {}%",
        Setting.NICKNAME: "Nickname: '{}'",
        Setting.ANIMATION_SPEED: "Animation Speed: {}x",

        Stat.TILES_MOVED: "Tiles Moved: {}",
        Stat.RANGED_ATTACKS_MADE: "Ranged Attacks: {}",
        Stat.PIECE_CONFLICTS: "Piece Conflicts: {}",
        Stat.PIECES_LOST: "Pieces Lost: {}",
        Stat.PIECES_BUILT: "Pieces Built: {}",
        Stat.UPGRADES_RESEARCHED: "Upgrades Researched: {}",
    }
}

# Cached copies of text surfaces
text_objects = {}
multiline_text_objects = {}


# Convenience method to return a string for the current language
def get_string(string_type, string_name):
    return string_type[LANGUAGE][string_name]


# Return a surface containing the provided string
def __get_cached_text__(string, light=True):
    color = light_color if light else dark_color
    background = dark_color if light else light_color

    if text_objects.get((string, color), None):
        return text_objects[(string, color)]
    else:
        new_text = draw_text(string, color, background)
        text_objects[(string, color)] = new_text
        return new_text


# Return a surface containing the provided string.
def get_text(string_type, string_name, light=True):
    return __get_cached_text__(string_type[LANGUAGE][string_name], light)


# Return a surface containing the provided FORMATTED string.
def get_formatted_text(string_type, string_name, light=True, *inputs):
    return __get_cached_text__(string_type[LANGUAGE][string_name].format(*inputs), light)


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

