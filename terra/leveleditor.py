import pygame
from terra.settings import *
from terra.constants import *
from terra.event import *
from terra.map.map import Map, load_map_from_file
from terra.ui.cursor import Cursor
from terra.map.tiletype import TileType
from terra.resources.assets import clear_color, spr_tiles, spr_cursor
from terra.util.mathutil import clamp


class LevelEditor:
    def __init__(self, mapname="map5.txt"):
        super().__init__()

        bitmap, _, _, _ = load_map_from_file(mapname)
        self.map = Map(bitmap)
        self.mapname = mapname
        self.cursor = Cursor(self.map)
        self.current_tile_type = TileType.GRASS
        self.secondary_tile_type = TileType.SEA

    def step(self, event):
        self.map.step(event)
        self.cursor.step(event)

        if is_event_type(event, E_SELECT):
            self.map.update_tile_type(int(self.cursor.gx), int(self.cursor.gy), self.current_tile_type)
        elif is_event_type(event, E_CANCEL):
            self.map.update_tile_type(int(self.cursor.gx), int(self.cursor.gy), self.secondary_tile_type)
        elif event.type == KEYDOWN:
            if event.key in KB_SCROLL_UP and pygame.key.get_mods() & KMOD_CTRL:
                self.secondary_tile_type = self.update_tile_type(self.secondary_tile_type, 1)
            elif event.key in KB_SCROLL_DOWN and pygame.key.get_mods() & KMOD_CTRL:
                self.secondary_tile_type = self.update_tile_type(self.secondary_tile_type, -1)
            elif event.key in KB_SCROLL_UP:
                self.current_tile_type = self.update_tile_type(self.current_tile_type, 1)
            elif event.key in KB_SCROLL_DOWN:
                self.current_tile_type = self.update_tile_type(self.current_tile_type, -1)
            elif event.key in KB_MENU:
                self.save_map()

    def update_tile_type(self, tiletype, amount):
        new_tile_type = clamp(tiletype.value + amount, 0, len(TileType) - 1)

        if not new_tile_type == tiletype:
            return TileType(new_tile_type)

    def save_map(self):
        bitmap = self.map.convert_bitmap_from_grid()

        with open("resources/maps/" + self.mapname, 'w') as mapfile:
            lines = ""
            for row in bitmap:
                line = ""
                for column in row:
                    line += "{} ".format(column)
                line += "\n"
                lines += line

            lines += "# Units\n# Buildings\n# Teams\nRED\nBLUE"

            mapfile.write(lines)

    def render(self, ui_screen):
        # Generate a screen of the size of the map
        map_screen = pygame.Surface((self.map.width * GRID_WIDTH, self.map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)
        self.map.render(map_screen, ui_screen)
        self.cursor.render(map_screen, ui_screen)

        # Render the current tile at the bottom of the screen
        ui_screen.fill(clear_color[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        ui_screen.blit(spr_tiles[self.current_tile_type][0], (0, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_tiles[self.secondary_tile_type][0], (GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[Team.BLUE], (GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Trim the screen to just the camera area
        return map_screen.subsurface((self.cursor.camera_x, self.cursor.camera_y,
                                      min(RESOLUTION_WIDTH, map_screen.get_size()[0]),
                                      min(RESOLUTION_HEIGHT, map_screen.get_size()[1])))
