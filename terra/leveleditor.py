from pygame.constants import KEYDOWN, KMOD_CTRL

from terra.constants import GRID_WIDTH, GRID_HEIGHT, RESOLUTION_WIDTH, RESOLUTION_HEIGHT, MAP_PATH
from terra.engine.gamescreen import GameScreen
from terra.event import *
from terra.keybindings import KB_MENU, KB_SCROLL_UP, KB_SCROLL_DOWN
from terra.managers.managers import Managers
from terra.managers.mapmanager import load_map_from_file
from terra.map.tiletype import TileType
from terra.resources.assets import clear_color, spr_tiles, spr_cursor
from terra.team import Team
from terra.util.mathutil import clamp


# A map editor for Terra maps.
# Allows placing tiles of different types and saving / loading maps.
class LevelEditor(GameScreen):
    def __init__(self, map_name="edited_map.map"):
        super().__init__()

        bitmap, pieces, teams = load_map_from_file(map_name)
        Managers.initialize_managers(bitmap, pieces, teams, map_name)

        self.current_tile_type = TileType.GRASS
        self.secondary_tile_type = TileType.SEA

    def step(self, event):
        super().step(event)

        Managers.step(event)

        if is_event_type(event, E_SELECT):
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            Managers.battle_map.update_tile_type(cursor_x, cursor_y, self.current_tile_type)
        elif is_event_type(event, E_CANCEL):
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            Managers.battle_map.update_tile_type(cursor_x, cursor_y, self.secondary_tile_type)
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
                Managers.save_game()

    def update_tile_type(self, tiletype, amount):
        new_tile_type = clamp(tiletype.value + amount, 0, len(TileType) - 1)

        if not new_tile_type == tiletype:
            return TileType(new_tile_type)

    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map_screen = pygame.Surface((Managers.battle_map.width * GRID_WIDTH, Managers.battle_map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)
        Managers.render(map_screen, ui_screen)

        # Render the current tile at the bottom of the screen
        ui_screen.fill(clear_color[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        ui_screen.blit(spr_tiles[self.current_tile_type][0], (0, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_tiles[self.secondary_tile_type][0], (GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[Team.BLUE], (GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Trim the screen to just the camera area
        camera_x, camera_y = Managers.player_manager.get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(RESOLUTION_WIDTH, map_screen.get_size()[0]),
                                      min(RESOLUTION_HEIGHT, map_screen.get_size()[1])))
