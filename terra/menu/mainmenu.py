from terra.constants import HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.event.event import EventType, publish_game_event
from terra.map.maputils import get_loadable_maps
from terra.map.minimap import draw_map_preview_from_file
from terra.menu.menu import Menu
from terra.menu.option import Option
from terra.menu.textinput import TextInput, FILTER_IP, FILTER_FILENAME, FILTER_ALPHANUMERIC
from terra.resources.assetloading import AssetType
from terra.resources.assets import light_color, shadow_color, light_team_color, spr_main_menu_option, dark_color
from terra.settings import Setting, SETTINGS, numeric_settings
from terra.strings import get_text, get_string, main_menu_strings, formatted_strings
from terra.util.drawingutil import draw_text
from terra.menu.tutorial import Tutorial


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

    local_option = (Option.LOCAL, [(Option.NEW_GAME, loadable_maps)])
    if len(loadable_saves) > 0:
        local_option[1].append((Option.LOAD_GAME, loadable_saves))

    host_option = (Option.HOST_GAME, [
        (Option.NEW_NETWORK_GAME, loadable_maps)
    ])
    if len(loadable_saves) > 0:
        host_option[1].append((Option.LOAD_NETWORK_GAME, loadable_saves))

    start_menu_options = [
        local_option,
        (Option.NETWORK, [
            host_option,
            (Option.JOIN_GAME, [])
        ]),
        (Option.LEVEL_EDITOR, [
            (Option.NEW_MAP, []),
            (Option.LOAD_MAP, loadable_maps)
        ]),
        (Option.SETTINGS, generate_settings_menu()),
        (Option.TUTORIAL, []),
        (Option.QUIT, [])
    ]

    return Option.START, start_menu_options


# Generate the settings menu.
def generate_settings_menu():
    return [
        (Setting.SCREEN_SCALE, []),
        (Setting.SFX_VOLUME, []),
        # (Setting.BGM_VOLUME, []),
        (Setting.ANIMATION_SPEED, []),
        (Setting.NICKNAME, []),
        (Setting.AUTOSAVE_INTERVAL, []),
        (Option.SAVE_SETTINGS, []),
    ]


