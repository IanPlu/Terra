import pygame

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gamescreen import GameScreen
from terra.event.event import EventType, publish_game_event
from terra.managers.mapmanager import get_loadable_maps, load_map_from_file, generate_minimap
from terra.menu.option import Option
from terra.menu.textinput import TextInput, FILTER_IP, FILTER_FILENAME, FILTER_ALPHANUMERIC
from terra.resources.assetloading import AssetType
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color, spr_main_menu_option, \
    spr_title_text
from terra.settings import Setting, SETTINGS, numeric_settings
from terra.strings import get_text, get_string, main_menu_strings, formatted_strings
from terra.team import Team
from terra.util.drawingutil import draw_text
from terra.util.mathutil import clamp

displayable_buffer = 1
max_displayable_options = 5
menu_width = 168


# Convert a list of loadable maps to selectable options: [(display name, filename), (...)]
def convert_loadable_maps_to_options(asset_type):
    options = []
    for mapname in get_loadable_maps(asset_type):
        options.append((mapname, []))
    return options


# Generate the default main menu.
def generate_menu():
    loadable_maps = convert_loadable_maps_to_options(AssetType.MAP)
    loadable_saves = convert_loadable_maps_to_options(AssetType.SAVE)

    start_menu_options = [
        (Option.LOCAL, [
            (Option.NEW_GAME, loadable_maps),
            (Option.LOAD_GAME, loadable_saves)
        ]),
        (Option.NETWORK, [
            (Option.HOST_GAME, [
                (Option.NEW_NETWORK_GAME, loadable_maps),
                (Option.LOAD_NETWORK_GAME, loadable_saves)
            ]),
            (Option.JOIN_GAME, [])
        ]),
        (Option.LEVEL_EDITOR, [
            (Option.NEW_MAP, []),
            (Option.LOAD_MAP, loadable_maps)
        ]),
        (Option.SETTINGS, generate_settings_menu()),
        (Option.QUIT, [])
    ]

    return Option.START, start_menu_options


# Generate the settings menu.
def generate_settings_menu():
    return [
        (Setting.SCREEN_SCALE, []),
        (Setting.SFX_VOLUME, []),
        (Setting.BGM_VOLUME, []),
        (Setting.NICKNAME, []),
        (Option.SAVE_SETTINGS, []),
    ]


