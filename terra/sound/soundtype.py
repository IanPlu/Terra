from enum import Enum

from terra.resources.assets import sfx_cursor_move, sfx_cursor_select, sfx_cursor_cancel


class SoundType(Enum):
    CURSOR_MOVE = sfx_cursor_move
    CURSOR_SELECT = sfx_cursor_select
    CURSOR_CANCEL = sfx_cursor_cancel
