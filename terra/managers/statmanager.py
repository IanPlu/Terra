from enum import Enum

from terra.engine.gameobject import GameObject
from terra.event import *
from terra.team import Team


# Labels for recorded statistics
class Stat(Enum):
    TILES_MOVED = "TILES_MOVED"
    RANGED_ATTACKS_MADE = "RANGED_ATTACKS_MADE"
    PIECE_CONFLICTS = "PIECE_CONFLICTS"
    PIECES_LOST = "PIECES_LOST"
    PIECES_BUILT = "PIECES_BUILT"
    UPGRADES_RESEARCHED = "UPGRADES_RESEARCHED"


# Manages recording statistics about a game over the course of the game.
# Listens for events and then records their occurrences
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

    def get_results(self):
        return self.team_stats

    def increment_stat(self, team, stat, value=1):
        self.team_stats[team][stat] += value

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_UNIT_MOVED):
            tiles_moved = abs(event.gx - event.dx) + abs(event.gy - event.dy)
            self.increment_stat(event.team, Stat.TILES_MOVED, value=tiles_moved)
        elif is_event_type(event, E_UNIT_RANGED_ATTACK):
            self.increment_stat(event.team, Stat.RANGED_ATTACKS_MADE)
        elif is_event_type(event, E_PIECES_IN_CONFLICT):
            for team in event.teams:
                self.increment_stat(team, Stat.PIECE_CONFLICTS)
        elif is_event_type(event, E_PIECE_DEAD):
            self.increment_stat(event.team, Stat.PIECES_LOST)
        elif is_event_type(event, E_PIECE_BUILT):
            self.increment_stat(event.team, Stat.PIECES_BUILT)
        elif is_event_type(event, E_UPGRADE_BUILT):
            self.increment_stat(event.team, Stat.UPGRADES_RESEARCHED)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
