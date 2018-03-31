from enum import Enum, auto


# Menu options
class Option(Enum):
    # Main menu options
    START = auto()
    NEW_GAME = auto()
    LOAD_GAME = auto()
    LEVEL_EDITOR = auto()
    SETTINGS = auto()
    QUIT = auto()
    LOCAL = auto()
    NETWORK = auto()
    HOST_GAME = auto()
    JOIN_GAME = auto()
    NEW_NETWORK_GAME = auto()
    LOAD_NETWORK_GAME = auto()
    NEW_MAP = auto()
    LOAD_MAP = auto()
    SAVE_SETTINGS = auto()

    # Piece selection options
    MENU_CANCEL_ORDER = auto()
    MENU_MOVE = auto()
    MENU_RANGED_ATTACK = auto()
    MENU_BUILD_PIECE = auto()
    MENU_PURCHASE_UPGRADE = auto()
    MENU_RAISE_TILE = auto()
    MENU_LOWER_TILE = auto()
    MENU_DEMOLISH_SELF = auto()

    # Pause menu options
    MENU_SUBMIT_TURN = auto()
    MENU_REVISE_TURN = auto()
    MENU_SAVE_GAME = auto()
    MENU_QUIT_BATTLE = auto()
    MENU_CONCEDE = auto()

    # Level editor options
    MENU_SAVE_MAP = auto()
    MENU_FILL_WITH_CURRENT_TILE = auto()
    MENU_MIRROR_X = auto()
    MENU_MIRROR_Y = auto()
