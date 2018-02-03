from terra.piece.building.buildingtype import BuildingType
from terra.piece.unit.unittype import UnitType

# Resource costs for all buildable pieces.
piece_prices = {
    UnitType.COLONIST: (10, 10, 10),
    UnitType.TROOPER: (10, 10, 10),
    UnitType.RANGER: (10, 10, 10),
    UnitType.GHOST: (10, 10, 10),
    BuildingType.CARBON_GENERATOR: (0, 0, 0),
    BuildingType.MINERAL_GENERATOR: (0, 0, 0),
    BuildingType.GAS_GENERATOR: (0, 0, 0),
    BuildingType.BARRACKS: (30, 30, 30),
}
