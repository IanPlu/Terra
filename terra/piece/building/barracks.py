from terra.piece.building.building import Building
from terra.constants import Team
from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType


# Produces units for a team.
class Barracks(Building):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)
        self.building_type = BuildingType.BARRACKS

        self.buildable_units = [UnitType.TROOPER, UnitType.RANGER, UnitType.GHOST]
        self.resource_production = (0, 0, 0)