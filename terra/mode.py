from enum import Enum, auto


class Mode(Enum):
    MAIN_MENU = auto()
    BATTLE = auto()
    EDIT = auto()
    RESULTS = auto()
    LOBBY = auto()
    NETWORK_LOBBY = auto()
    NETWORK_BATTLE = auto()
