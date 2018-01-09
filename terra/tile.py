import pygame
from terra.settings import *
from terra.gameobject import GameObject
from enum import Enum


class TileType(Enum):
    NONE = 0
    SEA = 1
    GRASS = 2
    WOODS = 3


tile_sprites = {
    TileType.NONE: pygame.image.load("resources/sprites/tiles/Tile_None.png"),
    TileType.SEA: pygame.image.load("resources/sprites/tiles/Tile_Sea.png"),
    TileType.GRASS: pygame.image.load("resources/sprites/tiles/Tile_Grass.png"),
    TileType.WOODS: pygame.image.load("resources/sprites/tiles/Tile_Woods.png")
}

coast_detail_sprites = {
    0: None,
    1: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail1.png"),
    2: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail2.png"),
    3: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail3.png"),
    4: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail4.png"),
    5: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail5.png"),
    6: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail6.png"),
    7: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail7.png"),
    8: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail8.png"),
    9: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail9.png"),
    10: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail10.png"),
    11: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail11.png"),
    12: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail12.png"),
    13: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail13.png"),
    14: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail14.png"),
    15: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail15.png"),
}


# A single tile on the map.
class Tile(GameObject):
    # Create a new Tile object at the provided grid coordinates
    def __init__(self, game_map, tile_type=1, gx=0, gy=0):
        super().__init__()
        self.game_map = game_map
        self.tile_type = TileType(tile_type)
        self.gx = gx
        self.gy = gy

    # Ask the Tile to render itself.
    def render(self, screen):
        super().render(screen)
        screen.blit(tile_sprites[self.tile_type],
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
                screen.blit(coast_detail_sprites[coast_index], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))
