from terra.engine.gameobject import GameObject
from terra.piece.unit.colonist import Colonist
from terra.piece.unit.trooper import Trooper
from terra.piece.unit.ranger import Ranger
from terra.piece.unit.ghost import Ghost
from terra.piece.unit.unit import Team
from terra.piece.building.base import Base
from terra.piece.building.generator import Generator
from terra.piece.building.barracks import Barracks
from terra.event import *
from terra.piece.piececonflict import PieceConflict
from terra.piece.orders import MoveOrder, BuildOrder
from terra.piece.piecetype import PieceType
from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType
from terra.piece.unit.unitprice import unit_prices
from terra.piece.unit.piecedamage import piece_damage
from terra.economy.resourcetypes import ResourceType


# Contains and manages all units and buildings from all teams
class PieceManager(GameObject):
    def __init__(self, battle, game_map, team_manager, roster=None, buildings=None):
        super().__init__()

        self.battle = battle
        self.game_map = game_map
        self.team_manager = team_manager

        # Hold the units and buildings located on this map
        # Key pairs look like: (gx, gy): [unit1, unit2, building1...]
        self.pieces = {}

        # Generate units from the provided Roster, if any
        if roster:
            for unit in roster:
                data = unit.split(' ')
                self.generate_piece_from_type(int(data[0]), int(data[1]), Team[data[2]], UnitType[data[3]])

        # Generate buildings from the provided buildings, if any
        if buildings:
            for building in buildings:
                data = building.split(' ')
                self.generate_piece_from_type(int(data[0]), int(data[1]), Team[data[2]], BuildingType[data[3]])

    # Return a list of piece(s) at the specified grid location
    # If piece type or team is provided, only return pieces of that type.
    def get_pieces_at(self, gx, gy, piece_type=None):
        pieces = self.pieces.get((gx, gy))
        if not pieces:
            return []
        else:
            if piece_type:
                pieces = [piece for piece in pieces if piece.piece_type == piece_type]
            return pieces

    # Return the unit or building for the specified team (None if no piece for that team is present)
    def get_piece_at(self, gx, gy, team, piece_type=None):
        for piece in self.get_pieces_at(gx, gy):
            if piece.team == team and (not piece_type or piece.piece_type == piece_type):
                return piece
        return None

    # Return any enemy units or buildings at the location (not belonging to the provided team)
    def get_enemy_pieces_at(self, gx, gy, my_team):
        pieces = []
        for piece in self.get_pieces_at(gx, gy):
            if not piece.team == my_team:
                pieces.append(piece)
        return pieces

    # Return all units or buildings belonging to the specified team
    def get_all_pieces_for_team(self, team, piece_type=None):
        all_pieces = []
        for coordinate, pieces in self.pieces.items():
            all_pieces.extend(pieces)

        # Filter
        all_pieces = [piece for piece in all_pieces if piece.team == team]
        if piece_type:
            all_pieces = [piece for piece in all_pieces if piece.piece_type == piece_type]

        return all_pieces

    # Register a piece with the game map.
    def register_piece(self, piece):
        if not self.pieces.get((piece.gx, piece.gy)):
            self.pieces[(piece.gx, piece.gy)] = []
        self.pieces[(piece.gx, piece.gy)].append(piece)

    # Unregister a piece with the game map.
    def remove_piece(self, gx, gy, team):
        piece = self.get_piece_at(gx, gy, team)
        if piece:
            self.pieces[(gx, gy)].remove(piece)
            if len(self.pieces[(gx, gy)]) == 0:
                del self.pieces[(gx, gy)]

    def generate_piece_from_type(self, gx, gy, team, piece_type):
        if piece_type == UnitType.COLONIST:
            self.register_piece(Colonist(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
        elif piece_type == UnitType.TROOPER:
            self.register_piece(Trooper(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
        elif piece_type == UnitType.RANGER:
            self.register_piece(Ranger(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
        elif piece_type == UnitType.GHOST:
            self.register_piece(Ghost(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
        elif piece_type == BuildingType.BASE:
            self.register_piece(Base(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
        elif piece_type == BuildingType.CARBON_GENERATOR:
            self.register_piece(Generator(self, self.team_manager, self.battle, self.game_map, team, gx, gy, ResourceType.CARBON))
        elif piece_type == BuildingType.MINERAL_GENERATOR:
            self.register_piece(Generator(self, self.team_manager, self.battle, self.game_map, team, gx, gy, ResourceType.MINERALS))
        elif piece_type == BuildingType.GAS_GENERATOR:
            self.register_piece(Generator(self, self.team_manager, self.battle, self.game_map, team, gx, gy, ResourceType.GAS))
        elif piece_type == BuildingType.BARRACKS:
            self.register_piece(Barracks(self, self.team_manager, self.battle, self.game_map, team, gx, gy))

    # Move a unit on the game map
    def move_unit(self, gx, gy, team):
        unit = self.get_piece_at(gx, gy, team, PieceType.UNIT)
        if unit:
            self.register_piece(unit)
            self.remove_piece(gx, gy, team)

    # Get lists of all units and buildings, regardless of position or team
    def __get_all_pieces__(self):
        units = []
        buildings = []
        for coordinate in self.pieces:
            for piece in self.pieces[coordinate]:
                if piece.piece_type == PieceType.UNIT:
                    units.append(piece)
                elif piece.piece_type == PieceType.BUILDING:
                    buildings.append(piece)
        return units, buildings

    # Return true if all movement and build orders for the provided team are valid
    # (no friendly units end up in the same tile)
    def validate_orders(self, team):
        coordinates = []
        spent_resources = []

        for piece in self.get_all_pieces_for_team(team):
            if piece.current_order:
                if isinstance(piece.current_order, MoveOrder):
                    coordinates.append((piece.current_order.dx, piece.current_order.dy))
                elif isinstance(piece.current_order, BuildOrder):
                    # Build orders for units result in a piece on the designated tile, and the builder's tile
                    if piece.current_order.new_piece_type in UnitType:
                        coordinates.append((piece.current_order.tx, piece.current_order.ty))
                        coordinates.append((piece.gx, piece.gy))
                    elif piece.current_order.new_piece_type in BuildingType:
                        coordinates.append((piece.current_order.tx, piece.current_order.ty))

                    # Check that a team isn't spending more than they have
                    spent_resources.append(unit_prices[piece.current_order.new_piece_type])
            else:
                coordinates.append((piece.gx, piece.gy))

        # Move orders are valid if all the coordinates are unique-- no duplicates are removed
        move_orders_valid = len(coordinates) == len(set(coordinates))
        build_orders_valid = self.team_manager.can_spend_resources(team, spent_resources)

        return move_orders_valid and build_orders_valid

    # Check for overlapping enemy units, and resolve their combat
    def resolve_unit_combat(self):
        # Find conflicting units (opposing team units occupying the same space
        conflicting_pieces = []
        for coordinate in self.pieces:
            if len(self.pieces.get(coordinate)) > 1:
                conflicting_pieces.append(self.pieces.get(coordinate))

        # Conflict resolution
        if len(conflicting_pieces) > 0:
            for piece_pair in conflicting_pieces:
                conflict = PieceConflict(piece_pair[0], piece_pair[1])
                conflict.resolve()

    def ranged_attack(self, gx, gy, origin_team, tx, ty):
        # Find the origin unit and the target pieces
        origin_unit = self.get_piece_at(gx, gy, origin_team)
        target_pieces = self.get_enemy_pieces_at(tx, ty, origin_team)

        for target in target_pieces:
            if hasattr(target, 'unit_type'):
                target_type = target.unit_type
            elif hasattr(target, 'building_type'):
                target_type = target.building_type
            else:
                target_type = None

            target.hp -= piece_damage[origin_unit.team][origin_unit.unit_type][target_type]

    def step(self, event):
        super().step(event)

        units, buildings = self.__get_all_pieces__()
        for building in buildings:
            building.step(event)
        for unit in units:
            unit.step(event)

        if is_event_type(event, E_UNIT_MOVED):
            self.move_unit(event.gx, event.gy, event.team)
        elif is_event_type(event, E_UNIT_RANGED_ATTACK):
            self.ranged_attack(event.gx, event.gy, event.team, event.tx, event.ty)
        elif is_event_type(event, E_PIECE_DEAD):
            self.remove_piece(event.gx, event.gy, event.team)
        elif is_event_type(event, E_PIECE_BUILT):
            self.generate_piece_from_type(event.tx, event.ty, event.team, event.new_piece_type)

        if is_event_type(event, START_PHASE_EXECUTE_COMBAT):
            self.resolve_unit_combat()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        units, buildings = self.__get_all_pieces__()
        for building in buildings:
            building.render(game_screen, ui_screen)
        for unit in units:
            unit.render(game_screen, ui_screen)
