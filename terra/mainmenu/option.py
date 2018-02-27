from enum import Enum


# Main menu options
class Option(Enum):
    START = 0
    NEW_GAME = 1
    LOAD_GAME = 2
    LEVEL_EDITOR = 3
    SETTINGS = 4
    QUIT = 5
    LOCAL = 6
    NETWORK = 7
    HOST_GAME = 8
    JOIN_GAME = 9
    NEW_NETWORK_GAME = 10
    LOAD_NETWORK_GAME = 11
    NEW_MAP = 12
    LOAD_MAP = 13
