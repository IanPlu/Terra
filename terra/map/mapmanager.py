from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.map.maputils import generate_bitmap_from_simplex_noise
from terra.map.tile import Tile
from terra.map.tiletype import TileType
from terra.piece.movementtype import movement_types, MovementAttribute
from terra.resources.assets import spr_grid
from terra.settings import SETTINGS, Setting


# A single map containing tiles, organized into a grid.
class MapManager(GameObject):
    def __init__(self, bitmap=None, width=10, height=10):
        super().__init__()

        # Use a provided bitmap to generate tiles, otherwise generate one of the provided size
        # These are only integers (not tiles) for faster modification.
        if bitmap:
            self.bitmap = bitmap
        else:
            self.bitmap = generate_bitmap_from_simplex_noise(width, height)

        self.height = len(self.bitmap)
        self.width = len(self.bitmap[0])

        # Serialize the map to Tile objects (from integers)
        self.tile_grid = self.convert_grid_from_bitmap(self.bitmap)

        # Adjust the grid opacity
        spr_grid.set_alpha(256 * SETTINGS.get(Setting.GRID_OPACITY) / 100)

    def destroy(self):
        super().destroy()
        for row in self.tile_grid:
            for tile in row:
                tile.destroy()

            del row

        del self.tile_grid
        self.tile_grid = []

    def register_handlers(self, event_bus):
        event_bus.register_handler(EventType.E_TILE_MINED, self.mine_tile)

    # Given a 2D array of ints, convert it to a 2D array of Tile objects
    def convert_grid_from_bitmap(self, bitmap):
        grid = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = Tile(self, bitmap[y][x], x, y)
                row.append(tile)
            grid.append(row)

        return grid

    # Serialize ourselves into a bitmap (2D array of ints)
    def convert_bitmap_from_grid(self):
        bitmap = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                row.append(tile.tile_type.value)
            bitmap.append(row)

        return bitmap

    # Return a flattened list of all tiles in the map
    def get_all_tiles(self):
        all_tiles = []
        for tiles in self.tile_grid:
            for tile in tiles:
                all_tiles.append(tile)
        return all_tiles

    # Return the tile at the specified grid location.
    def get_tile_at(self, gx, gy):
        if 0 <= gx < self.width and 0 <= gy < self.height:
            return self.tile_grid[gy][gx]
        else:
            return None

    # Return the tile type at the specified grid location.
    def get_tile_type_at(self, gx, gy):
        return getattr(self.get_tile_at(gx, gy), 'tile_type', None)

    # Return True if the tile is passable for the provided movement type. Tiles out of bounds are impassible.
    def is_tile_passable(self, gx, gy, movement_type):
        return 0 <= gx < self.width and 0 <= gy < self.height and \
               self.get_tile_type_at(gx, gy) in movement_types[movement_type][MovementAttribute.PASSABLE]

    # Return true if our movement type can pass over the tile, but not end movement on it
    def is_tile_traversable(self, gx, gy, movement_type):
        return 0 <= gx < self.width and 0 <= gy < self.height and \
               self.get_tile_type_at(gx, gy) in movement_types[movement_type][MovementAttribute.TRAVERSABLE]

    # From the tiles adjacent to (gx, gy), return any that are passable for the provided movement type
    def get_valid_adjacent_tiles_for_movement_type(self, gx, gy, movement_type):
        return self.get_tiles_in_range(gx, gy, 1, 1, movement_type, include_traversable=False)

    def get_valid_adjacent_traversable_tiles(self, gx, gy, movement_type):
        return self.get_tiles_in_range(gx, gy, 1, 1, movement_type, include_traversable=True)

    # Return tile types for all tiles within the min and max range of the center coord
    def get_tiles_in_range(self, cx, cy, min_range, max_range, movement_type=None, include_traversable=False):
        tiles = []
        for y in range(self.height):
            for x in range(self.width):
                within_range = min_range <= abs(cx - x) + abs(cy - y) <= max_range
                is_passable = not movement_type or self.is_tile_passable(x, y, movement_type)
                is_traversable = include_traversable and (not movement_type or self.is_tile_traversable(x, y, movement_type))

                if within_range and (is_passable or is_traversable):
                    tiles.append((x, y))

        return tiles

    # Return the number of generally passable tiles (non-SEA, non-MOUNTAIN)
    def get_map_size(self):
        return len([tile for tile in self.get_all_tiles() if tile.tile_type not in [TileType.SEA, TileType.MOUNTAIN]])

    # Return a list of coordinates of tiles of the specified type
    def find_tiles_by_type(self, tile_type):
        coords = []
        for y in range(self.height):
            for x in range(self.width):
                if self.get_tile_type_at(x, y) == tile_type:
                    coords.append((x, y))

        return coords

    # Update the tile at the specified location to the new type
    def update_tile_type(self, gx, gy, new_tile_type):
        self.tile_grid[gy][gx] = Tile(self, new_tile_type, gx, gy)

    # Mine out a tile according to an event
    def mine_tile(self, event):
        if self.get_tile_type_at(event.gx, event.gy) == TileType.METEOR:
            self.update_tile_type(event.gx, event.gy, TileType.GRASS)

    # Replace all tiles with the provided tiletype.
    def fill_map_with_tile(self, new_tile_type):
        for x in range(self.width):
            for y in range(self.height):
                self.update_tile_type(x, y, new_tile_type)

    # Mirror the map across the specified axes, prioritizing the top-left-most tiles.
    def mirror_map(self, mirror_x=True, mirror_y=False):
        for x in range(self.width):
            for y in range(self.height):
                mx = self.width - 1 - x if mirror_x else x
                my = self.height - 1 - y if mirror_y else y
                self.update_tile_type(mx, my, self.get_tile_type_at(x, y))

    # Render the map to the screen
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for x in range(self.width):
            for y in range(self.height):
                self.tile_grid[y][x].render(game_screen, ui_screen)
