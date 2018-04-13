import logging

from terra.strings import get_string, phase_strings, formatted_strings
from terra.util.loggingutil import get_logger, check_log_dir_exists
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.session import Manager


# Logs events that occur over the course of a battle.
class CombatLogger(GameObject):
    def __init__(self, mapname=None):
        super().__init__()

        if mapname:
            filename = mapname + ".log"
        else:
            filename = "Terra.log"

        check_log_dir_exists()
        self.logger = get_logger("CombatLogger", logging.INFO, filename)

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.START_PHASE_START_TURN, self.log_new_turn)
        event_bus.register_handler(EventType.E_NEXT_PHASE, self.log_new_phase)
        event_bus.register_handler(EventType.END_PHASE_ORDERS, self.log_order_assignments)
        event_bus.register_handler(EventType.E_RESOURCES_GAINED, self.log_resource_acquisition)
        event_bus.register_handler(EventType.E_RESOURCES_LOST, self.log_resource_loss)
        event_bus.register_handler(EventType.E_UPGRADE_BUILT, self.log_upgrade)

        event_bus.register_handler(EventType.E_ORDER_CANCELED, self.log_failed_order_execution)
        event_bus.register_handler(EventType.E_PIECE_DAMAGED, self.log_damage)
        event_bus.register_handler(EventType.E_PIECE_HEALED, self.log_healing)

        event_bus.register_handler(EventType.E_PIECE_BUILT, self.log_piece_built)
        event_bus.register_handler(EventType.E_UNIT_MOVED, self.log_piece_moved)
        event_bus.register_handler(EventType.E_UNIT_RANGED_ATTACK, self.log_ranged_attack)
        event_bus.register_handler(EventType.E_TILE_TERRAFORMED, self.log_terraforming)
        event_bus.register_handler(EventType.E_PIECE_DEMOLISHED, self.log_demolition)

        event_bus.register_handler(EventType.E_BATTLE_OVER, self.log_results)
        event_bus.register_handler(EventType.E_PIECES_IN_CONFLICT, self.log_contesting_pieces)

    # Log the start of new turns.
    def log_new_turn(self, event):
        self.logger.info("== TURN {} BEGIN ==".format(event.turn_number))

    # Log the start of a new phase.
    def log_new_phase(self, event):
        self.logger.info("= {} phase begins".format(get_string(phase_strings, event.new_phase)))

    # Log all orders from all pieces
    def log_order_assignments(self, event):
        for piece in self.get_manager(Manager.PIECE).__get_all_pieces__():
            self.log_order_assignment(piece, piece.current_order)

    # Log an order assigned to a unit.
    def log_order_assignment(self, piece, order):
        if order:
            self.logger.info("{} was assigned the order '{}'".format(str(piece), str(order)))

    def log_piece_built(self, event):
        self.logger.info("{} {} was built on ({}, {}). ".format(event.team, event.new_piece_type, event.tx, event.ty))

    def log_piece_moved(self, event):
        piece = self.get_manager(Manager.PIECE).get_piece_at(event.gx, event.gy, event.team)
        self.logger.info("{} moved to ({}, {})".format(piece, event.dx, event.dy))

    def log_ranged_attack(self, event):
        piece = self.get_manager(Manager.PIECE).get_piece_at(event.gx, event.gy, event.team)
        self.logger.info("{} conducted a ranged attack on ({}, {})".format(piece, event.tx, event.ty))

    def log_terraforming(self, event):
        self.logger.info("Tile at ({}, {}) was {}".format(event.gx, event.gy, "raised" if event.raising else "lowered"))

    def log_demolition(self, event):
        piece = self.get_manager(Manager.PIECE).get_piece_at(event.gx, event.gy, event.team)
        self.logger.info("{} was successfully demolished.".format(piece))

    # Log whenever an order fails to execute (usually because it is contested)
    def log_failed_order_execution(self, event):
        piece = self.get_manager(Manager.PIECE).get_piece_at(event.gx, event.gy, event.team)
        self.logger.info("{} failed to execute its orders!".format(str(piece)))

    # Log whenever two or more pieces are contesting the same tile
    def log_contesting_pieces(self, event):
        pieces = self.get_manager(Manager.PIECE).get_pieces_at(event.gx, event.gy)
        self.logger.info("{} are contesting the tile at ({}, {})!".format(str(pieces), event.gx, event.gy))

    # Log whenever a piece takes damage.
    def log_damage(self, event):
        self.logger.info("{} took {} damage from {}!".format(str(event.piece), event.damage, str(event.source)))

    def log_healing(self, event):
        piece = self.get_manager(Manager.PIECE).get_piece_at(event.gx, event.gy, event.team)
        self.logger.info("{} healed for {} health.".format(str(piece), event.health))

    # Log whenever a team researches a new upgrade
    def log_upgrade(self, event):
        self.logger.info("{} team researched the upgrade {}".format(str(event.team), str(event.new_upgrade_type)))

    # Log a change in a team's resource count
    def log_resource_change(self, team, amount):
        if amount > 0:
            self.logger.info("{} team acquired {} resources.".format(team, amount))
        else:
            self.logger.info("{} team spent {} resources.".format(team, abs(amount)))

    def log_resource_acquisition(self, event):
        self.log_resource_change(event.team, event.new_resources)

    def log_resource_loss(self, event):
        self.log_resource_change(event.team, -event.resources_lost)

    # Log the end of a game.
    def log_results(self, event):
        self.logger.info("=== BATTLE OVER! ===")
        winning_team = event.results["winning_team"]
        all_teams = event.results["all_teams"]
        team_stats = event.results["team_stats"]

        for team in all_teams:
            if team == winning_team:
                self.logger.info("{} team has won!".format(team))
            else:
                self.logger.info("{} team has lost.".format(team))

            self.logger.info("-- Stats for team {} --".format(team))
            for stat, value in team_stats[team].items():
                self.logger.info("  * " + get_string(formatted_strings, stat).format(value))
