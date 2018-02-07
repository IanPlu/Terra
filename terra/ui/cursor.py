from pygame.constants import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN

from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_LEFT, KB_RIGHT, KB_CONFIRM, KB_CANCEL, KB_MENU
from terra.resources.assets import spr_cursor
from terra.settings import SCREEN_SCALE
from terra.team import Team
from terra.ui.menupopup import MenuPopup
from terra.ui.tileselection import TileSelection
from terra.util.mathutil import clamp


# Controllable cursor on the map.
# Triggers selection events and allows the player to move around.
class Cursor(GameObject):
    def __init__(self, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__()
        self.game_map = game_map
        self.gx = gx
        self.gy = gy
        self.team = team

        self.menu = None
        self.move_ui = None

        self.camera_x = 0
        self.camera_y = 0

    def confirm(self):
        publish_game_event(E_SELECT, {
            'gx': int(self.gx),
            'gy': int(self.gy),
            'team': self.team,
            'selecting_movement': self.move_ui is not None
        })

    def cancel(self):
        publish_game_event(E_CANCEL, {})

    # Creates a generic menu popup from the provided event.
    def open_menu(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def close_menu(self):
        del self.menu
        self.menu = None

    def open_pause_menu(self):
        self.menu = MenuPopup(self, self.gx, self.gy, self.team, [
            MENU_SUBMIT_TURN, MENU_SAVE_GAME, MENU_QUIT_BATTLE
        ], centered=True)

    def open_move_ui(self, event):
        self.move_ui = TileSelection(event.gx, event.gy, event.min_range, event.max_range,
                                     event.game_map, event.movement_type, event.team, event.piece_manager, event.option)

    def close_move_ui(self):
        del self.move_ui
        self.move_ui = None

    def open_build_ui(self, event):
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
                elif event.key in KB_DOWN and self.gy < self.game_map.height - 1:
                    self.gy += 1
                if event.key in KB_LEFT and self.gx > 0:
                    self.gx -= 1
                elif event.key in KB_RIGHT and self.gx < self.game_map.width - 1:
                    self.gx += 1

                # Unit selection
                if event.key in KB_CONFIRM:
                    self.confirm()
                elif event.key in KB_CANCEL:
                    self.cancel()
                elif event.key in KB_MENU:
                    self.open_pause_menu()

            # Mouse control of the cursor
            elif event.type == MOUSEMOTION:
                mousex, mousey = pygame.mouse.get_pos()
                # Convert the screen coordinates to the grid coordinates
                self.gx = (mousex / SCREEN_SCALE + self.camera_x) // GRID_WIDTH
                self.gy = (mousey / SCREEN_SCALE + self.camera_y) // GRID_HEIGHT

            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CONFIRM:
                    self.confirm()
                elif event.button in KB_CANCEL:
                    self.cancel()

        # Clamp gx and gy, and scroll camera as appropriate
        self.gx = clamp(self.gx, 0, self.game_map.width - 1)
        self.gy = clamp(self.gy, 0, self.game_map.height - 2)

        self.scroll_camera()

    def scroll_camera(self):
        camera_min_gx = self.camera_x // GRID_WIDTH
        camera_min_gy = self.camera_y // GRID_HEIGHT
        camera_max_gx = camera_min_gx + RESOLUTION_WIDTH // GRID_WIDTH
        camera_max_gy = camera_min_gy + RESOLUTION_HEIGHT // GRID_HEIGHT

        screen_buffer = 1

        if self.gx >= camera_max_gx - screen_buffer:
            self.camera_x += GRID_WIDTH
        if self.gx <= camera_min_gx + screen_buffer:
            self.camera_x -= GRID_WIDTH
        if self.gy >= camera_max_gy - screen_buffer - 1:
            self.camera_y += GRID_HEIGHT
        if self.gy <= camera_min_gy + screen_buffer:
            self.camera_y -= GRID_HEIGHT

        self.camera_x = clamp(self.camera_x, 0, self.game_map.width * GRID_WIDTH - RESOLUTION_WIDTH)
        self.camera_y = clamp(self.camera_y, 0, self.game_map.height * GRID_HEIGHT - RESOLUTION_HEIGHT)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.move_ui:
            self.move_ui.render(game_screen, ui_screen)

        game_screen.blit(spr_cursor[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.menu:
            self.menu.render(game_screen, ui_screen)
