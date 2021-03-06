from collections import Counter

from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.engine.gameobject import GameObject
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.piece.attribute import Attribute
from terra.piece.orders import MoveOrder, BuildOrder, UpgradeOrder
from terra.piece.piece import Piece
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piececonflict import PieceConflict
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.sound.soundtype import SoundType
from terra.team.team import Team
from terra.util.collectionutil import safe_get_from_list


# Manager for all pieces from all teams.
# Contains methods for accessing, filtering, and modifying pieces.
class PieceManager(GameObject):
    def __init__(self, pieces=None):
        super().__init__()

        # Hold the pieces located on this map
        # Key pairs look like: (gx, gy): [unit1, unit2, building1...]
        self.pieces = {}

        # Generate units from the provided text roster, if any
        if pieces:
            for piece in pieces:
                data = piece.split(' ')
                hp = int(safe_get_from_list(data, 4)) if safe_get_from_list(data, 4) else None

                self.register_piece(Piece(PieceType[data[3]], Team[data[2]], int(data[0]), int(data[1]), hp))

    def destroy(self):
        super().destroy()

        if self.pieces:
            pieces = self.__get_all_pieces__()
            for piece in pieces:
                piece.destroy()

            del self.pieces
            self.pieces = {}

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_UNIT_MOVED, self.move_piece_from_event)
        event_bus.register_handler(EventType.E_UNIT_RANGED_ATTACK, self.conduct_ranged_attack_from_event)
        event_bus.register_handler(EventType.E_PIECE_DEAD, self.destroy_piece_from_event)
        event_bus.register_handler(EventType.E_PIECE_BUILT, self.register_piece_from_event)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_COMBAT, self.resolve_unit_combat)

    # Serialize all orders for pieces from the specified team for submission to another player in a network game
    def serialize_orders(self, team):
        orders = {}
        pieces = self.get_all_pieces_for_team(team)
        for piece in pieces:
            if piece.current_order:
                orders[(piece.gx, piece.gy)] = piece.current_order.serialize()
            else:
                orders[(piece.gx, piece.gy)] = None

        return orders

    # Mass set orders for all pieces belonging to the provided team.
    def set_orders(self, team, orders):
        pieces = self.get_all_pieces_for_team(team)
        for piece in pieces:
            piece.current_order = orders.get((piece.gx, piece.gy))

    # Return a list of piece(s) at the specified grid location
    # If piece type or team is provided, only return pieces of that type.
    def get_pieces_at(self, gx, gy, piece_type=None, team=None, piece_subtype=None):
        pieces = self.pieces.get((gx, gy))
        if not pieces:
            return []
        else:
            if piece_type:
                pieces = [piece for piece in pieces if piece.piece_type == piece_type]
            if piece_subtype:
                pieces = [piece for piece in pieces if piece.piece_subtype == piece_subtype]
            if team:
                pieces = [piece for piece in pieces if piece.team == team]
            return pieces

    # Return the unit or building for the specified team (None if no piece for that team is present)
    def get_piece_at(self, gx, gy, team, piece_subtype=None):
        for piece in self.get_pieces_at(gx, gy):
            if piece.team == team and (not piece_subtype or piece.piece_subtype == piece_subtype):
                return piece
        return None

    # Return any enemy units or buildings at the location (not belonging to the provided team)
    def get_enemy_pieces_at(self, gx, gy, my_team, piece_type=None, piece_subtype=None):
        pieces = []
        for piece in self.get_pieces_at(gx, gy):
            if not piece.team == my_team:
                pieces.append(piece)

        if piece_type:
            pieces = [piece for piece in pieces if piece.piece_type == piece_type]
        if piece_subtype:
            pieces = [piece for piece in pieces if piece.piece_subtype == piece_subtype]

        return pieces

    # Return any pieces adjacent to the specified tile
    def get_adjacent_pieces(self, gx, gy, team=None):
        coords = [(gx + 1, gy), (gx - 1, gy), (gx, gy + 1), (gx, gy - 1)]
        pieces = []
        for coord in coords:
            pieces.extend(self.get_pieces_at(coord[0], coord[1], team=team))

        return pieces

    # Return any enemy pieces adjacent to the specified tile
    def get_adjacent_enemies(self, gx, gy, team):
        coords = [(gx + 1, gy), (gx - 1, gy), (gx, gy + 1), (gx, gy - 1)]
        pieces = []
        for coord in coords:
            pieces.extend(self.get_enemy_pieces_at(coord[0], coord[1], team))

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

    # Return all pieces not belonging to the specified team. Supports filtering down to a specific type or subtype.
    def get_all_enemy_pieces(self, team, piece_subtype=None, piece_type=None):
        all_pieces = []
        for coordinate, pieces in self.pieces.items():
            all_pieces.extend(pieces)

        # Filter
        all_pieces = [piece for piece in all_pieces if piece.team != team]
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

    # Return all pieces for the specified team, where the provided piece attribute is True.
    def get_all_pieces_with_attribute(self, team, attribute):
        return [piece for piece in self.get_all_pieces_for_team(team) if piece.attr(attribute)]

    # Return all pieces belonging to the provided archetype and team
    def get_all_pieces_by_archetype(self, team, archetype):
        return [piece for piece in self.get_all_pieces_for_team(team) if piece.piece_archetype == archetype]

    # Return a count of how many pieces this team has per archetype
    def get_archetype_counts(self, team, units_only=False):
        counts = Counter({
            PieceArchetype.GROUND: 0,
            PieceArchetype.RANGED: 0,
            PieceArchetype.MOBILITY: 0,
        })
        counts.update(Counter([piece.piece_archetype for piece in self.get_all_pieces_for_team(team)]))

        if units_only:
            return list(filter(lambda pair: pair[0] in [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY], counts.most_common()))
        else:
            return counts.most_common()

    # Return a count of how many pieces all enemies have per archetype
    def get_enemy_archetype_counts(self, my_team, units_only=False):
        counts = Counter({
            PieceArchetype.GROUND: 0,
            PieceArchetype.RANGED: 0,
            PieceArchetype.MOBILITY: 0,
        })
        counts.update(Counter([piece.piece_archetype for piece in self.get_all_enemy_pieces(my_team)]))

        if units_only:
            return list(filter(lambda pair: pair[0] in [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY], counts.most_common()))
        else:
            return counts.most_common()

    # Return a count of how many pieces this team has per type
    def get_piece_counts(self, team):
        counts = Counter()
        counts.update(Counter([piece.piece_type for piece in self.get_all_pieces_for_team(team)]))

        return counts.most_common()

    # Return the sum of all resource production for the specified team
    def get_income(self, team):
        return sum(piece.attr(Attribute.RESOURCE_PRODUCTION) for piece in self.get_all_pieces_for_team(team))

    # Register a piece with the game map.
    def register_piece(self, piece):
        if not self.pieces.get((piece.gx, piece.gy)):
            self.pieces[(piece.gx, piece.gy)] = []
        self.pieces[(piece.gx, piece.gy)].append(piece)

    # Unregister a piece with the game map. Note that this does not destroy it, just removes it from the grid.
    def remove_piece(self, piece):
        self.pieces[(piece.gx, piece.gy)].remove(piece)
        if len(self.pieces[(piece.gx, piece.gy)]) == 0:
            del self.pieces[(piece.gx, piece.gy)]

    # Unregister a piece with the game map by looking it up with grid coordinates and a team.
    def remove_piece_by_coord(self, gx, gy, team):
        piece = self.get_piece_at(gx, gy, team)
        if piece:
            self.remove_piece(piece)

    # Completely destroy a piece, removing it from the game map.
    def destroy_piece(self, piece):
        piece.destroy()
        self.remove_piece(piece)

    # Completely destroy a piece by looking it up with grid coordinates and a team.
    def destroy_piece_by_coord(self, gx, gy, team):
        piece = self.get_piece_at(gx, gy, team)
        if piece:
            self.destroy_piece(piece)

    # Move a piece on the game map from (gx, gy) to new coords (dx, dy)
    def move_piece(self, gx, gy, team, dx, dy):
        piece = self.get_piece_at(gx, gy, team, PieceSubtype.UNIT)
        if piece:
            self.remove_piece_by_coord(gx, gy, team)
            piece.gx = dx
            piece.gy = dy
            self.register_piece(piece)

    # Destroy all pieces belonging to the provided team
    def destroy_all_pieces_for_team(self, team):
        for piece in self.get_all_pieces_for_team(team):
            self.destroy_piece(piece)

    def register_piece_from_event(self, event):
        self.register_piece(Piece(event.new_piece_type, event.team, event.tx, event.ty))

    def remove_piece_from_event(self, event):
        self.remove_piece_by_coord(event.gx, event.gy, event.team)

    def destroy_piece_from_event(self, event):
        self.destroy_piece(event.piece)

    def move_piece_from_event(self, event):
        self.move_piece(event.gx, event.gy, event.team, event.dx, event.dy)

    def destroy_all_pieces(self):
        for piece in self.__get_all_pieces__():
            self.destroy_piece(piece)

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
                                                         int(piece.hp)))
        return piece_strings

    # Return true if all movement and build orders for the provided team are valid together.
    # This doesn't check for obviously illegal moves, like moving farther than your movement range allows.
    # Orders are all valid if:
    #       * No friendly units end up on the same tile
    #       * There are enough resources to build + research everything we want to build + research
    #       * Not attempting to research the same upgrade multiple times
    def validate_orders(self, team):
        coordinates = []
        spent_resources = []
        upgrades_bought = []

        for piece in self.get_all_pieces_for_team(team):
            if piece.current_order:
                if isinstance(piece.current_order, MoveOrder):
                    coordinates.append((piece.current_order.dx, piece.current_order.dy))
                elif isinstance(piece.current_order, BuildOrder):
                    # Build orders result in a piece on the designated tile, and the builder's tile
                    coordinates.append((piece.current_order.tx, piece.current_order.ty))
                    coordinates.append((piece.gx, piece.gy))

                    # Check that a team isn't spending more than they have
                    spent_resources.append(self.get_manager(Manager.TEAM).attr(piece.team, piece.current_order.new_piece_type, Attribute.PRICE))
                elif isinstance(piece.current_order, UpgradeOrder):
                    # Check that a team isn't spending more than they have
                    spent_resources.append(base_upgrades[piece.current_order.new_upgrade_type][UpgradeAttribute.UPGRADE_PRICE])
                    # Check that a team isn't building the same upgrade multiple times
                    upgrades_bought.append(piece.current_order.new_upgrade_type)
            else:
                coordinates.append((piece.gx, piece.gy))

        # Move orders are valid if all the coordinates are unique-- no duplicates are removed
        move_orders_valid = len(coordinates) == len(set(coordinates))

        # Build + upgrade orders are valid if there's enough resources to satisfy all orders
        build_orders_valid = self.get_manager(Manager.TEAM).can_spend_resources(team, spent_resources)

        # Upgrade orders are valid if all upgrades being bought are unique
        upgrades_bought_valid = len([k for k, v in Counter(upgrades_bought).items() if v > 1]) <= 0

        # Publish events containing the invalid orders, if any
        if not move_orders_valid:
            # Find and return the coordinates of the collision(s)
            collisions = [k for k, v in Counter(coordinates).items() if v > 1]

            publish_game_event(EventType.E_INVALID_MOVE_ORDERS, {
                'team': team,
                'invalid_coordinates': collisions
            })
            print("Invalid move orders: {}".format(collisions))
        if not build_orders_valid:
            publish_game_event(EventType.E_INVALID_BUILD_ORDERS, {
                'team': team,
                'spent_resources': spent_resources,
                'affected_pieces': [piece for piece in self.get_all_pieces_for_team(team)
                                    if isinstance(piece.current_order, (BuildOrder, UpgradeOrder))]
            })
            print("Invalid build orders: {}".format(spent_resources))
        if not upgrades_bought_valid:
            duplicate_upgrades = [k for k, v in Counter(upgrades_bought).items() if v > 1]

            publish_game_event(EventType.E_INVALID_UPGRADE_ORDERS, {
                'team': team,
                'duplicate_upgrades': duplicate_upgrades,
                'affected_pieces': [piece for piece in self.get_all_pieces_for_team(team)
                                    if isinstance(piece.current_order, UpgradeOrder) and
                                    piece.current_order.new_upgrade_type in duplicate_upgrades]
            })
            print("Invalid upgrade orders. Duplicates: {}".format(duplicate_upgrades))

        return move_orders_valid and build_orders_valid and upgrades_bought_valid

    # Check for overlapping enemy units, and resolve their combat
    def resolve_unit_combat(self, event):
        # Find conflicting units (units occupying the same space)
        conflicting_pieces = []
        for coordinate in self.pieces:
            if len(self.pieces.get(coordinate)) > 1:
                conflicting_pieces.append(self.pieces.get(coordinate))

        # Conflict resolution
        if len(conflicting_pieces) > 0:
            for conflicts in conflicting_pieces:
                teams = set([piece.team for piece in conflicts])
                # Edge case: two allied pieces briefly occupying the same location
                # This happens from building a new unit onto a tile where a piece is demolishing itself
                if len(teams) > 1:
                    self.play_sound(SoundType.PIECE_CONFLICT)
                    conflict = PieceConflict(conflicts)
                    conflict.resolve()

    # Conduct a ranged attack.
    # Event should contain grid coordinates gx and gy, the origin team, and target grid coordinates tx and ty.
    def ranged_attack(self, gx, gy, team, tx, ty):
        # Find the origin unit and the target pieces
        origin_unit = self.get_piece_at(gx, gy, team)
        target_pieces = self.get_enemy_pieces_at(tx, ty, team)

        splashed_pieces = []
        aoe_multiplier = self.get_manager(Manager.TEAM).attr(origin_unit.team, origin_unit.piece_type, Attribute.RANGED_AOE_MULTIPLIER)
        if aoe_multiplier > 0:
            splashed_pieces.extend(self.get_adjacent_enemies(tx, ty, team))

        def conduct_ranged_attack(target, modifier):
            attack = origin_unit.get_attack_rating(target)
            # Pieces with armor-piercing ignore defensive bonuses
            if self.get_manager(Manager.TEAM).attr(origin_unit.team, origin_unit.piece_type, Attribute.ARMOR_PIERCING):
                defense = 0
            else:
                defense = target.get_defense_rating()

            damage = int(attack * modifier * (1 - defense / 10))
            lifesteal = damage * origin_unit.attr(Attribute.LIFESTEAL)

            target.damage_hp(damage, origin_unit)
            if lifesteal > 0:
                origin_unit.heal(lifesteal)

        for target_piece in target_pieces:
            conduct_ranged_attack(target_piece, 1)
        for target_piece in splashed_pieces:
            conduct_ranged_attack(target_piece, aoe_multiplier)

    def conduct_ranged_attack_from_event(self, event):
        self.ranged_attack(event.gx, event.gy, event.team, event.tx, event.ty)

    def step(self, event):
        super().step(event)

        pieces = self.__get_all_pieces__()
        for piece in pieces:
            piece.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        pieces = self.__get_all_pieces__()
        for piece in pieces:
            piece.render(game_screen, ui_screen)
