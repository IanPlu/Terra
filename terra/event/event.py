from enum import Enum, auto
from pygame import USEREVENT
from pygame.event import Event, post

EVENT_TYPE = "event_type"
FROM_NETWORK = "from_network"


# Identifiers for various event objects.
# TODO: Formalize what parameters belong to each event
class EventType(Enum):
    # General action events
    E_OPEN_MENU = auto()
    E_CLOSE_MENU = auto()
    E_OPEN_TILE_SELECTION = auto()
    E_SELECT_TILE = auto()
    E_CANCEL_TILE_SELECTION = auto()
    E_SELECT = auto()
    E_CANCEL = auto()
    E_OPEN_BUILD_MENU = auto()
    E_SELECT_BUILD_UNIT = auto()
    E_CANCEL_BUILD_UNIT = auto()
    E_OPEN_UPGRADE_MENU = auto()
    E_SELECT_UPGRADE = auto()
    E_CANCEL_UPGRADE = auto()
    E_CLOSE_DETAILBOX = auto()

    E_SUBMIT_TURN = auto()
    E_CANCEL_TURN = auto()
    E_TURN_SUBMITTED = auto()
    E_CANCEL_TURN_SUBMITTED = auto()
    E_ALL_TURNS_SUBMITTED = auto()
    E_CONCEDE = auto()
    E_SAVE_GAME = auto()
    E_QUIT_BATTLE = auto()
    E_BATTLE_OVER = auto()
    E_EXIT_RESULTS = auto()
    E_START_BATTLE = auto()
    E_START_NETWORK_BATTLE = auto()
    E_EXIT_LOBBY = auto()
    E_NETWORKING_ERROR = auto()
    E_SWAP_ACTIVE_PLAYER = auto()

    E_ALL_TEAMS_FILLED = auto()
    E_TEAM_LEFT = auto()

    # Notification events
    E_UNIT_MOVED = auto()
    E_UNIT_RANGED_ATTACK = auto()
    E_PIECES_IN_CONFLICT = auto()
    E_CLEANUP = auto()
    E_PIECE_DEAD = auto()
    E_BASE_DESTROYED = auto()
    E_PIECE_BUILT = auto()
    E_UPGRADE_BUILT = auto()
    E_INVALID_MOVE_ORDERS = auto()
    E_INVALID_BUILD_ORDERS = auto()
    E_INVALID_UPGRADE_ORDERS = auto()
    E_ORDER_CANCELED = auto()
    E_ARMOR_GRANTED = auto()
    E_PIECE_HEALED = auto()
    E_PIECE_ON_INVALID_TERRAIN = auto()
    E_TILE_TERRAFORMED = auto()
    E_PLAYER_CONCEDED = auto()
    E_TEAM_DEFEATED = auto()
    E_DEATH_AOE = auto()
    E_DEATH_MONEY_LOSS = auto()
    E_RESOURCES_GAINED = auto()
    E_RESOURCES_LOST = auto()
    E_PIECE_DAMAGED = auto()
    E_PIECE_DEMOLISHED = auto()

    # Phase events
    START_PHASE_START_TURN = auto()
    START_PHASE_ORDERS = auto()
    START_PHASE_EXECUTE_MOVE = auto()
    START_PHASE_EXECUTE_BUILD = auto()
    START_PHASE_EXECUTE_COMBAT = auto()
    START_PHASE_EXECUTE_RANGED = auto()
    START_PHASE_EXECUTE_SPECIAL = auto()
    E_NEXT_PHASE = auto()

    END_PHASE_START_TURN = auto()
    END_PHASE_ORDERS = auto()
    END_PHASE_MOVE = auto()
    END_PHASE_BUILD = auto()
    END_PHASE_COMBAT = auto()
    END_PHASE_RANGED = auto()
    END_PHASE_SPECIAL = auto()

    MENU_SELECT_OPTION = auto()

    # Text input options
    TEXT_SUBMIT_INPUT = auto()
    TEXT_CANCEL_INPUT = auto()

    # Network notification events
    NETWORK_CLIENT_CONNECTED = auto()
    NETWORK_CONNECTED_TO_HOST = auto()
    NETWORK_CLIENT_DISCONNECTED = auto()
    NETWORK_DISCONNECTED_FROM_HOST = auto()


# Publish the specified game event, with the data provided.
# Usage: publish_game_event(EventType.MY_EVENT_TYPE, {'data': my_data})
def publish_game_event(event_type, data):
    data[EVENT_TYPE] = event_type
    event = Event(USEREVENT, data)
    post(event)


# Publish the specified game event, with the data provided, and the event marked as being from the network (not local)
# Usage: publish_game_event(EventType.MY_EVENT_TYPE, {'data': my_data})
def publish_game_event_from_network(event_type, data):
    data[FROM_NETWORK] = True
    publish_game_event(event_type, data)


# Return true if the event is any of the provided types.
# Usage: is_event_type(event, EventType.MY_EVENT_TYPE1, EventType.MY_EVENT_TYPE2, ...)
def is_event_type(event, *event_type):
    return event.type == USEREVENT and event.event_type in event_type


# Return true if the event is of any of the provided types AND it originated here (not from the network)
# Usage: is_event_type(event, EventType.MY_EVENT_TYPE1, EventType.MY_EVENT_TYPE2, ...)
def is_local_event_type(event, *event_type):
    return event.type == USEREVENT and event.event_type in event_type and not hasattr(event, FROM_NETWORK)
