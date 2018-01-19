from terra.piece.building.building import Building
from terra.constants import Team
from terra.resources.assets import spr_building_base
from terra.event import publish_game_event, E_BASE_DESTROYED


# A team's base of operations.
# Allows purchasing upgrades and building colonists.
# If a team's base is destroyed, they lose.
class Base(Building):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)

        self.sprite = spr_building_base

        # self.buildable_units = [Colonist]
        self.resource_production = (100, 100, 100)

    def on_death(self):
        publish_game_event(E_BASE_DESTROYED, {
            'team': self.team,
            'gx': self.gx,
            'gy': self.gy
        })
        super().on_death()
