from pygame.constants import K_UP, K_w, K_DOWN, K_s, K_LEFT, K_a, K_RIGHT, K_d, K_RETURN, K_SPACE, K_BACKSPACE, \
    K_LSHIFT, K_RSHIFT, K_ESCAPE, K_PAGEUP, K_PAGEDOWN, K_1, K_2, K_3, K_4, K_5

# Key bindings
MOUSE_LCLICK = 1
MOUSE_RCLICK = 3

KB_UP = {K_UP, K_w}
KB_DOWN = {K_DOWN, K_s}
KB_LEFT = {K_LEFT, K_a}
KB_RIGHT = {K_RIGHT, K_d}

KB_CONFIRM = {K_RETURN, K_SPACE, MOUSE_LCLICK}
KB_CANCEL = {K_BACKSPACE, K_LSHIFT, K_RSHIFT, MOUSE_RCLICK}
KB_MENU = {K_ESCAPE}

KB_SCROLL_UP = {K_PAGEUP}
KB_SCROLL_DOWN = {K_PAGEDOWN}

KB_DEBUG1 = {K_1}
KB_DEBUG2 = {K_2}
KB_DEBUG3 = {K_3}
KB_DEBUG4 = {K_4}
KB_DEBUG5 = {K_5}
