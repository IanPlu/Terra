from terra.settings import *
from terra.engine.gameobject import GameObject
from terra.map.movementtype import MovementType
from terra.event import *
from terra.resources.assets import spr_tile_selectable


# Controllable tile selection UI.
# Displays a range of tiles that can be chosen. Created at an anchor point with a min and max
# range. Optionally account for terrain and units without orders.
# When complete, fires an event containing the coordinates of the selected tile.
class TileSelection(GameObject):
    def __init__(self, gx, gy, min_range, max_range, game_map, movement_type=None, team=None, army=None, option=None):
        super().__init__()
        self.gx = gx
        self.gy = gy
        self.game_map = game_map
        self.min_range = min_range
        self.max_range = max_range

        # Only required for accounting for movement costs / impassable terrain
        self.movement_type = movement_type

        # Only required for accounting for friendly units without orders
        self.army = army
        self.team = team

        # Menu option event to fire back on completion
        self.option = option

        self.coordinate_set = self.__generate_coordinate_set__()
        return

    # Generate a list of the coordinates of all tiles available to select
    def __generate_coordinate_set__(self):
        possible_coordinates = set()
        excluded_coordinates = {(self.gx, self.gy)}

        def traverse_tile(gx, gy, remaining_range, min_range, max_range, game_map, movement_type, team, army, first_move):
            # If we're out of tile range to use, return
            if remaining_range <= 0:
                return
            # If the tile is impassible, return (tiles off the edge are impassible too)
            elif not game_map.is_tile_passable(gx, gy, movement_type):
                return
            # Otherwise, add the current tile to the selectable list, and iterate in all four directions
            else:
                possible_coordinates.add((gx, gy))

                # Caveat: if the tile is inside the minimum range, add it to the exclusion set
                if remaining_range > max_range + 1 - min_range:
                    excluded_coordinates.add((gx, gy))

                # If there's an enemy unit on this tile, we can move onto it, but no further
                if not first_move and movement_type and team and movement_type is not MovementType.GHOST and \
                        len(army.get_enemy_units_at(gx, gy, team)) > 0:
                    return

                traverse_tile(gx + 1, gy, remaining_range - 1, min_range, max_range, game_map, movement_type, team, army, False)
                traverse_tile(gx - 1, gy, remaining_range - 1, min_range, max_range, game_map, movement_type, team, army, False)
                traverse_tile(gx, gy + 1, remaining_range - 1, min_range, max_range, game_map, movement_type, team, army, False)
                traverse_tile(gx, gy - 1, remaining_range - 1, min_range, max_range, game_map, movement_type, team, army, False)

        traverse_tile(self.gx, self.gy, self.max_range + 1,
                      self.min_range, self.max_range, self.game_map, self.movement_type, self.team, self.army, True)

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

    def cancel(self, event):
        publish_game_event(E_CANCEL_TILE_SELECTION, {})

    def step(self, event):
        super().step(event)

        # TODO: If event is a selection event and it's for one of our tiles, fire the selection event
        # If we catch a cancel button press, fire the cancel selection event
        if is_event_type(event, E_SELECT):
            if (event.gx, event.gy) in self.coordinate_set and \
                    event.team == self.team and event.selecting_movement:
                self.confirm(event)
        elif is_event_type(event, E_CANCEL):
            self.cancel(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        subscreen = pygame.Surface((game_screen.get_rect().width, game_screen.get_rect().height), pygame.SRCALPHA)
        subscreen.fill((0, 0, 0, 0))

        for x, y in self.coordinate_set:
            subscreen.blit(spr_tile_selectable, (x * GRID_WIDTH, y * GRID_HEIGHT))

        game_screen.blit(subscreen, (0, 0))