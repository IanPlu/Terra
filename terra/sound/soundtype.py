from enum import Enum

from terra.resources.assets import sfx_cursor_move, sfx_cursor_select, sfx_cursor_cancel, sfx_turn_submitted, \
    sfx_all_turns_submitted, sfx_piece_hit, sfx_order_canceled, sfx_ranged_attack, sfx_building_built, sfx_unit_built, \
    sfx_piece_conflict


class SoundType(Enum):
    CURSOR_MOVE = sfx_cursor_move
    CURSOR_SELECT = sfx_cursor_select
    CURSOR_CANCEL = sfx_cursor_cancel

    TURN_SUBMITTED = sfx_turn_submitted
    ALL_TURNS_SUBMITTED = sfx_all_turns_submitted

    PIECE_DEAD = sfx_piece_hit
    ORDER_CANCELED = sfx_order_canceled

    RANGED_ATTACK = sfx_ranged_attack
    PIECE_CONFLICT = sfx_piece_conflict
    BUILDING_BUILT = sfx_building_built
    UNIT_CREATED = sfx_unit_built
