import pygame

from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.managers import Managers
from terra.piece.attribute import Attribute
from terra.piece.movementtype import MovementType
from terra.piece.piecesubtype import PieceSubtype
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

        self.coordinate_set = self.__generate_coordinate_set__()

        # Abort immediately if there are no valid selectable tiles
        if len(self.coordinate_set) == 0:
            self.cancel()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_SELECT, self.confirm)
        event_bus.register_handler(EventType.E_CANCEL, self.cancel)

    # Return the initial list of coordinates that cannot be selected
    def __generate_excluded_coordinates__(self):
        excluded_coordinates = set()

        # if it's not movement, only exclude our own tile
        if not self.movement_type or self.movement_type in [MovementType.RAISE, MovementType.LOWER, MovementType.BUILDING, MovementType.GENERATOR]:
            return {(self.gx, self.gy)}
        # Otherwise exclude friendly buildings from selection
        else:
            for building in Managers.piece_manager.get_all_pieces_for_team(self.team, PieceSubtype.BUILDING):
                excluded_coordinates.add((building.gx, building.gy))

            # Some pieces cannot occupy the same space as enemy buildings
            if self.piece_type and Managers.team_manager.attr(self.team, self.piece_type, Attribute.CANT_ATTACK_BUILDINGS):
                for building in Managers.piece_manager.get_all_enemy_pieces(self.team, PieceSubtype.BUILDING):
                    excluded_coordinates.add((building.gx, building.gy))

        return excluded_coordinates

    # Generate a list of the coordinates of all tiles available to select
    def __generate_coordinate_set__(self):
        possible_coordinates = {(self.gx, self.gy)}
        excluded_coordinates = self.__generate_excluded_coordinates__()

        def traverse_tile(gx, gy, remaining_range, min_range, max_range, movement_type, piece_type, team, first_move):
            # If we're out of tile range to use, return
            if remaining_range <= 0:
                return
            # If the tile is passable, add the current tile to the selectable list, and iterate in all four directions
            elif Managers.battle_map.is_tile_passable(gx, gy, movement_type) or \
                    Managers.battle_map.is_tile_traversable(gx, gy, movement_type) or first_move:
                possible_coordinates.add((gx, gy))

                # Caveat: if the tile is inside the minimum range, add it to the exclusion set
                # Also add it to the exclusion set if it's only traversable, not passable
                if remaining_range > max_range + 1 - min_range or \
                        Managers.battle_map.is_tile_traversable(gx, gy, movement_type):
                    excluded_coordinates.add((gx, gy))

                # If there's an enemy unit on this tile, we can move onto it but no further (unless we ignore impedance)
                if len(Managers.piece_manager.get_enemy_pieces_at(gx, gy, team)) > 0 and \
                        not first_move and piece_type and movement_type and \
                        not Managers.team_manager.attr(team, piece_type, Attribute.IGNORE_IMPEDANCE):
                        return

                traverse_tile(gx + 1, gy, remaining_range - 1, min_range, max_range,
                              movement_type, piece_type, team, False)
                traverse_tile(gx - 1, gy, remaining_range - 1, min_range, max_range,
                              movement_type, piece_type, team, False)
                traverse_tile(gx, gy + 1, remaining_range - 1, min_range, max_range,
                              movement_type, piece_type, team, False)
                traverse_tile(gx, gy - 1, remaining_range - 1, min_range, max_range,
                              movement_type, piece_type, team, False)

            # If the tile isn't passable or traversable, end iteration here and return
            else:
                return

        traverse_tile(self.gx, self.gy, self.max_range + 1, self.min_range, self.max_range,
                      self.movement_type, self.piece_type, self.team, True)

        return possible_coordinates - excluded_coordinates

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