# Main menu for the game.
# Allows player to load or start games, access the level editor, and change settings.
class MainMenu(Menu):
    def __init__(self):
        self.current_menu = generate_menu()
        self.text_input = None
        self.tutorial = None

        super().__init__(num_options=len(self.current_menu[1]),
                         max_displayable_options=6,
                         displayable_buffer=1,
                         root_x=HALF_RES_WIDTH,
                         root_y=HALF_RES_HEIGHT - 24,
                         width=168,
                         option_height=24)

    def destroy(self):
        super().destroy()

        if self.text_input:
            self.text_input.destroy()
        if self.tutorial:
            self.tutorial.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.TEXT_CANCEL_INPUT, self.handle_text_input)
        event_bus.register_handler(EventType.TEXT_SUBMIT_INPUT, self.handle_text_input)
        event_bus.register_handler(EventType.TUTORIAL_EXIT, self.close_tutorial)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.LEFT, self.lower_setting)
        input_handler.register_handler(InputAction.PRESS, Key.RIGHT, self.raise_setting)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.reset_menu)

    def is_accepting_input(self):
        return self.text_input is None and self.tutorial is None

    def confirm(self):
        super().confirm()

        if 0 <= self.menu_pos < self.num_options:
            selection = self.current_menu[1][self.menu_pos]

            if not selection[0] in Setting:
                if len(selection[1]) > 0:
                    self.current_menu = selection
                    self.menu_pos = 0
                    self.num_options = len(selection[1])
                    self.clamp_menu_bounds()
                else:
                    self.handle_menu_selection(selection)
            elif selection[0] == Setting.NICKNAME:
                self.text_input = TextInput("NICKNAME_INPUT", selection[0],
                                            default_text=SETTINGS.get_unsaved(Setting.NICKNAME),
                                            input_filter=FILTER_ALPHANUMERIC)

    def cancel(self):
        super().cancel()

        self.reset_menu()

    def reset_menu(self):
        if self.current_menu[0] == Option.SETTINGS:
            SETTINGS.reset_settings()

        self.current_menu = generate_menu()
        self.menu_pos = 0
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
        elif option[0] == Option.TUTORIAL:
            self.tutorial = Tutorial()
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

    def close_tutorial(self, event):
        self.tutorial.destroy()
        self.tutorial = None

        self.reset_menu()

    # Lower a setting in the settings submenu
    def lower_setting(self):
        selection, _ = self.current_menu[1][self.menu_pos]
        if selection in numeric_settings:
            SETTINGS.lower_setting(selection)

    # Raise a setting in the settings submenu
    def raise_setting(self):
        selection, _ = self.current_menu[1][self.menu_pos]
        if selection in numeric_settings:
            SETTINGS.raise_setting(selection)

    def step(self, event):
        super().step(event)

        if self.text_input:
            self.text_input.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.text_input:
            self.text_input.render(game_screen, ui_screen)
        elif self.tutorial:
            self.tutorial.render(game_screen, ui_screen)
        else:
            # Draw text for the menu title
            menu_title_text = get_text(main_menu_strings, self.current_menu[0])
            game_screen.blit(self.draw_menu_box(self.width - 16, 24, background=light_team_color),
                             (self.root_x - 8, self.root_y - 16))
            game_screen.blit(menu_title_text, (self.root_x + 24, self.root_y - 12))

            # Draw a scrollbar if necessary
            if self.should_show_scroll_bar(self.max_displayable_options, self.num_options):
                width = 8
                height = self.option_height * min(self.max_displayable_options, self.num_options)
                game_screen.blit(self.draw_scroll_bar(width, height, self.max_displayable_options, self.menu_min, self.num_options),
                                 (self.root_x + self.width - 24, self.root_y))

            # Draw each menu option
            row_y = 0
            displayable_options = self.current_menu[1][self.menu_min:self.menu_max]
            for option in displayable_options:
                is_selected = self.menu_pos == self.current_menu[1].index(option)
                x_offset = 0 if is_selected else 16

                position_x, position_y = self.root_x, self.root_y + row_y * self.option_height
                box = self.draw_menu_box(self.width - x_offset, self.option_height,
                                         background=light_team_color if is_selected else shadow_color)
                game_screen.blit(box, (position_x - 24 + x_offset, position_y))

                if isinstance(option[0], str):
                    # Render arbitrary text
                    # Format the text a bit
                    text = option[0]\
                        .replace("_", " ")\
                        .replace(".map", "")\
                        .replace(".sav", "")\
                        .title()

                    # Render arbitrary text
                    game_screen.blit(draw_text(text, light_color, dark_color), (position_x + 8, position_y + 8))

                    # Render map previews if we're trying to select a map
                    if is_selected and self.current_menu[0] in [Option.NEW_GAME, Option.NEW_MAP,
                                                                Option.LOAD_GAME, Option.LOAD_MAP,
                                                                Option.NEW_NETWORK_GAME, Option.LOAD_NETWORK_GAME]:
                        asset_type = AssetType.MAP if self.current_menu[0] in [Option.NEW_GAME, Option.NEW_MAP,
                                                                               Option.NEW_NETWORK_GAME, Option.LOAD_MAP] else AssetType.SAVE

                        container_height = 24 * self.max_displayable_options
                        container_width = self.width - 24

                        map_preview = draw_map_preview_from_file(container_width, container_height, option[0], asset_type=asset_type)
                        game_screen.blit(map_preview, (self.root_x - container_width - 24, self.root_y))

                elif option[0] in Setting:
                    # Display the setting prompt and the current value
                    display_string = get_string(formatted_strings, option[0]).format(SETTINGS.get_unsaved(option[0]))
                    game_screen.blit(draw_text(display_string, light_color, dark_color), (position_x + 24, position_y + 8))

                else:
                    # Display the icon for the option
                    game_screen.blit(spr_main_menu_option[option[0]], (position_x - 24 + x_offset, position_y))
                    # Display prerendered text
                    game_screen.blit(get_text(main_menu_strings, option[0]), (position_x + 24, position_y + 8))

                row_y += 1
