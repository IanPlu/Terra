import logging

from terra.constants import LOG_PATH
from terra.settings import LANGUAGE
from terra.strings import phase_strings


# Logs events that occur over the course of the game
class CombatLogger:
    def __init__(self, mapname):
        super().__init__()

        logging.basicConfig(format="%(message)s",
                            filename=LOG_PATH + mapname + ".log",
                            level=logging.INFO)

    def log_new_round(self, round_number):
        logging.info("== ROUND {} BEGIN ==".format(round_number))

    def log_new_phase(self, phase):
        logging.info("= Phase {} begins".format(phase_strings[LANGUAGE][phase]))

    # Log an order assigned to a unit.
    def log_order_assignment(self, piece, order):
        if order:
            logging.info("{} was assigned the order '{}'".format(str(piece), str(order)))

    # Log whenever an order is successfully executed.
    def log_successful_order_execution(self, piece, order):
        logging.info("{} successfully executed '{}'".format(str(piece), str(order)))

    # Log whenever an order fails to execute (usually because it is contested)
    def log_failed_order_execution(self, piece, order):
        logging.info("{} failed to execute '{}'".format(str(piece), str(order)))

    # Log whenever two or more pieces are contesting the same tile
    def log_contesting_pieces(self, piece1, piece2):
        logging.info("{} and {} are contesting the tile at ({}, {})!".format(str(piece1), str(piece2), piece1.gx, piece1.gy))

    # Log whenever a piece takes damage.
    def log_damage(self, piece, damage):
        logging.info("{} took {} damage!".format(str(piece), damage))
