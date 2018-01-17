from terra.map.movementtype import MovementType
from terra.map.tile import Tile
from terra.map.tiletype import TileType
from terra.engine.gameobject import GameObject
import random

impassible_terrain_types = {
    None: [],
    MovementType.GROUND: [TileType.SEA],
    MovementType.GHOST: [TileType.SEA]
}


# A single map containing tiles, organized into a grid.
class Map(GameObject):
    def __init__(self, bitmap=None, width=10, height=10):
        super().__init__()

        # Use a provided bitmap to generate tiles, otherwise generate one of the provided size
        # These are only integers (not tiles) for faster modification.
        if bitmap:
            self.bitmap = bitmap
        else:
            self.bitmap = self.generate_bitmap(width, height)

        self.height = len(self.bitmap)
        self.width = len(self.bitmap[0])

        # Serialize the map to Tile objects (from integers)
        self.tile_grid = self.convert_grid_from_bitmap(self.bitmap)

    # Generate a map of the required size
    def generate_bitmap(self, width, height):
        bitmap = []
        for _ in range(height):
            row = []
            for _ in range(width):
                tile = random.randint(1, 3)
                row.append(tile)
            bitmap.append(row)

        return bitmap

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
               not self.get_tile_type_at(gx, gy) in impassible_terrain_types[movement_type]

    def step(self, event):
        super().step(event)

    # Render the map to the screen
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        for x in range(self.width):
            for y in range(self.height):
                # print("x: {}, y: {}".format(x, y))
                self.tile_grid[y][x].render(game_screen, ui_screen)
