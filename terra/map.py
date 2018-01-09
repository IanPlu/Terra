from terra.tile import Tile
from terra.gameobject import GameObject
import random


# A single map containing units and tiles, organized into a grid.
class Map(GameObject):
    def __init__(self, mapname=None, width=10, height=10):
        super().__init__()

        # Load a map if a name is provided, otherwise generate one of the provided size
        if mapname:
            self.bitmap = self.generate_bitmap_from_file(mapname)

        else:
            self.bitmap = self.generate_bitmap(width, height)

        self.height = len(self.bitmap)
        self.width = len(self.bitmap[0])
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

    # Generate a map from the provided filename
    # TODO: Add error handling
    def generate_bitmap_from_file(self, mapname):
        with open("resources/maps/" + mapname) as mapfile:
            bitmap = []
            for line in mapfile:
                # Grab all non-newline chars, convert them to ints, and add them to the line list
                bitmap.append(list(map(int, line.rstrip().split(' '))))

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

    # Render the map to the screen
    def render(self, screen):
        super().render(screen)
        for x in range(self.width):
            for y in range(self.height):
                self.tile_grid[x][y].render(screen)





