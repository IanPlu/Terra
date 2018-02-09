from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.piece.movementtype import MovementType
from terra.piece.piecesubtype import PieceSubtype
from terra.resources.assets import spr_tile_selectable


# Controllable tile selection UI.
# Displays a range of tiles that can be chosen. Created at an anchor point with a min and max
# range. Optionally account for terrain and units without orders.
# When complete, fires an event containing the coordinates of the selected tile.
class TileSelection(GameObject):
    def __init__(self, gx, gy, min_range, max_range, game_map,
                 movement_type=None, team=None, piece_manager=None, option=None):
        super().__init__()
        self.gx = gx
        self.gy = gy
        self.game_map = game_map
        self.min_range = min_range
        self.max_range = max_range

        # Only required for accounting for movement costs / impassable terrain
        self.movement_type = movement_type

        # Only required for accounting for friendly units without orders
        self.piece_manager = piece_manager
        self.team = team

        # Menu option event to fire back on completion
        self.option = option

        self.coordinate_set = self.__generate_coordinate_set__()
        return

    # Return the initial list of coordinates that cannot be selected
    def __generate_excluded_coordinates__(self):
        excluded_coordinates = set()

        # if it's not movement, only exclude our own tile
        if not self.movement_type:
            return {(self.gx, self.gy)}
        # Otherwise exclude friendly buildings from selection
        else:
            for building in self.piece_manager.get_all_pieces_for_team(self.team, PieceSubtype.BUILDING):
                excluded_coordinates.add((building.gx, building.gy))

            # Ghosts cannot occupy the same space as enemy buildings
            if self.movement_type is MovementType.GHOST:
                for building in self.piece_manager.get_all_enemy_pieces(self.team, PieceSubtype.BUILDING):
                    excluded_coordinates.add((building.gx, building.gy))

        return excluded_coordinates

    # Generate a list of the coordinates of all tiles available to select
    def __generate_coordinate_set__(self):
        possible_coordinates = {(self.gx, self.gy)}
        excluded_coordinates = self.__generate_excluded_coordinates__()

        def traverse_tile(gx, gy, remaining_range, min_range, max_range,
                          game_map, movement_type, team, piece_manager, first_move):
            # If we're out of tile range to use, return
            if remaining_range <= 0:
                return
            # If the tile is impassible, return (tiles off the edge are impassible too)
            elif not game_map.is_tile_passable(gx, gy, movement_type) and not first_move:
                return
            # Otherwise, add the current tile to the selectable list, and iterate in all four directions
            else:
                possible_coordinates.add((gx, gy))

                # Caveat: if the tile is inside the minimum range, add it to the exclusion set
                if remaining_range > max_range + 1 - min_range:
                    excluded_coordinates.add((gx, gy))

                # If there's an enemy unit on this tile, we can move onto it, but no further (unless we're a GHOST)
                elif not first_move and movement_type and team and movement_type is not MovementType.GHOST and \
                        len(piece_manager.get_enemy_pieces_at(gx, gy, team)) > 0:
                    return

                traverse_tile(gx + 1, gy, remaining_range - 1, min_range, max_range,
                              game_map, movement_type, team, piece_manager, False)
                traverse_tile(gx - 1, gy, remaining_range - 1, min_range, max_range,
                              game_map, movement_type, team, piece_manager, False)
                traverse_tile(gx, gy + 1, remaining_range - 1, min_range, max_range,
                              game_map, movement_type, team, piece_manager, False)
                traverse_tile(gx, gy - 1, remaining_range - 1, min_range, max_range,
                              game_map, movement_type, team, piece_manager, False)

        traverse_tile(self.gx, self.gy, self.max_range + 1, self.min_range, self.max_range,
                      self.game_map, self.movement_type, self.team, self.piece_manager, True)

        return possible_coordinates - excluded_coordinates

    def confirm(self, event):
        publish_game_event(E_SELECT_TILE, {
            'gx': self.gx,
            'gy': self.gy,
            'option': self.option,
            'team': self.team,
            'dx': event.gx,
            'dy': event.gy,
        })

    # noinspection PyMethodMayBeStatic
    def cancel(self):
        publish_game_event(E_CANCEL_TILE_SELECTION, {})

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_SELECT):
            if (event.gx, event.gy) in self.coordinate_set and \
                    event.team == self.team and event.selecting_movement:
                self.confirm(event)
        elif is_event_type(event, E_CANCEL):
            self.cancel()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        subscreen = pygame.Surface((game_screen.get_rect().width, game_screen.get_rect().height), pygame.SRCALPHA)
        subscreen.fill((0, 0, 0, 0))

        for x, y in self.coordinate_set:
            subscreen.blit(spr_tile_selectable, (x * GRID_WIDTH, y * GRID_HEIGHT))

        game_screen.blit(subscreen, (0, 0))
