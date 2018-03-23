from enum import Enum, auto


# Main menu options
class Option(Enum):
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
