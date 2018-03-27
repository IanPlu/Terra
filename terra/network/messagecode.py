from enum import Enum


class MessageCode(Enum):
    NEW_CONNECTION = "[NEW_CON]"
    SET_ORDERS = "[SET_ORD]"
    CANCEL_ORDERS = "[CCL_ORD]"
    DROP_CONNECTION = "[DEL_CON]"
    SET_GAME_STATE = "[SET_GAM]"
    END_CONNECTION = "[END_CON]"
    PLAYER_CONCEDED = "[CONCEDE]"
    SET_TEAM = "[SET_TEA]"
    START_BATTLE = "[STA_BAT]"
