from terra.constants import *
from terra.piece.piece import Piece
from terra.event import *
from terra.piece.piecetype import PieceType
from terra.map.movementtype import MovementType
from terra.piece.orders import *
from terra.piece.unit.unittype import UnitType
from terra.resources.assets import spr_units
from terra.piece.unit.damagetype import DamageType
from terra.map.tiletype import TileType
from terra.piece.building.buildingtype import BuildingType, building_type_from_menu_option


# A single unit on the map.
class Unit(Piece):
    # Create a new Unit at the provided grid coordinates for the specified team
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0, hp=None):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy, hp)

        self.piece_type = PieceType.UNIT
        self.unit_type = UnitType.UNIT

        # Unit-specific overrideable variables.
        self.damage_type = DamageType.MELEE
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GROUND
        self.movement_range = 0
        self.can_build = False

    def get_sprite(self):
        return spr_units[self.team][self.unit_type]

    def get_available_actions(self):
        actions = []
        if self.movement_range > 0:
            actions.append(MENU_MOVE)
        if self.damage_type == DamageType.RANGED and not self.in_conflict:
            actions.append(MENU_RANGED_ATTACK)
        if self.can_build and self.__can_build_generator__():
            actions.extend([MENU_BUILD_CARBON_GENERATOR, MENU_BUILD_MINERAL_GENERATOR, MENU_BUILD_GAS_GENERATOR])
        if self.can_build and not self.game_map.get_tile_type_at(self.gx, self.gy) == TileType.RESOURCE:
            actions.append(MENU_BUILD_BARRACKS)
        actions.append(MENU_CANCEL_ORDER)
        return actions

    def __can_build_generator__(self):
        return self.game_map.get_tile_type_at(self.gx + 1, self.gy) == TileType.RESOURCE or \
               self.game_map.get_tile_type_at(self.gx - 1, self.gy) == TileType.RESOURCE or \
               self.game_map.get_tile_type_at(self.gx, self.gy + 1) == TileType.RESOURCE or \
               self.game_map.get_tile_type_at(self.gx, self.gy - 1) == TileType.RESOURCE

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
        elif event.option == MENU_BUILD_BARRACKS:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'game_map': self.game_map,
                'movement_type': MovementType.BUILD_BARRACKS,
                'team': self.team,
                'piece_manager': self.piece_manager,
                'option': event.option
            })
        elif event.option in [MENU_BUILD_CARBON_GENERATOR, MENU_BUILD_MINERAL_GENERATOR,
                              MENU_BUILD_GAS_GENERATOR]:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'game_map': self.game_map,
                'movement_type': MovementType.BUILD_GENERATOR,
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
        elif building_type_from_menu_option[event.option] in BuildingType:
            self.set_order(event)

    def set_order(self, event):
        if event.option == MENU_MOVE:
            self.current_order = MoveOrder(self, event.dx, event.dy)
        elif event.option == MENU_RANGED_ATTACK:
            self.current_order = RangedAttackOrder(self, event.dx, event.dy)
        elif event.option in [MENU_BUILD_CARBON_GENERATOR, MENU_BUILD_MINERAL_GENERATOR,
                              MENU_BUILD_GAS_GENERATOR, MENU_BUILD_BARRACKS]:
            self.current_order = BuildOrder(self, event.dx, event.dy, self.team,
                                            building_type_from_menu_option[event.option])

        elif event.option == MENU_CANCEL_ORDER:
            self.current_order = None
        else:
            self.current_order = None

    def handle_phase_build(self, event):
        if isinstance(self.current_order, BuildOrder):
            publish_game_event(E_PIECE_BUILT, {
                'tx': self.current_order.tx,
                'ty': self.current_order.ty,
                'team': self.current_order.team,
                'new_piece_type': self.current_order.new_piece_type
            })

            # Pop orders once they're executed
            self.current_order = None

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
