import pygame
from terra.piece.unit.unittype import UnitType

EVENT_TYPE = "event_type"
event_counter = 0


def define_event():
    global event_counter
    event_counter += 1
    return event_counter


# General action events
E_OPEN_MENU = define_event()
E_CLOSE_MENU = define_event()
E_OPEN_TILE_SELECTION = define_event()
E_SELECT_TILE = define_event()
E_CANCEL_TILE_SELECTION = define_event()
E_SELECT = define_event()
E_CANCEL = define_event()
E_OPEN_BUILD_MENU = define_event()
E_SELECT_BUILD_UNIT = define_event()
E_CANCEL_BUILD_UNIT = define_event()

# Notification events
E_UNIT_MOVED = define_event()
E_UNIT_RANGED_ATTACK = define_event()
E_PIECES_IN_CONFLICT = define_event()
E_CLEANUP = define_event()
E_INVALID_ORDER = define_event()
E_PIECE_DEAD = define_event()
E_BASE_DESTROYED = define_event()
E_PIECE_BUILT = define_event()

# Phase events
START_PHASE_START_TURN = define_event()
START_PHASE_ORDERS = define_event()
START_PHASE_EXECUTE_BUILD = define_event()
START_PHASE_EXECUTE_MOVE = define_event()
START_PHASE_EXECUTE_COMBAT = define_event()
START_PHASE_EXECUTE_RANGED = define_event()
START_PHASE_EXECUTE_SPECIAL = define_event()
E_NEXT_PHASE = define_event()

# Menu option events
MENU_CANCEL_ORDER = define_event()
MENU_MOVE = define_event()
MENU_RANGED_ATTACK = define_event()
MENU_BUILD_UNIT = define_event()
MENU_BUILD_CARBON_GENERATOR = define_event()
MENU_BUILD_MINERAL_GENERATOR = define_event()
MENU_BUILD_GAS_GENERATOR = define_event()
MENU_BUILD_BARRACKS = define_event()


def publish_game_event(event_type, data):
    data[EVENT_TYPE] = event_type
    event = pygame.event.Event(pygame.USEREVENT, data)
    pygame.event.post(event)


def is_event_type(event, *event_type):
    return event.type == pygame.USEREVENT and event.event_type in event_type
