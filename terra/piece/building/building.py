from terra.piece.piece import Piece
from terra.constants import Team
from terra.resources.assets import spr_buildings
from terra.piece.piecetype import PieceType
from terra.piece.building.buildingtype import BuildingType
from terra.piece.orders import BuildOrder
from terra.piece.unit.unitprice import unit_prices
from terra.event import *
from terra.map.movementtype import MovementType


# An immoveable building placed on the map.
# Buildings function like Units-- they have health and can execute a limited set of orders.
# Buildings are destroyed when their health reaches 0.
class Building(Piece):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)

        self.piece_type = PieceType.BUILDING
        self.building_type = BuildingType.BUILDING

        # Building specific overrideable variables
        self.resource_production = (0, 0, 0)
        self.buildable_units = []

    def get_sprite(self):
        return spr_buildings[self.team][self.building_type]

    def get_available_actions(self):
        actions = []

        if len(self.buildable_units) and not self.in_conflict:
            actions.append(MENU_BUILD_UNIT)

        actions.extend(super().get_available_actions())
        return actions

    def handle_menu_option(self, event):
        if event.option == MENU_BUILD_UNIT:
            publish_game_event(E_OPEN_BUILD_MENU, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'buildable_units': self.buildable_units,
                'options': self.buildable_units
            })
        elif event.option in UnitType:
            # Attempting to build something, so open the the tile selection
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'game_map': self.game_map,
                'movement_type': MovementType.GROUND,
                'team': self.team,
                'piece_manager': self.piece_manager,
                'option': event.option
            })
        else:
            self.set_order(event)

    def handle_tile_selection(self, event):
        if event.option in UnitType:
            self.set_order(event)

    def set_order(self, event):
        if event.option in UnitType:
            self.current_order = BuildOrder(self, event.dx, event.dy, self.team, event.option)
        else:
            self.current_order = None

    def handle_phase_start_turn(self, event):
        # Produce resources
        if not self.resource_production == (0, 0, 0):
            self.team_manager.add_resources(self.team, self.resource_production)

        super().handle_phase_start_turn(event)

    def handle_phase_build(self, event):
        if isinstance(self.current_order, BuildOrder):
            publish_game_event(E_PIECE_BUILT, {
                'tx': self.current_order.tx,
                'ty': self.current_order.ty,
                'team': self.current_order.team,
                'new_piece_type': self.current_order.new_piece_type
            })

            # Deduct unit price
            self.team_manager.deduct_resources(self.team, unit_prices[self.current_order.new_piece_type])

            # Pop orders once they're executed
            self.current_order = None

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
