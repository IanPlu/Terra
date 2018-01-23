from enum import Enum


class MovementType(Enum):
    NONE = 0
    GROUND = 1
    GHOST = 2
    BUILD_BARRACKS = 3
    BUILD_GENERATOR = 4
