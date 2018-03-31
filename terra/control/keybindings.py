from enum import Enum

from pygame.constants import K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d, K_RETURN, K_LSHIFT, K_RSHIFT, K_ESCAPE, \
    K_PAGEUP, K_PAGEDOWN, K_1, K_2, K_3, K_4, K_5, K_BACKQUOTE, K_TAB


# Pygame doesn't assign constants to mouse buttons, just numbers.
# Translate these into usable names.
class MouseConstant(Enum):
    LCLICK = 1
    MCLICK = 2
    RCLICK = 3
    WHEELUP = 4
    WHEELDOWN = 5


# Key bindings and groupings.
# Each enum member is an alias for one or more pygame input constants.
class Key(Enum):
    UP = frozenset([K_UP, K_w])
    DOWN = frozenset([K_DOWN, K_s])
    LEFT = frozenset([K_LEFT, K_a])
    RIGHT = frozenset([K_RIGHT, K_d])

    CONFIRM = frozenset([K_RETURN, MouseConstant.LCLICK])
    CANCEL = frozenset([K_LSHIFT, K_RSHIFT, MouseConstant.RCLICK])
    MENU = frozenset([K_ESCAPE])
    MENU2 = frozenset([K_TAB, MouseConstant.MCLICK])

    SCROLL_UP = frozenset([K_PAGEUP, MouseConstant.WHEELUP])
    SCROLL_DOWN = frozenset([K_PAGEDOWN, MouseConstant.WHEELDOWN])

    DEBUG0 = frozenset([K_BACKQUOTE])
    DEBUG1 = frozenset([K_1])
    DEBUG2 = frozenset([K_2])
    DEBUG3 = frozenset([K_3])
    DEBUG4 = frozenset([K_4])
    DEBUG5 = frozenset([K_5])


# Translate a pygame input constant to a keybinding constant
def translate_input(input):
    for key in Key:
        if input in key.value:
            return key


# Translate a pygame mouse button into to a keybinding constant
def translate_mouse_button(input):
    button = MouseConstant(input)
    return translate_input(button)



