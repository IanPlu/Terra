from pygame.constants import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN

from terra.constants import CAMERA_WIDTH, CAMERA_HEIGHT
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_LEFT, KB_RIGHT, KB_CONFIRM, KB_CANCEL, KB_MENU
from terra.managers.managers import Managers
from terra.mode import Mode
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_cursor, spr_turn_submitted_indicator
from terra.settings import SETTINGS, Setting
from terra.sound.soundtype import SoundType
from terra.ui.menupopup import MenuPopup
from terra.ui.tileselection import TileSelection
from terra.util.mathutil import clamp


camera_scroll_speed = 3
camera_lock_distance = 1
camera_scroll_border = 1.5


# Controllable cursor on the map.
# Triggers selection events and allows the player to move around.
# Maintains a camera position roughly centered on the cursor.
class Cursor(GameObject):
    def __init__(self, team):
        super().__init__()

        # Cursors start on their team's base
        base = Managers.piece_manager.get_all_pieces_for_team(team, piece_type=PieceType.BASE)
        if len(base):
            self.gx = base[0].gx
            self.gy = base[0].gy
        else:
            self.gx = 0
            self.gy = 0

        self.team = team

        self.menu = None
        self.move_ui = None

        self.camera_x = self.gx * GRID_WIDTH
        self.camera_y = self.gy * GRID_HEIGHT
        self.camera_dest_x = self.camera_x
        self.camera_dest_y = self.camera_y
        self.scroll_camera()

        # Set the camera position to the destination immediately, otherwise we might scroll out of the map area
        self.camera_x = self.camera_dest_x
        self.camera_y = self.camera_dest_y

    def confirm(self):
        if not Managers.team_manager.is_turn_submitted(self.team):
            publish_game_event(E_SELECT, {
                'gx': int(self.gx),
                'gy': int(self.gy),
                'team': self.team,
                'selecting_movement': self.move_ui is not None
            })

    def cancel(self):
        if not Managers.team_manager.is_turn_submitted(self.team):
            publish_game_event(E_CANCEL, {})

    # Creates a generic menu popup from the provided event.
    def open_menu(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def close_menu(self):
        del self.menu
        self.menu = None

    def open_pause_menu(self):
        if Managers.current_mode in [Mode.BATTLE]:
            if Managers.team_manager.is_turn_submitted(self.team):
                menu_options = [MENU_REVISE_TURN]
            else:
                menu_options = [MENU_SUBMIT_TURN]

            menu_options.extend([MENU_SAVE_GAME, MENU_CONCEDE, MENU_QUIT_BATTLE])
        elif Managers.current_mode == Mode.EDIT:
            menu_options = [MENU_FILL_WITH_CURRENT_TILE, MENU_SAVE_MAP, MENU_QUIT_BATTLE]
        else:
            # Don't open the menu in this mode
            return

        self.menu = MenuPopup(self, self.gx, self.gy, self.team, menu_options, centered=True)

    def open_move_ui(self, event):
        self.move_ui = TileSelection(event.gx, event.gy, event.min_range, event.max_range,
                                     event.movement_type, event.piece_type, event.team, event.option)

    def close_move_ui(self):
        del self.move_ui
        self.move_ui = None

    def open_build_ui(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def open_upgrade_ui(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_OPEN_MENU):
            self.open_menu(event)
        elif is_event_type(event, E_CLOSE_MENU):
            self.close_menu()
        elif is_event_type(event, E_OPEN_TILE_SELECTION):
            self.open_move_ui(event)
        elif is_event_type(event, E_SELECT_TILE, E_CANCEL_TILE_SELECTION):
            self.close_move_ui()
        elif is_event_type(event, E_OPEN_BUILD_MENU):
            self.open_build_ui(event)
        elif is_event_type(event, E_SELECT_BUILD_UNIT, E_CANCEL_BUILD_UNIT):
            self.close_menu()
        elif is_event_type(event, E_OPEN_UPGRADE_MENU):
            self.open_upgrade_ui(event)
        elif is_event_type(event, E_SELECT_UPGRADE, E_CANCEL_UPGRADE):
            self.close_menu()

        # Only react to button inputs if we're not showing a sub menu
        if self.menu:
            self.menu.step(event)
        else:
            if self.move_ui:
                self.move_ui.step(event)

            if event.type == KEYDOWN:
                # Cursor movement
                if event.key in KB_UP and self.gy > 0:
                    self.gy -= 1
                    Managers.sound_manager.play_sound(SoundType.CURSOR_MOVE)
                elif event.key in KB_DOWN and self.gy < Managers.battle_map.height - 1:
                    self.gy += 1
                    Managers.sound_manager.play_sound(SoundType.CURSOR_MOVE)
                if event.key in KB_LEFT and self.gx > 0:
                    self.gx -= 1
                    Managers.sound_manager.play_sound(SoundType.CURSOR_MOVE)
                elif event.key in KB_RIGHT and self.gx < Managers.battle_map.width - 1:
                    self.gx += 1
                    Managers.sound_manager.play_sound(SoundType.CURSOR_MOVE)

                # Unit selection
                if event.key in KB_CONFIRM:
                    self.confirm()
                    Managers.sound_manager.play_sound(SoundType.CURSOR_SELECT)
                elif event.key in KB_CANCEL:
                    self.cancel()
                    Managers.sound_manager.play_sound(SoundType.CURSOR_CANCEL)
                elif event.key in KB_MENU:
                    self.open_pause_menu()

            # Mouse control of the cursor
            elif event.type == MOUSEMOTION:
                mousex, mousey = pygame.mouse.get_pos()
                # Convert the screen coordinates to the grid coordinates
                self.gx = (mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH
                self.gy = (mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT

            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CONFIRM:
                    self.confirm()
                elif event.button in KB_CANCEL:
                    self.cancel()

    # Clamp gx and gy, and scroll camera as appropriate
    def scroll_camera(self):
        if not self.menu and pygame.mouse.get_focused():
            mousex, mousey = pygame.mouse.get_pos()
            # Convert the screen coordinates to the grid coordinates
            self.gx = clamp((mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH, 0, Managers.battle_map.width - 1)
            self.gy = clamp((mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT, 0, Managers.battle_map.height - 1)

        camera_min_gx = self.camera_dest_x // GRID_WIDTH
        camera_min_gy = self.camera_dest_y // GRID_HEIGHT
        camera_max_gx = camera_min_gx + CAMERA_WIDTH // GRID_WIDTH
        camera_max_gy = camera_min_gy + CAMERA_HEIGHT // GRID_HEIGHT

        if self.gx >= camera_max_gx - camera_scroll_border:
            self.camera_dest_x += GRID_WIDTH
        if self.gx <= camera_min_gx + camera_scroll_border:
            self.camera_dest_x -= GRID_WIDTH
        if self.gy >= camera_max_gy - camera_scroll_border:
            self.camera_dest_y += GRID_HEIGHT
        if self.gy <= camera_min_gy + camera_scroll_border:
            self.camera_dest_y -= GRID_HEIGHT

        self.camera_dest_x = clamp(self.camera_dest_x, 0, Managers.battle_map.width * GRID_WIDTH - CAMERA_WIDTH)
        self.camera_dest_y = clamp(self.camera_dest_y, 0, Managers.battle_map.height * GRID_HEIGHT - CAMERA_HEIGHT)

        # Scroll the actual camera position to the destination coords
        if self.camera_x != self.camera_dest_x:
            self.camera_x += (self.camera_dest_x - self.camera_x) / camera_scroll_speed
            if abs(self.camera_x - self.camera_dest_x) <= camera_lock_distance:
                self.camera_x = self.camera_dest_x
        if self.camera_y != self.camera_dest_y:
            self.camera_y += (self.camera_dest_y - self.camera_y) / camera_scroll_speed
            if abs(self.camera_y - self.camera_dest_y) <= camera_lock_distance:
                self.camera_y = self.camera_dest_y

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.scroll_camera()

        if self.move_ui:
            self.move_ui.render(game_screen, ui_screen)

        game_screen.blit(spr_cursor[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if Managers.team_manager.is_turn_submitted(self.team):
            game_screen.blit(spr_turn_submitted_indicator[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.menu:
            self.menu.render(game_screen, ui_screen)
