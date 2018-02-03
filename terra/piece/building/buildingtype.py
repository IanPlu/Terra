from enum import Enum

from terra.event import MENU_BUILD_CARBON_GENERATOR, MENU_BUILD_MINERAL_GENERATOR, \
    MENU_BUILD_GAS_GENERATOR, MENU_BUILD_BARRACKS


# Possible building types.
class BuildingType(Enum):
    BUILDING = 0
    BASE = 1
    CARBON_GENERATOR = 2
    MINERAL_GENERATOR = 3
    GAS_GENERATOR = 4
    BARRACKS = 5


# Conversion for building types from menu option events
building_type_from_menu_option = {
    MENU_BUILD_CARBON_GENERATOR: BuildingType.CARBON_GENERATOR,
    MENU_BUILD_MINERAL_GENERATOR: BuildingType.MINERAL_GENERATOR,
    MENU_BUILD_GAS_GENERATOR: BuildingType.GAS_GENERATOR,
    MENU_BUILD_BARRACKS: BuildingType.BARRACKS
}
