from enum import Enum


# Possible types of tiles. Determines movement capability, building placement, and so on.
class TileType(Enum):
    SEA = 1
    GRASS = 2
    WOODS = 3
    RESOURCE = 4
    MOUNTAIN = 5
    COAST = 6
    HILL = 7
    METEOR = 8
