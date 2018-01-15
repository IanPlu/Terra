import pygame
from enum import Enum


class Team(Enum):
    RED = 0
    BLUE = 1


class BattlePhase(Enum):
    START_TURN = 0
    ORDERS = 1
    EXECUTE_BUILD = 2
    EXECUTE_MOVE = 3
    EXECUTE_COMBAT = 4
    EXECUTE_RANGED = 5
    EXECUTE_SPECIAL = 6


RESOLUTION_WIDTH = 264
RESOLUTION_HEIGHT = 264
