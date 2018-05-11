import pygame

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
from terra.managers.session import SESSION, Session, Manager
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.resources.assets import clear_color, spr_tiles, spr_cursor, spr_pieces
from terra.team.team import Team
from threading import Timer
from terra.settings import SETTINGS, Setting


# A map editor for Terra maps.
# Allows placing tiles of different types and saving / loading maps.
class LevelEditor(GameScreen):
    def __init__(self, map_name):
        super().__init__()

        Session.set_up_level_editor(map_name)

        # Begin scheduling autosaves
        if SETTINGS.get(Setting.AUTOSAVE_INTERVAL) > 0:
            self.autosave()

    def destroy(self):
        super().destroy()
        if SESSION:
            SESSION.reset()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_CLOSE_MENU, self.handle_menu_selection)

    def handle_menu_selection(self, event):
        if event.option == Option.MENU_SAVE_MAP:
            SESSION.save_map_to_file()
        elif event.option == Option.MENU_QUIT_BATTLE:
            publish_game_event(EventType.E_QUIT_BATTLE, {})
        elif event.option == Option.MENU_FILL_WITH_CURRENT_TILE:
            self.fill_with_current_tile()
        elif event.option == Option.MENU_DESTROY_ALL_PIECES:
            self.clear_all_pieces()
        elif event.option == Option.MENU_MIRROR_X:
            self.mirror_map(mirror_x=True, mirror_y=False)
        elif event.option == Option.MENU_MIRROR_Y:
            self.mirror_map(mirror_x=False, mirror_y=True)

    def step(self, event):
        super().step(event)

        SESSION.step(event)

    def fill_with_current_tile(self):
        cursor = self.get_manager(Manager.PLAYER).cursors[Team.RED]
        self.get_manager(Manager.MAP).fill_map_with_tile(cursor.tile_type[0])

    def clear_all_pieces(self):
        self.get_manager(Manager.PIECE).destroy_all_pieces()

    def mirror_map(self, mirror_x=True, mirror_y=False):
        self.get_manager(Manager.MAP).mirror_map(mirror_x, mirror_y)

    def get_tile_sprite_for_tiletype(self, tiletype):
        if tiletype in [TileType.COAST]:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)
        else:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)

    def get_piece_sprite_for_piecetype(self, piecetype, team):
        return spr_pieces[team][piecetype]

    def autosave(self):
        if SESSION.is_active():
            timer = Timer(SETTINGS.get(Setting.AUTOSAVE_INTERVAL), self.autosave)
            timer.daemon = True
            timer.start()

            SESSION.save_map_to_file(autosave=True)

    def render(self, ui_screen):
        super().render(ui_screen)

        cursor = self.get_manager(Manager.PLAYER).cursors[Team.RED]

        # Generate a screen of the size of the map
        map = self.get_manager(Manager.MAP)
        map_screen = pygame.Surface((map.width * GRID_WIDTH, map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)
        SESSION.render(map_screen, ui_screen)

        # Render the current tile at the bottom of the screen
        ui_screen.fill(clear_color[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        # Render tiles
        tile_display = pygame.Surface((GRID_WIDTH * 2, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        tile_display.set_alpha(255 if cursor.placing_tiles else 64)

        tile_display.blit(self.get_tile_sprite_for_tiletype(cursor.tile_type[0]), (0, 0))
        tile_display.blit(spr_cursor[Team.RED], (0, 0))
        tile_display.blit(self.get_tile_sprite_for_tiletype(cursor.tile_type[1]), (GRID_WIDTH, 0))
        tile_display.blit(spr_cursor[Team.BLUE], (GRID_WIDTH, 0))

        ui_screen.blit(tile_display, (0, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render pieces
        piece_display = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        piece_display.set_alpha(255 if not cursor.placing_tiles else 64)

        piece_display.fill(clear_color[cursor.team], (0, 0, GRID_WIDTH, GRID_HEIGHT))
        piece_display.blit(self.get_piece_sprite_for_piecetype(cursor.piece_type, cursor.team), (0, 0))
        piece_display.blit(spr_cursor[cursor.team], (0, 0))

        ui_screen.blit(piece_display, (GRID_WIDTH * 3, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Trim the screen to just the camera area
        camera_x, camera_y = self.get_manager(Manager.PLAYER).get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
