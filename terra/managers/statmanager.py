from enum import Enum

from terra.engine.gameobject import GameObject
from terra.event.event import is_event_type, EventType
from terra.team import Team


# Labels for recorded statistics
class Stat(Enum):
    TILES_MOVED = "TILES_MOVED"
    RANGED_ATTACKS_MADE = "RANGED_ATTACKS_MADE"
    PIECE_CONFLICTS = "PIECE_CONFLICTS"
    PIECES_LOST = "PIECES_LOST"
    PIECES_BUILT = "PIECES_BUILT"
    UPGRADES_RESEARCHED = "UPGRADES_RESEARCHED"


event_type_to_stat = {
    EventType.E_UNIT_MOVED: Stat.TILES_MOVED,
    EventType.E_UNIT_RANGED_ATTACK: Stat.RANGED_ATTACKS_MADE,
    EventType.E_PIECES_IN_CONFLICT: Stat.PIECE_CONFLICTS,
    EventType.E_PIECE_DEAD: Stat.PIECES_LOST,
    EventType.E_PIECE_BUILT: Stat.PIECES_BUILT,
    EventType.E_UPGRADE_BUILT: Stat.UPGRADES_RESEARCHED,
}


# Manages recording statistics about a game over the course of the game.
# Listens for events and then records their occurrences.
class StatManager(GameObject):
    def __init__(self, teams):
        super().__init__()
        self.team_stats = {}

        for team in teams:
            data = team.split(' ')
            team = Team[data[0]]

            self.team_stats[team] = {}
            for stat in Stat:
                self.team_stats[team][stat] = 0

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        for event_type, stat in event_type_to_stat.items():
            event_bus.register_handler(event_type, self.increment_stat_from_event)

    def get_results(self):
        return self.team_stats

    def increment_stat(self, team, stat, value):
        self.team_stats[team][stat] += value

    def increment_stat_from_event(self, event):
        if is_event_type(event, EventType.E_UNIT_MOVED):
            value = abs(event.gx - event.dx) + abs(event.gy - event.dy)
        else:
            value = 1

        if hasattr(event, 'teams'):
            for team in event.teams:
                self.increment_stat(team, event_type_to_stat[event.event_type], value)
        else:
            self.increment_stat(event.team, event_type_to_stat[event.event_type], value)
