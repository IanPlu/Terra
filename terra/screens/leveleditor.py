import pygame
from pygame.constants import KMOD_CTRL

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.piece.piecetype import PieceType
from terra.resources.assets import clear_color, spr_tiles, spr_cursor, spr_pieces
from terra.team.team import Team
from terra.util.mathutil import clamp
from terra.managers.session import SESSION, Session, Manager


# A map editor for Terra maps.
# Allows placing tiles of different types and saving / loading maps.
class LevelEditor(GameScreen):
    def __init__(self, map_name):
        super().__init__()

        bitmap, pieces, team_data, upgrades, meta = Session.set_up_level_editor(map_name)
        self.teams = [Team[team.split(' ')[0]] for team in team_data] + [Team.NONE]

        self.current_tile_type = TileType.GRASS
        self.secondary_tile_type = TileType.SEA

        self.placing_tiles = True
        self.piece_team = self.teams[0]
        self.piece_type = PieceType.COLONIST

        self.placing_multiple = False
        self.placing_multiple_alt = False

        self.allow_placing_multiple = False

    def destroy(self):
        super().destroy()
        if SESSION:
            SESSION.reset()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_SELECT, self.confirm)
        event_bus.register_handler(EventType.E_CANCEL, self.confirm_alt)
        event_bus.register_handler(EventType.E_CLOSE_MENU, self.handle_menu_selection)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_UP, self.scroll_up)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_DOWN, self.scroll_down)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.swap_placing_mode)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.enable_placing_multiple)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.enable_placing_multiple_alt)

        input_handler.register_handler(InputAction.RELEASE, Key.CONFIRM, self.disable_placing_multiple)
        input_handler.register_handler(InputAction.RELEASE, Key.CANCEL, self.disable_placing_multiple_alt)

    def handle_menu_selection(self, event):
        if event.option == Option.MENU_SAVE_MAP:
            SESSION.save_map_to_file()
        elif event.option == Option.MENU_QUIT_BATTLE:
            publish_game_event(EventType.E_QUIT_BATTLE, {})
        elif event.option == Option.MENU_FILL_WITH_CURRENT_TILE:
            self.fill_with_current_tile()
        elif event.option == Option.MENU_MIRROR_X:
            self.mirror_map(mirror_x=True, mirror_y=False)
        elif event.option == Option.MENU_MIRROR_Y:
            self.mirror_map(mirror_x=False, mirror_y=True)

    def step(self, event):
        super().step(event)

        SESSION.step(event)

        if self.placing_multiple:
            self.confirm(event)
        elif self.placing_multiple_alt:
            self.confirm_alt(event)

    def confirm(self, event):
        cursor_x, cursor_y = self.get_manager(Manager.PLAYER).get_cursor_coords()
        if self.placing_tiles:
            self.get_manager(Manager.MAP).update_tile_type(cursor_x, cursor_y, self.current_tile_type)
        else:
            if self.get_manager(Manager.PIECE).get_piece_at(cursor_x, cursor_y, self.piece_team):
                # Delete the existing piece first
                publish_game_event(EventType.E_PIECE_DEAD, {
                    'gx': cursor_x,
                    'gy': cursor_y,
                    'team': self.piece_team
                })

            publish_game_event(EventType.E_PIECE_BUILT, {
                'tx': cursor_x,
                'ty': cursor_y,
                'team': self.piece_team,
                'new_piece_type': self.piece_type,
            })

    def confirm_alt(self, event):
        cursor_x, cursor_y = self.get_manager(Manager.PLAYER).get_cursor_coords()
        if self.placing_tiles:
            self.get_manager(Manager.MAP).update_tile_type(cursor_x, cursor_y, self.secondary_tile_type)
        else:
            publish_game_event(EventType.E_PIECE_DEAD, {
                'gx': cursor_x,
                'gy': cursor_y,
                'team': self.piece_team
            })

    def scroll(self, direction):
        if self.placing_tiles:
            if pygame.key.get_mods() & KMOD_CTRL:
                self.secondary_tile_type = self.update_tile_type(self.secondary_tile_type, direction)
            else:
                self.current_tile_type = self.update_tile_type(self.current_tile_type, direction)
        else:
            if pygame.key.get_mods() & KMOD_CTRL:
                self.piece_team = self.update_team(self.piece_team, direction)
            else:
                self.piece_type = self.update_piece_type(self.piece_type, direction)

    def scroll_up(self):
        self.scroll(1)

    def scroll_down(self):
        self.scroll(-1)

    def swap_placing_mode(self):
        self.placing_tiles = not self.placing_tiles

    def enable_placing_multiple(self):
        if self.allow_placing_multiple:
            self.placing_multiple = True

    def disable_placing_multiple(self):
        self.placing_multiple = False

    def enable_placing_multiple_alt(self):
        if self.allow_placing_multiple:
            self.placing_multiple_alt = True

    def disable_placing_multiple_alt(self):
        self.placing_multiple_alt = False

    def update_tile_type(self, tiletype, amount):
        new_tile_type = clamp(tiletype.value + amount, 1, len(TileType))

        if not new_tile_type == tiletype:
            return TileType(new_tile_type)

    def update_piece_type(self, piecetype, amount):
        new_piece_type = clamp(piecetype.value + amount, 1, len(PieceType) - 1)

        if not new_piece_type == piecetype:
            return PieceType(new_piece_type)

    def update_team(self, team, amount):
        new_index = self.teams.index(team) + amount
        if new_index > len(self.teams) - 1:
            new_index = 0
        elif new_index < 0:
            new_index = len(self.teams) - 1

        new_team = self.teams[new_index]

        if not new_team == team:
            return Team(new_team)
        else:
            return team

    def get_tile_sprite_for_tiletype(self, tiletype):
        if tiletype in [TileType.COAST]:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)
        else:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)

    def get_piece_sprite_for_piecetype(self, piecetype):
        return spr_pieces[self.piece_team][piecetype]

    def fill_with_current_tile(self):
        self.get_manager(Manager.MAP).fill_map_with_tile(self.current_tile_type)

    def mirror_map(self, mirror_x=True, mirror_y=False):
        self.get_manager(Manager.MAP).mirror_map(mirror_x, mirror_y)

    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map = self.get_manager(Manager.MAP)
        map_screen = pygame.Surface((map.width * GRID_WIDTH, map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)
        SESSION.render(map_screen, ui_screen)

        # Render the current tile at the bottom of the screen
        ui_screen.fill(clear_color[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        # Render tiles
        tile_display = pygame.Surface((GRID_WIDTH * 2, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        tile_display.set_alpha(255 if self.placing_tiles else 64)

        tile_display.blit(self.get_tile_sprite_for_tiletype(self.current_tile_type), (0, 0))
        tile_display.blit(spr_cursor[Team.RED], (0, 0))
        tile_display.blit(self.get_tile_sprite_for_tiletype(self.secondary_tile_type), (GRID_WIDTH, 0))
        tile_display.blit(spr_cursor[Team.BLUE], (GRID_WIDTH, 0))

        ui_screen.blit(tile_display, (0, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render pieces
        piece_display = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        piece_display.set_alpha(255 if not self.placing_tiles else 64)

        piece_display.fill(clear_color[self.piece_team], (0, 0, GRID_WIDTH, GRID_HEIGHT))
        piece_display.blit(self.get_piece_sprite_for_piecetype(self.piece_type), (0, 0))
        piece_display.blit(spr_cursor[self.piece_team], (0, 0))

        ui_screen.blit(piece_display, (GRID_WIDTH * 3, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Trim the screen to just the camera area
        camera_x, camera_y = self.get_manager(Manager.PLAYER).get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
