from terra.piece.building.building import Building
from terra.constants import Team
from terra.event import publish_game_event, E_BASE_DESTROYED
from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType


# A team's base of operations.
# Allows purchasing upgrades and building colonists.
# If a team's base is destroyed, they lose.
class Base(Building):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)
        self.building_type = BuildingType.BASE

        self.buildable_units = [UnitType.COLONIST]
        self.resource_production = (10, 10, 10)

    def on_death(self):
        publish_game_event(E_BASE_DESTROYED, {
            'team': self.team,
            'gx': self.gx,
            'gy': self.gy
        })
        super().on_death()
