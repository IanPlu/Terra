from terra.piece.piece import Piece
from terra.constants import Team
from terra.resources.assets import spr_building_base
from terra.piece.piecetype import PieceType


# An immoveable building placed on the map.
# Buildings function like Units-- they have health and can execute a limited set of orders.
# Buildings are destroyed when their health reaches 0.
class Building(Piece):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)

        self.piece_type = PieceType.BUILDING

        self.sprite = spr_building_base

        # Building specific overrideable variables
        self.resource_production = (0, 0, 0)
        self.buildable_units = []

    def handle_phase_start_turn(self, event):
        # Produce resources
        if not self.resource_production == (0, 0, 0):
            self.team_manager.add_resources(self.team, self.resource_production)

        super().handle_phase_start_turn(event)

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