# Main menu for the game.
# Allows player to load or start games, access the level editor, and so on
class MainMenu(GameScreen):
    def __init__(self):
        super().__init__()

        self.current_menu = generate_menu()
        self.current_menu_pos = 0
        self.num_options = len(self.current_menu[1])
        self.current_menu_min = 0
        self.current_menu_max = self.num_options

        self.root_x = HALF_RES_WIDTH
        self.root_y = HALF_RES_HEIGHT - 48

        self.text_input = None

    def destroy(self):
        super().destroy()

        if self.text_input:
            self.text_input.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.TEXT_CANCEL_INPUT, self.handle_text_input)
        event_bus.register_handler(EventType.TEXT_SUBMIT_INPUT, self.handle_text_input)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.UP, self.cursor_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.cursor_down)
        input_handler.register_handler(InputAction.PRESS, Key.LEFT, self.lower_setting)
        input_handler.register_handler(InputAction.PRESS, Key.RIGHT, self.raise_setting)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.reset_menu)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.reset_menu)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_UP, self.scroll_menu_pos_up)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_DOWN, self.scroll_menu_pos_down)
        input_handler.register_handler(InputAction.MOTION, None, self.set_cursor_pos_to_mouse_coords)

    def is_accepting_input(self):
        return self.text_input is None

    def cursor_up(self):
        self.current_menu_pos -= 1
        self.normalize_menu_pos()

    def cursor_down(self):
        self.current_menu_pos += 1
        self.normalize_menu_pos()

    def normalize_menu_pos(self):
        if self.current_menu_pos < 0:
            self.current_menu_pos = self.num_options - 1
        if self.current_menu_pos > self.num_options - 1:
            self.current_menu_pos = 0

        # Scroll the displayable area
        if self.current_menu_pos < self.current_menu_min + displayable_buffer:
            self.current_menu_min = self.current_menu_pos - displayable_buffer
        if self.current_menu_pos >= self.current_menu_max - displayable_buffer:
            self.current_menu_min = self.current_menu_pos + displayable_buffer - max_displayable_options + 1

        # Clamp to the bounds of the option list
        self.clamp_menu_bounds()

    def cursor_in_menu_bounds(self):
        mouse_x = pygame.mouse.get_pos()[0] / SETTINGS.get(Setting.SCREEN_SCALE)
        mouse_y = pygame.mouse.get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE)
        return self.root_x - 24 <= mouse_x <= self.root_x + menu_width - 24 and \
               self.root_y <= mouse_y <= self.root_y + 24 * min(max_displayable_options, self.num_options) + 24

    def set_cursor_pos_to_mouse_coords(self):
        if self.cursor_in_menu_bounds():
            self.current_menu_pos = clamp((int(pygame.mouse.get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE))
                                           - self.root_y - 24) // 24 + self.current_menu_min, self.current_menu_min, self.current_menu_max)

    def scroll_menu_pos_up(self):
        self.current_menu_min = clamp(self.current_menu_min - 1, 0, self.num_options - max_displayable_options)
        self.clamp_menu_bounds()
        self.set_cursor_pos_to_mouse_coords()

    def scroll_menu_pos_down(self):
        self.current_menu_min = clamp(self.current_menu_min + 1, 0, self.num_options - max_displayable_options)
        self.clamp_menu_bounds()
        self.set_cursor_pos_to_mouse_coords()

    def clamp_menu_bounds(self):
        self.current_menu_min = clamp(self.current_menu_min, 0, self.num_options - max_displayable_options)
        self.current_menu_max = clamp(self.current_menu_min + max_displayable_options, 0, self.num_options)

    def confirm(self):
        if 0 <= self.current_menu_pos < self.num_options:
            selection = self.current_menu[1][self.current_menu_pos]

            if not selection[0] in Setting:
                if len(selection[1]) > 0:
                    self.current_menu = selection
                    self.current_menu_pos = 0
                    self.num_options = len(selection[1])
                    self.clamp_menu_bounds()
                else:
                    self.handle_menu_selection(selection)
            elif selection[0] == Setting.NICKNAME:
                self.text_input = TextInput("NICKNAME_INPUT", selection[0], default_text=SETTINGS.get_unsaved(Setting.NICKNAME), input_filter=FILTER_ALPHANUMERIC)

    def reset_menu(self):
        if self.current_menu[0] == Option.SETTINGS:
            SETTINGS.reset_settings()

        self.current_menu = generate_menu()
        self.current_menu_pos = 0
        self.num_options = len(self.current_menu[1])
        self.clamp_menu_bounds()

    def handle_menu_selection(self, option):
        if self.current_menu[0] in [Option.NEW_GAME, Option.LOAD_GAME, Option.LOAD_MAP]:
            publish_game_event(EventType.MENU_SELECT_OPTION, {
                'option': self.current_menu[0],
                'mapname': option[0]
            })
        elif self.current_menu[0] in [Option.NEW_NETWORK_GAME, Option.LOAD_NETWORK_GAME]:
            publish_game_event(EventType.MENU_SELECT_OPTION, {
                'option': self.current_menu[0],
                'mapname': option[0],
                'address': "localhost"
            })
        elif option[0] == Option.JOIN_GAME:
            self.text_input = TextInput("IP_INPUT", option[0], default_text="localhost", input_filter=FILTER_IP)
        elif option[0] == Option.NEW_MAP:
            self.text_input = TextInput("MAPNAME_INPUT", option[0], default_text="new_map", input_filter=FILTER_FILENAME)
        else:
            publish_game_event(EventType.MENU_SELECT_OPTION, {
                'option': option[0]
            })

    def handle_text_input(self, event):
        self.text_input.destroy()
        self.text_input = None

        if event.input:
            if event.tag == Option.NEW_MAP:
                publish_game_event(EventType.MENU_SELECT_OPTION, {
                    'option': event.tag,
                    'mapname': event.input + ".map"
                })
            elif event.tag == Option.JOIN_GAME:
                publish_game_event(EventType.MENU_SELECT_OPTION, {
                    'option': event.tag,
                    'address': event.input
                })
            elif event.tag == Setting.NICKNAME:
                SETTINGS.set_nonnumeric_setting(Setting.NICKNAME, event.input)

    def lower_setting(self):
        selection, _ = self.current_menu[1][self.current_menu_pos]
        if selection in numeric_settings:
            SETTINGS.lower_setting(selection)

    def raise_setting(self):
        selection, _ = self.current_menu[1][self.current_menu_pos]
        if selection in numeric_settings:
            SETTINGS.raise_setting(selection)

    def step(self, event):
        super().step(event)

        if self.text_input:
            self.text_input.step(event)

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        game_screen.blit(spr_title_text, (self.root_x - spr_title_text.get_width() // 2, 24))

        if self.text_input:
            self.text_input.render(game_screen, ui_screen)
        else:
            # Draw text for the menu title
            game_screen.blit(get_text(main_menu_strings, self.current_menu[0]), (self.root_x - 12, self.root_y))

            # Draw a scrollbar if necessary
            percentage_shown = max_displayable_options / self.num_options
            if percentage_shown < 1:
                height = 24 * min(max_displayable_options, self.num_options)
                game_screen.fill(light_color, (self.root_x + menu_width - 22, self.root_y + 23, 4, height))
                game_screen.fill(shadow_color[Team.RED], (self.root_x + menu_width - 22, self.root_y + 24, 3, height - 3))

                game_screen.fill(light_color, (self.root_x + menu_width - 22,
                                               self.root_y + 23 + (height * self.current_menu_min / self.num_options),
                                               4, percentage_shown * height))

            # Draw each menu option
            row_y = 1
            displayable_options = self.current_menu[1][self.current_menu_min:self.current_menu_max]
            for option in displayable_options:
                is_selected = self.current_menu_pos == self.current_menu[1].index(option)
                x_offset = 0 if is_selected else 16

                position_x, position_y = self.root_x, self.root_y + row_y * 24
                game_screen.fill(light_color, (position_x - 24 - 1 + x_offset, position_y - 1, menu_width + 3 - x_offset, 24))
                game_screen.fill(light_team_color[Team.RED] if is_selected else shadow_color[Team.RED],
                                 (position_x - 24 + x_offset, position_y, menu_width - x_offset, 21))

                if isinstance(option[0], str):
                    # Render arbitrary text
                    game_screen.blit(draw_text(option[0], light_color, shadow_color[Team.RED]), (position_x + 8, position_y + 4))

                    # Render map previews if we're trying to select a map
                    if is_selected and self.current_menu[0] in [Option.NEW_GAME, Option.NEW_MAP,
                                                                Option.LOAD_GAME, Option.LOAD_MAP,
                                                                Option.NEW_NETWORK_GAME, Option.LOAD_NETWORK_GAME]:
                        asset_type = AssetType.MAP if self.current_menu[0] in [Option.NEW_GAME, Option.NEW_MAP,
                                                                               Option.NEW_NETWORK_GAME, Option.LOAD_MAP] else AssetType.SAVE

                        bitmap, _, _, _, _ = load_map_from_file(option[0], asset_type=asset_type)
                        minimap = generate_minimap(bitmap)
                        game_screen.blit(minimap, (self.root_x - 25 - minimap.get_width(), self.root_y + 24))
                elif option[0] in Setting:
                    # Display the setting prompt and the current value
                    display_string = get_string(formatted_strings, option[0]).format(SETTINGS.get_unsaved(option[0]))
                    game_screen.blit(draw_text(display_string, light_color, shadow_color[Team.RED]), (position_x + 24, position_y + 4))
                else:
                    # Display the icon for the option
                    game_screen.blit(spr_main_menu_option[option[0]], (position_x - 24 + x_offset, position_y))
                    # Display prerendered text
                    game_screen.blit(get_text(main_menu_strings, option[0]), (position_x + 24, position_y + 4))

                row_y += 1

        return game_screen
