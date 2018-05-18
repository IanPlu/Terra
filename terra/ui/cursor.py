import pygame

from terra.constants import CAMERA_WIDTH, CAMERA_HEIGHT
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject
from terra.managers.session import Manager
from terra.resources.assets import spr_cursor
from terra.settings import SETTINGS, Setting
from terra.sound.soundtype import SoundType
from terra.util.mathutil import clamp

camera_scroll_speed = 3
camera_lock_distance = 1
camera_scroll_border = 1.5


# Base controllable cursor on the map.
# Maintains a camera position roughly centered on the cursor, and allows moving the cursor around.
class Cursor(GameObject):
    def __init__(self, team):
        super().__init__()

        self.team = team

        self.gx = 0
        self.gy = 0

        self.camera_x = self.gx * GRID_WIDTH
        self.camera_y = self.gy * GRID_HEIGHT
        self.camera_dest_x = self.camera_x
        self.camera_dest_y = self.camera_y
        self.scroll_camera()

        # Set the camera position to the destination immediately, otherwise we might scroll out of the map area
        self.camera_x = self.camera_dest_x
        self.camera_y = self.camera_dest_y

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.UP, self.move_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.move_down)
        input_handler.register_handler(InputAction.PRESS, Key.LEFT, self.move_left)
        input_handler.register_handler(InputAction.PRESS, Key.RIGHT, self.move_right)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.cancel)
        input_handler.register_handler(InputAction.MOTION, None, self.convert_mouse_coords_to_cursor)

    def convert_mouse_coords_to_cursor(self):
        mousex, mousey = pygame.mouse.get_pos()
        # Convert the screen coordinates to the grid coordinates
        self.gx = int((mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH)
        self.gy = int((mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT)

    def move_up(self):
        if self.gy > 0:
            self.gy -= 1
            self.play_sound(SoundType.CURSOR_MOVE)

    def move_down(self):
        if self.gy < self.get_manager(Manager.MAP).height - 1:
            self.gy += 1
            self.play_sound(SoundType.CURSOR_MOVE)

    def move_left(self):
        if self.gx > 0:
            self.gx -= 1
            self.play_sound(SoundType.CURSOR_MOVE)

    def move_right(self):
        if self.gx < self.get_manager(Manager.MAP).width - 1:
            self.gx += 1
            self.play_sound(SoundType.CURSOR_MOVE)

    def confirm(self):
        self.play_sound(SoundType.CURSOR_SELECT)

    def cancel(self):
        self.play_sound(SoundType.CURSOR_SELECT)

    def is_active(self):
        return True

    # Clamp gx and gy, and scroll camera as appropriate
    def scroll_camera(self):
        map = self.get_manager(Manager.MAP)

        if self.is_active():
            mousex, mousey = pygame.mouse.get_pos()
            # Convert the screen coordinates to the grid coordinates
            self.gx = int(clamp((mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH, 0, map.width - 1))
            self.gy = int(clamp((mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT, 0, map.height - 1))

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

        self.camera_dest_x = clamp(self.camera_dest_x, 0, map.width * GRID_WIDTH - CAMERA_WIDTH)
        self.camera_dest_y = clamp(self.camera_dest_y, 0, map.height * GRID_HEIGHT - CAMERA_HEIGHT)

        # Scroll the actual camera position to the destination coords
        if self.camera_x != self.camera_dest_x:
            self.camera_x += (self.camera_dest_x - self.camera_x) / camera_scroll_speed
            if abs(self.camera_x - self.camera_dest_x) <= camera_lock_distance:
                self.camera_x = self.camera_dest_x
        if self.camera_y != self.camera_dest_y:
            self.camera_y += (self.camera_dest_y - self.camera_y) / camera_scroll_speed
            if abs(self.camera_y - self.camera_dest_y) <= camera_lock_distance:
                self.camera_y = self.camera_dest_y

    # Scroll the camera and draw a cursor
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.scroll_camera()

        game_screen.blit(spr_cursor[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

