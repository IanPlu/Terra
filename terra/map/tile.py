from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.engine.animatedgameobject import AnimatedGameObject
from terra.map.tiletype import TileType
from terra.resources.assets import spr_tiles, spr_coast_detail


# A single tile on the map.
class Tile(AnimatedGameObject):
    # Create a new Tile object at the provided grid coordinates
    def __init__(self, game_map, tile_type=1, gx=0, gy=0):
        self.game_map = game_map
        self.tile_type = TileType(tile_type)
        self.gx = gx
        self.gy = gy

        super().__init__(spr_tiles[self.tile_type], 2)

    # Ask the Tile to render itself.
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        game_screen.blit(self.sprite,
                         (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        # For SEA tiles, render coastlines if adjacent to non-sea (map border counts as sea)
        if self.tile_type == TileType.SEA:
            # Use a 4-bit address to determine the coast sprite to use.
            # Each direction is one binary place: NESW
            # 0=no coast, 1=yes coast
            coast_index = 0

            north_type = self.game_map.get_tile_type_at(self.gx, self.gy-1)
            east_type = self.game_map.get_tile_type_at(self.gx+1, self.gy)
            south_type = self.game_map.get_tile_type_at(self.gx, self.gy+1)
            west_type = self.game_map.get_tile_type_at(self.gx-1, self.gy)

            if north_type and north_type != TileType.SEA:
                coast_index += 8
            if east_type and east_type != TileType.SEA:
                coast_index += 4
            if south_type and south_type != TileType.SEA:
                coast_index += 2
            if west_type and west_type != TileType.SEA:
                coast_index += 1

            if coast_index > 0:
                game_screen.blit(spr_coast_detail[coast_index], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))
