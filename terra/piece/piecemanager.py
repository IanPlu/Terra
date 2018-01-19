from terra.engine.gameobject import GameObject
from terra.piece.unit.colonist import Colonist
from terra.piece.unit.trooper import Trooper
from terra.piece.unit.ranger import Ranger
from terra.piece.unit.ghost import Ghost
from terra.piece.unit.unit import Team
from terra.piece.building.base import Base
from terra.event import *
from terra.piece.piececonflict import PieceConflict
from terra.piece.orders import MoveOrder
from terra.piece.piecetype import PieceType


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

                gx = int(data[0])
                gy = int(data[1])
                team = Team[data[2]]
                unit_type = data[3]

                if unit_type == "Colonist":
                    self.register_piece(Colonist(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Trooper":
                    self.register_piece(Trooper(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Ranger":
                    self.register_piece(Ranger(self, self.team_manager, self.battle, self.game_map, team, gx, gy))
                elif unit_type == "Ghost":
                    self.register_piece(Ghost(self, self.team_manager, self.battle, self.game_map, team, gx, gy))

        # Generate buildings from the provided buildings, if any
        if buildings:
            for building in buildings:
                data = building.split(' ')

                gx = int(data[0])
                gy = int(data[1])
                team = Team[data[2]]
                building_type = data[3]

                if building_type == "Base":
                    self.register_piece(Base(self, self.team_manager, self.battle, self.game_map, team, gx, gy))

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

    # Return true if all movement orders for the provided team are valid (no friendly units end up in the same tile)
    def validate_movement_orders(self, team):
        coordinates = []
        for unit in self.get_all_pieces_for_team(team):
            if unit.current_order:
                if isinstance(unit.current_order, MoveOrder):
                    coordinates.append((unit.current_order.dx, unit.current_order.dy))
            else:
                coordinates.append((unit.gx, unit.gy))

        # Return true if all the coordinates are unique-- no duplicates are removed
        return len(coordinates) == len(set(coordinates))

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
        # Find the origin unit and the target unit
        origin_unit = self.get_piece_at(gx, gy, origin_team)
        target_units = self.get_enemy_pieces_at(tx, ty, origin_team)

        for unit in target_units:
            unit.hp -= origin_unit.ranged_attack

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

        if is_event_type(event, START_PHASE_EXECUTE_COMBAT):
            self.resolve_unit_combat()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        units, buildings = self.__get_all_pieces__()
        for building in buildings:
            building.render(game_screen, ui_screen)
        for unit in units:
            unit.render(game_screen, ui_screen)
