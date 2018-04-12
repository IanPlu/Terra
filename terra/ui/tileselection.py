from queue import PriorityQueue

import pygame

from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.piece.attribute import Attribute
from terra.piece.movementtype import MovementType
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_tile_selectable


# Controllable tile selection UI.
# Displays a range of tiles that can be chosen. Created at an anchor point with a min and max
# range. Optionally account for terrain and units without orders.
# When complete, fires an event containing the coordinates of the selected tile.
class TileSelection(GameObject):
    def __init__(self, gx, gy, min_range, max_range, movement_type=None, piece_type=None, team=None, option=None):
        super().__init__()
        self.gx = gx
        self.gy = gy
        self.min_range = min_range
        self.max_range = max_range

        # Only required for accounting for movement costs / impassable terrain
        self.movement_type = movement_type
        self.piece_type = piece_type

        self.team = team

        # Menu option event to fire back on completion
        self.option = option

        self.coordinate_set = self.__navigate__()

        # Abort immediately if there are no valid selectable tiles
        if len(self.coordinate_set) == 0:
            self.cancel(None)

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_SELECT, self.confirm)
        event_bus.register_handler(EventType.E_CANCEL, self.cancel)

    def __can_be_impeded__(self):
        return self.piece_type and self.movement_type and not self.get_manager(Manager.TEAM).attr(self.team, self.piece_type, Attribute.IGNORE_IMPEDANCE)

    # Use Dijkstra's algorithm to navigate the map for tile selection, with some rules caveats
    # https://www.redblobgames.com/pathfinding/a-star/introduction.html
    def __navigate__(self):
        frontier = PriorityQueue()
        frontier.put((self.gx, self.gy), 0)
        cost_so_far = {(self.gx, self.gy): 0}
        traversable = set()
        excluded_coordinates = self.__generate_excluded_coordinates__()

        # If we have a piece with the 'PORTAL' attribute, we need to look out for potential portal tiles
        portal_coords = self.__generate_portal_coordinates__()

        while not frontier.empty():
            current = frontier.get()
            neighbors = self.get_manager(Manager.MAP).get_valid_adjacent_tiles_for_movement_type(current[0], current[1], self.movement_type)

            # If there's a friendly base on this tile, add any portal coords to the neighbors
            if len(portal_coords) > 0 and len(self.get_manager(Manager.PIECE).get_pieces_at(current[0], current[1],
                                                                                   PieceType.BASE, self.team)) > 0:
                neighbors.extend(portal_coords)

            for next in neighbors:
                new_cost = cost_so_far[current] + 1
                if (next not in cost_so_far or new_cost < cost_so_far[next]) and new_cost <= self.max_range:
                    cost_so_far[next] = new_cost
                    traversable.add(next)

                    # If there's an enemy on this tile, and we are susceptible to impedance, don't investigate past it
                    if not (len(self.get_manager(Manager.PIECE).get_enemy_pieces_at(next[0], next[1], self.team)) > 0 and self.__can_be_impeded__()):
                        frontier.put(next, new_cost)

                    # If this tile is within our minimum range, add it to the exclusion list
                    if new_cost < self.min_range:
                        excluded_coordinates.add(next)

        # Remove previously excluded coordinates from the list
        return traversable - excluded_coordinates

    # Return the initial list of coordinates that cannot be selected
    def __generate_excluded_coordinates__(self):
        excluded_coordinates = set()

        # if it's not movement, only exclude our own tile
        if not self.movement_type or self.movement_type in [MovementType.RAISE, MovementType.LOWER, MovementType.BUILDING, MovementType.GENERATOR]:
            return {(self.gx, self.gy)}
        # Otherwise exclude friendly buildings from selection
        else:
            for building in self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team, PieceSubtype.BUILDING):
                excluded_coordinates.add((building.gx, building.gy))

            # Some pieces cannot occupy the same space as enemy buildings
            if self.piece_type and self.get_manager(Manager.TEAM).attr(self.team, self.piece_type, Attribute.CANT_ATTACK_BUILDINGS):
                for building in self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team, PieceSubtype.BUILDING):
                    excluded_coordinates.add((building.gx, building.gy))

        return excluded_coordinates

    # Return the list of coordinates where we have pieces with the 'PORTAL' attribute
    def __generate_portal_coordinates__(self):
        if self.movement_type and self.piece_type:
            return [(piece.gx, piece.gy) for piece in self.get_manager(Manager.PIECE).get_all_pieces_with_attribute(self.team, Attribute.PORTAL)]
        else:
            return []

    def confirm(self, event):
        if (event.gx, event.gy) in self.coordinate_set and \
                event.team == self.team and event.selecting_movement:
            publish_game_event(EventType.E_SELECT_TILE, {
                'gx': self.gx,
                'gy': self.gy,
                'option': self.option,
                'team': self.team,
                'dx': event.gx,
                'dy': event.gy,
            })

    def cancel(self, event):
        publish_game_event(EventType.E_CANCEL_TILE_SELECTION, {})

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        subscreen = pygame.Surface((game_screen.get_rect().width, game_screen.get_rect().height), pygame.SRCALPHA)
        subscreen.fill((0, 0, 0, 0))

        for x, y in self.coordinate_set:
            subscreen.blit(spr_tile_selectable, (x * GRID_WIDTH, y * GRID_HEIGHT))

        game_screen.blit(subscreen, (0, 0))
