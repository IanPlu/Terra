from terra.constants import *
from terra.piece.piece import Piece
from terra.event import *
from terra.piece.piecetype import PieceType
from terra.map.movementtype import MovementType
from terra.piece.orders import *


# A single unit on the map.
class Unit(Piece):
    # Create a new Unit at the provided grid coordinates for the specified team
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)

        self.piece_type = PieceType.UNIT

        # Unit-specific overrideable variables.
        self.attack = 0
        self.ranged_attack = 0
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GROUND
        self.movement_range = 0

    def get_available_actions(self):
        actions = []
        if self.movement_range > 0:
            actions.append(MENU_MOVE)
        if self.ranged_attack > 0 and not self.in_conflict:
            actions.append(MENU_RANGED_ATTACK)

        actions.extend(super().get_available_actions())
        return actions

    # Handle menu selections. Open tile selection for moves, ranged attack selection, etc.
    def handle_menu_option(self, event):
        if event.option == MENU_MOVE:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': self.movement_range,
                'game_map': self.game_map,
                'movement_type': self.movement_type,
                'team': self.team,
                'piece_manager': self.piece_manager,
                'option': event.option
            })
        elif event.option == MENU_RANGED_ATTACK:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': self.min_range,
                'max_range': self.max_range,
                'game_map': self.game_map,
                'movement_type': None,
                'team': self.team,
                'piece_manager': self.piece_manager,
                'option': event.option
            })
        else:
            self.set_order(event)

    def handle_tile_selection(self, event):
        if event.option == MENU_MOVE:
            self.set_order(event)
        elif event.option == MENU_RANGED_ATTACK:
            self.set_order(event)

    def set_order(self, event):
        order = None
        if event.option == MENU_MOVE:
            order = MoveOrder(self, event.option, event.dx, event.dy)
        elif event.option == MENU_RANGED_ATTACK:
            order = RangedAttackOrder(self, event.option, event.dx, event.dy)
        elif event.option == MENU_CANCEL_ORDER:
            order = None

        self.current_order = order

    def handle_phase_move(self, event):
        if isinstance(self.current_order, MoveOrder):
            publish_game_event(E_UNIT_MOVED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'dx': self.current_order.dx,
                'dy': self.current_order.dy
            })

            self.gx = self.current_order.dx
            self.gy = self.current_order.dy

            # Pop orders once they're executed
            self.current_order = None

    def handle_phase_ranged(self, event):
        if isinstance(self.current_order, RangedAttackOrder):
            publish_game_event(E_UNIT_RANGED_ATTACK, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'tx': self.current_order.tx,
                'ty': self.current_order.ty
            })

            # Pop orders once they're executed
            self.current_order = None

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
