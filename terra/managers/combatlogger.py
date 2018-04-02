import logging

from terra.strings import get_string, phase_strings, formatted_strings
from terra.util.loggingutil import get_logger, check_log_dir_exists


# Logs events that occur over the course of the game
class CombatLogger:
    def __init__(self, mapname=None):
        super().__init__()

        if mapname:
            filename = mapname + ".log"
        else:
            filename = "Terra.log"

        check_log_dir_exists()
        self.logger = get_logger("CombatLogger", logging.INFO, filename)

    def log_new_turn(self, turn_number):
        self.logger.info("== TURN {} BEGIN ==".format(turn_number))

    def log_new_phase(self, phase):
        self.logger.info("= {} phase begins".format(get_string(phase_strings, phase)))

    # Log an order assigned to a unit.
    def log_order_assignment(self, piece, order):
        if order:
            self.logger.info("{} was assigned the order '{}'".format(str(piece), str(order)))

    # Log whenever an order is successfully executed.
    def log_successful_order_execution(self, piece, order):
        self.logger.info("{} successfully executed '{}'".format(str(piece), str(order)))

    # Log whenever an order fails to execute (usually because it is contested)
    def log_failed_order_execution(self, piece, order):
        self.logger.info("{} failed to execute '{}'".format(str(piece), str(order)))

    # Log whenever two or more pieces are contesting the same tile
    def log_contesting_pieces(self, pieces):
        self.logger.info("{} are contesting the tile at ({}, {})!".format(str(pieces), pieces[0].gx, pieces[0].gy))

    # Log whenever a piece takes damage.
    def log_damage(self, piece, damage, source):
        self.logger.info("{} took {} damage from {}!".format(str(piece), damage, str(source)))

    def log_healing(self, piece, health):
        self.logger.info("{} healed for {} health.".format(str(piece), health))

    # Log whenever a team researches a new upgrade
    def log_upgrade(self, upgrade, team):
        self.logger.info("{} team researched the upgrade {}".format(str(team), str(upgrade)))

    def log_resource_acquisition(self, amount, team):
        if amount > 0:
            self.logger.info("{} team acquired {} resources.".format(team, amount))
        else:
            self.logger.info("{} team spent {} resources.".format(team, abs(amount)))

    # Log the end of a game.
    def log_results(self, winning_teams, all_teams, team_stats):
        self.logger.info("=== BATTLE OVER! ===")

        for team in all_teams:
            if team in winning_teams:
                self.logger.info("{} team has won!".format(team))
            else:
                self.logger.info("{} team has lost.".format(team))

            self.logger.info("-- Stats for team {} --".format(team))
            for stat, value in team_stats[team].items():
                self.logger.info("  * " + get_string(formatted_strings, stat).format(value))

