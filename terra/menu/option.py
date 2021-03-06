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
    TUTORIAL = auto()
    CAMPAIGN = auto()
    NEW_CAMPAIGN_GAME = auto()
    LOAD_CAMPAIGN_GAME = auto()

    # Lobby options
    LEAVE_LOBBY = auto()
    START_BATTLE = auto()
    AI_PERSONALITY = auto()
    ADD_HUMAN = auto()
    REMOVE_HUMAN = auto()

    # Piece selection options
    MENU_CANCEL_ORDER = auto()
    MENU_MOVE = auto()
    MENU_RANGED_ATTACK = auto()
    MENU_BUILD_PIECE = auto()
    MENU_PURCHASE_UPGRADE = auto()
    MENU_MINE_TILE = auto()
    MENU_DEMOLISH_SELF = auto()
    MENU_HEAL_SELF = auto()

    # Pause menu options
    MENU_SUBMIT_TURN = auto()
    MENU_REVISE_TURN = auto()
    MENU_SAVE_GAME = auto()
    MENU_QUIT_BATTLE = auto()
    MENU_CONCEDE = auto()
    MENU_SWAP_ACTIVE_PLAYER = auto()

    # Level editor options
    MENU_SAVE_MAP = auto()
    MENU_FILL_WITH_CURRENT_TILE = auto()
    MENU_DESTROY_ALL_PIECES = auto()
    MENU_MIRROR_X = auto()
    MENU_MIRROR_Y = auto()


contestable_options = [
    Option.MENU_RANGED_ATTACK,
    Option.MENU_BUILD_PIECE,
    Option.MENU_PURCHASE_UPGRADE,
    Option.MENU_MINE_TILE,
    Option.MENU_HEAL_SELF,
]

