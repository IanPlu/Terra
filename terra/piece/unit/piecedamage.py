from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType
from terra.constants import Team


# Base unit damage tables. First entry is the attacking unit, second entry is the defending unit.
base_piece_damage = {
    UnitType.COLONIST: {
        UnitType.COLONIST: 0,
        UnitType.TROOPER: 0,
        UnitType.RANGER: 0,
        UnitType.GHOST: 0,
        BuildingType.BASE: 0,
        BuildingType.CARBON_GENERATOR: 0,
        BuildingType.MINERAL_GENERATOR: 0,
        BuildingType.GAS_GENERATOR: 0,
        BuildingType.BARRACKS: 0,
    },
    UnitType.TROOPER: {
        UnitType.COLONIST: 1,
        UnitType.TROOPER: 1,
        UnitType.RANGER: 1,
        UnitType.GHOST: 2,
        BuildingType.BASE: 2,
        BuildingType.CARBON_GENERATOR: 2,
        BuildingType.MINERAL_GENERATOR: 2,
        BuildingType.GAS_GENERATOR: 2,
        BuildingType.BARRACKS: 2,
    },
    UnitType.RANGER: {
        UnitType.COLONIST: 1,
        UnitType.TROOPER: 2,
        UnitType.RANGER: 1,
        UnitType.GHOST: 1,
        BuildingType.BASE: 2,
        BuildingType.CARBON_GENERATOR: 2,
        BuildingType.MINERAL_GENERATOR: 2,
        BuildingType.GAS_GENERATOR: 2,
        BuildingType.BARRACKS: 2,
    },
    UnitType.GHOST: {
        UnitType.COLONIST: 2,
        UnitType.TROOPER: 1,
        UnitType.RANGER: 2,
        UnitType.GHOST: 1,
        BuildingType.BASE: 2,
        BuildingType.CARBON_GENERATOR: 2,
        BuildingType.MINERAL_GENERATOR: 2,
        BuildingType.GAS_GENERATOR: 2,
        BuildingType.BARRACKS: 2,
    }
}

# Actual up to date damage tables, specific to each team.
# Upgrades can mutate this value over the course of the game.
piece_damage = {}

# Propagate base values to each team
for team in Team:
    piece_damage[team] = base_piece_damage
