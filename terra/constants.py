import pygame
from enum import Enum


class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


class Team(Enum):
    RED = 0
    BLUE = 1


RESOLUTION_WIDTH = 240
RESOLUTION_HEIGHT = 240


# TODO: Figure out a better mechanism for tracking event offsets than doing it by hand
# General action events
E_OPEN_MENU = pygame.USEREVENT + 1
E_CLOSE_MENU = pygame.USEREVENT + 2
E_SELECT = pygame.USEREVENT + 3
E_CANCEL = pygame.USEREVENT + 4
E_EXECUTE_ORDERS = pygame.USEREVENT + 5

# Menu option events
MENU_MOVE_N = pygame.USEREVENT + 11
MENU_MOVE_E = pygame.USEREVENT + 12
MENU_MOVE_S = pygame.USEREVENT + 13
MENU_MOVE_W = pygame.USEREVENT + 14
MENU_CANCEL_ORDER = pygame.USEREVENT + 15
