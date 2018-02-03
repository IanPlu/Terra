from terra.economy.resourcetypes import ResourceType
from terra.economy.resourceyields import resource_yields
from terra.piece.building.building import Building
from terra.piece.building.buildingtype import BuildingType
from terra.team import Team

__resource_to_building_type__ = {
    ResourceType.CARBON: BuildingType.CARBON_GENERATOR,
    ResourceType.MINERALS: BuildingType.MINERAL_GENERATOR,
    ResourceType.GAS: BuildingType.GAS_GENERATOR,
}


# A resource generator for a team.
# Generators are subtyped for a specific resource when they're placed.
class Generator(Building):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0, hp=None,
                 resource_type=ResourceType.CARBON):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy, hp)
        self.resource_type = resource_type
        self.building_type = __resource_to_building_type__[self.resource_type]

        self.buildable_units = []
        self.resource_production = self.__get_resource_yields__()

    # Return how much of each resource this building produces, depending on its resource type.
    def __get_resource_yields__(self):
        if self.resource_type == ResourceType.CARBON:
            return resource_yields[self.team][self.resource_type], 0, 0
        elif self.resource_type == ResourceType.MINERALS:
            return 0, resource_yields[self.team][self.resource_type], 0
        elif self.resource_type == ResourceType.GAS:
            return 0, 0, resource_yields[self.team][self.resource_type]
        else:
            return 0, 0, 0
