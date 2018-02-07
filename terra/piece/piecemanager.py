from collections import Counter

from terra.engine.gameobject import GameObject
from terra.event import *
from terra.piece.orders import MoveOrder, BuildOrder
from terra.piece.piece import Piece
from terra.piece.pieceattributes import Attribute
from terra.piece.piececonflict import PieceConflict
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.team import Team
from terra.util.collectionutil import safe_get_from_list


# Contains and manages all pieces from all teams
class PieceManager(GameObject):
    def __init__(self, battle, game_map, team_manager, pieces=None):
        super().__init__()

        self.battle = battle
        self.game_map = game_map
        self.team_manager = team_manager

        # Hold the pieces located on this map
        # Key pairs look like: (gx, gy): [unit1, unit2, building1...]
        self.pieces = {}

        # Generate units from the provided Roster, if any
        if pieces:
            for piece in pieces:
                data = piece.split(' ')
                hp = int(safe_get_from_list(data, 4)) if safe_get_from_list(data, 4) else None

                self.register_piece(Piece(PieceType[data[3]], self, self.team_manager, self.battle, self.game_map,
                                          Team[data[2]], int(data[0]), int(data[1]), hp))

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
    def get_piece_at(self, gx, gy, team, piece_subtype=None):
        for piece in self.get_pieces_at(gx, gy):
            if piece.team == team and (not piece_subtype or piece.piece_subtype == piece_subtype):
                return piece
        return None

    # Return any enemy units or buildings at the location (not belonging to the provided team)
    def get_enemy_pieces_at(self, gx, gy, my_team):
        pieces = []
        for piece in self.get_pieces_at(gx, gy):
            if not piece.team == my_team:
                pieces.append(piece)
        return pieces

    # Return all pieces belonging to the specified team. Supports filtering down to a specific type or subtype.
    def get_all_pieces_for_team(self, team, piece_subtype=None, piece_type=None):
        all_pieces = []
        for coordinate, pieces in self.pieces.items():
            all_pieces.extend(pieces)

        # Filter
        all_pieces = [piece for piece in all_pieces if piece.team == team]
        if piece_subtype:
            filtered_pieces = []

            for piece in all_pieces:
                if piece.piece_subtype == piece_subtype:
                    filtered_pieces.append(piece)

            return filtered_pieces
        elif piece_type:
            filtered_pieces = []

            for piece in all_pieces:
                if piece.piece_type == piece_type:
                    filtered_pieces.append(piece)

            return filtered_pieces
        else:
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
        unit = self.get_piece_at(gx, gy, team, PieceSubtype.UNIT)
        if unit:
            self.register_piece(unit)
            self.remove_piece(gx, gy, team)

    # Get lists of all units and buildings, regardless of position or team
    def __get_all_pieces__(self):
        pieces = []
        for coordinate in self.pieces:
            for piece in self.pieces[coordinate]:
                pieces.append(piece)
        return pieces

    # Return a list of string representations for all units and buildings, for saving the game state
    def serialize_pieces(self):
        pieces = self.__get_all_pieces__()

        piece_strings = []
        for piece in pieces:
            piece_strings.append("{} {} {} {} {}".format(piece.gx, piece.gy,
                                                         piece.team.name,
                                                         piece.piece_type.name,
                                                         piece.hp))
        return piece_strings

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
                    # Build orders result in a piece on the designated tile, and the builder's tile
                    coordinates.append((piece.current_order.tx, piece.current_order.ty))
                    coordinates.append((piece.gx, piece.gy))

                    # Check that a team isn't spending more than they have
                    spent_resources.append(self.team_manager.attr(piece.team, piece.current_order.new_piece_type, Attribute.PRICE))
            else:
                coordinates.append((piece.gx, piece.gy))

        # Move orders are valid if all the coordinates are unique-- no duplicates are removed
        move_orders_valid = len(coordinates) == len(set(coordinates))
        build_orders_valid = self.team_manager.can_spend_resources(team, spent_resources)

        # Publish events containing the invalid orders, if any
        if not move_orders_valid:
            # Find and return the coordinates of the collision(s)
            collisions = [k for k, v in Counter(coordinates).items() if v > 1]

            publish_game_event(E_INVALID_MOVE_ORDERS, {
                'team': team,
                'invalid_coordinates': collisions
            })
        if not build_orders_valid:
            publish_game_event(E_INVALID_BUILD_ORDERS, {
                'team': team,
                'spent_resources': spent_resources
            })

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
                conflict = PieceConflict(piece_pair[0], piece_pair[1], self.team_manager)
                conflict.resolve()

    def ranged_attack(self, gx, gy, origin_team, tx, ty):
        # Find the origin unit and the target pieces
        origin_unit = self.get_piece_at(gx, gy, origin_team)
        target_pieces = self.get_enemy_pieces_at(tx, ty, origin_team)

        for target in target_pieces:
            target_type = target.piece_type
            attack = self.team_manager.attr(origin_unit.team, origin_unit.piece_type, Attribute.ATTACK)
            multiplier = self.team_manager.attr(origin_unit.team, origin_unit.piece_type, Attribute.ATTACK_MULTIPLIER)[target_type]

            target.hp -= attack * multiplier

    def step(self, event):
        super().step(event)

        pieces = self.__get_all_pieces__()
        for piece in pieces:
            piece.step(event)

        if is_event_type(event, E_UNIT_MOVED):
            self.move_unit(event.gx, event.gy, event.team)
        elif is_event_type(event, E_UNIT_RANGED_ATTACK):
            self.ranged_attack(event.gx, event.gy, event.team, event.tx, event.ty)
        elif is_event_type(event, E_PIECE_DEAD):
            self.remove_piece(event.gx, event.gy, event.team)
        elif is_event_type(event, E_PIECE_BUILT):
            self.register_piece(Piece(event.new_piece_type, self, self.team_manager, self.battle, self.game_map,
                                      event.team, event.tx, event.ty))

        if is_event_type(event, START_PHASE_EXECUTE_COMBAT):
            self.resolve_unit_combat()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        pieces = self.__get_all_pieces__()
        for piece in pieces:
            piece.render(game_screen, ui_screen)
