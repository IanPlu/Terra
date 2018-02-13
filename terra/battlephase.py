from enum import Enum


# Substeps in the current turn, executed in order.
class BattlePhase(Enum):
    START_TURN = 0
    ORDERS = 1
    EXECUTE_MOVE = 2
    EXECUTE_BUILD = 3
    EXECUTE_COMBAT = 4
    EXECUTE_RANGED = 5
    EXECUTE_SPECIAL = 6
