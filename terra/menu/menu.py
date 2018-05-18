from pygame import Surface, SRCALPHA
from pygame.mouse import get_pos

from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject
from terra.managers.session import Manager
from terra.resources.assets import shadow_color, light_color
from terra.settings import SETTINGS, Setting
from terra.sound.soundtype import SoundType
from terra.team.team import Team
from terra.util.mathutil import clamp


# Utilities and shared controls for menu-like objects.
# Automatically sets up some input handlers for common actions, like moving the cursor
# and adjusting the displayed options
class Menu(GameObject):
    def __init__(self, num_options, max_displayable_options, displayable_buffer, root_x, root_y, width, option_height):
        super().__init__()

        self.menu_pos = 0
        self.num_options = num_options

        self.max_displayable_options = max_displayable_options
        self.displayable_buffer = displayable_buffer
        self.menu_min = 0
        self.menu_max = max_displayable_options

        self.root_x = root_x
        self.root_y = root_y
        self.width = width
        self.option_height = option_height

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.UP, self.cursor_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.cursor_down)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.cancel)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_UP, self.scroll_menu_up)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_DOWN, self.scroll_menu_down)
        input_handler.register_handler(InputAction.MOTION, None, self.set_cursor_pos_to_mouse_coords)

    def confirm(self):
        self.play_sound(SoundType.CURSOR_SELECT)

    def cancel(self):
        self.play_sound(SoundType.CURSOR_CANCEL)

    # Move the cursor up
    def cursor_up(self):
        self.menu_pos -= 1
        self.normalize_menu_pos()
        self.play_sound(SoundType.CURSOR_MOVE)

    # Move the cursor down
    def cursor_down(self):
        self.menu_pos += 1
        self.normalize_menu_pos()
        self.play_sound(SoundType.CURSOR_MOVE)

    # Scroll the displayed menu portion up
    def scroll_menu_up(self):
        self.menu_min = clamp(self.menu_min - 1, 0, self.num_options - self.max_displayable_options)
        self.clamp_menu_bounds()
        self.set_cursor_pos_to_mouse_coords()

    # Scroll the display menu portion down
    def scroll_menu_down(self):
        self.menu_min = clamp(self.menu_min + 1, 0, self.num_options - self.max_displayable_options)
        self.clamp_menu_bounds()
        self.set_cursor_pos_to_mouse_coords()

    # Restrict the menu position to be within the number of options, and scroll the options
    def normalize_menu_pos(self):
        if self.menu_pos < 0:
            self.menu_pos = self.num_options - 1
        if self.menu_pos > self.num_options - 1:
            self.menu_pos = 0

        # Scroll the displayable area
        if self.menu_pos < self.menu_min + self.displayable_buffer:
            self.menu_min = self.menu_pos - self.displayable_buffer
        if self.menu_pos >= self.menu_max - self.displayable_buffer:
            self.menu_min = self.menu_pos + self.displayable_buffer - self.max_displayable_options + 1

        # Clamp to the bounds of the option list
        self.clamp_menu_bounds()

    # Set new menu min and max to something sensible
    def clamp_menu_bounds(self):
        self.menu_min = clamp(self.menu_min, 0, self.num_options - self.max_displayable_options)
        self.menu_max = clamp(self.menu_min + self.max_displayable_options, 0, self.num_options)

    # Return true if the mouse cursor is within our height and width
    def cursor_in_menu_bounds(self):
        mouse_x = get_pos()[0] / SETTINGS.get(Setting.SCREEN_SCALE)
        mouse_y = get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE)
        height = self.option_height * min(self.max_displayable_options, self.num_options)

        return self.root_x <= mouse_x <= self.root_x + self.width and self.root_y <= mouse_y <= self.root_y + height

    def set_cursor_pos_to_mouse_coords(self):
        if self.cursor_in_menu_bounds():
            self.menu_pos = clamp((int(get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE))
                                   - self.root_y) // 24 + self.menu_min, self.menu_min, self.menu_max)

    # Draw a menu box, with the specified size in px and color.
    @staticmethod
    def draw_menu_box(width, height, background=shadow_color[Team.RED], border=light_color):
        box = Surface((width, height), SRCALPHA, 32)

        box.fill(border, (0, 0, width, height))
        box.fill(background, (1, 1, width - 2, height - 3))

        return box

    # Return true if we should show a scroll bar-- we have more options than we can show
    @staticmethod
    def should_show_scroll_bar(max_displayable_options, num_options):
        return max_displayable_options < num_options

    @staticmethod
    def draw_scroll_bar(width, height, max_displayable_options, menu_min, num_options, background=shadow_color[Team.RED]):
        box = Menu.draw_menu_box(width, height, background)

        # What percent of the total options are visible right now
        percentage_shown = max_displayable_options / num_options
        # Where in the list we are (for positioning the scroll bar)
        position_in_list = menu_min / num_options

        box.fill(light_color, (0, 0 + (height * position_in_list), width, height * percentage_shown))
        return box
