from pygame.constants import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_CONFIRM, KB_CANCEL, KB_MENU, KB_SCROLL_DOWN, KB_SCROLL_UP
from terra.mainmenu.option import Option
from terra.mainmenu.textinput import TextInput, FILTER_IP, FILTER_FILENAME
from terra.managers.mapmanager import get_loadable_maps
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color
from terra.settings import SCREEN_SCALE
from terra.strings import get_text, main_menu_strings
from terra.team import Team
from terra.util.drawingutil import draw_text
from terra.util.mathutil import clamp

displayable_buffer = 1
max_displayable_options = 5


# Convert a list of loadable maps to selectable options: [(display name, filename), (...)]
def convert_loadable_maps_to_options(suffix):
    options = []
    for mapname in get_loadable_maps(suffix):
        options.append((mapname, []))
    return options


# Generate the default main menu.
def generate_menu():
    loadable_maps = convert_loadable_maps_to_options(".map")
    loadable_saves = convert_loadable_maps_to_options(".sav")

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
        (Option.SETTINGS, []),
        (Option.QUIT, [])
    ]

    return Option.START, start_menu_options


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

        self.root_x = RESOLUTION_WIDTH // 2
        self.root_y = RESOLUTION_HEIGHT // 2 - 48

        self.text_input = None

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

    def set_cursor_pos_to_mouse_coords(self):
        self.current_menu_pos = clamp((int(pygame.mouse.get_pos()[1] / SCREEN_SCALE) - self.root_y - 24) // 24 +
                                      self.current_menu_min, self.current_menu_min, self.current_menu_max)

    def scroll_menu_pos_up(self):
        self.current_menu_min = clamp(self.current_menu_min - 1, 0, self.num_options - max_displayable_options)
        self.clamp_menu_bounds()

    def scroll_menu_pos_down(self):
        self.current_menu_min = clamp(self.current_menu_min + 1, 0, self.num_options - max_displayable_options)
        self.clamp_menu_bounds()

    def clamp_menu_bounds(self):
        self.current_menu_min = clamp(self.current_menu_min, 0, self.num_options - max_displayable_options)
        self.current_menu_max = clamp(self.current_menu_min + max_displayable_options, 0, self.num_options)

    def confirm(self):
        if 0 <= self.current_menu_pos < self.num_options:
            selection = self.current_menu[1][self.current_menu_pos]

            if len(selection[1]) > 0:
                self.current_menu = selection
                self.current_menu_pos = 0
                self.num_options = len(selection[1])
                self.clamp_menu_bounds()
            else:
                self.handle_menu_selection(selection)

    def cancel(self):
        self.current_menu = generate_menu()
        self.current_menu_pos = 0
        self.num_options = len(self.current_menu[1])
        self.clamp_menu_bounds()

    def handle_menu_selection(self, option):
        if self.current_menu[0] in [Option.NEW_GAME, Option.LOAD_GAME, Option.LOAD_MAP]:
            publish_game_event(MENU_SELECT_OPTION, {
                'option': self.current_menu[0],
                'mapname': option[0]
            })
        elif self.current_menu[0] in [Option.NEW_NETWORK_GAME, Option.LOAD_NETWORK_GAME]:
            publish_game_event(MENU_SELECT_OPTION, {
                'option': self.current_menu[0],
                'mapname': option[0],
                'address': "localhost"
            })
        elif option[0] == Option.JOIN_GAME:
            self.text_input = TextInput("IP_INPUT", option[0], default_text="localhost", input_filter=FILTER_IP)
        elif option[0] == Option.NEW_MAP:
            self.text_input = TextInput("MAPNAME_INPUT", option[0], default_text="new_map", input_filter=FILTER_FILENAME)
        else:
            publish_game_event(MENU_SELECT_OPTION, {
                'option': option[0]
            })

    def step(self, event):
        super().step(event)

        if self.text_input:
            self.text_input.step(event)

            if is_event_type(event, TEXT_CANCEL_INPUT):
                self.text_input = None
            elif is_event_type(event, TEXT_SUBMIT_INPUT):
                self.text_input = None
                if event.tag == Option.NEW_MAP:
                    publish_game_event(MENU_SELECT_OPTION, {
                        'option': event.tag,
                        'mapname': event.input + ".map"
                    })
                elif event.tag == Option.JOIN_GAME:
                    publish_game_event(MENU_SELECT_OPTION, {
                        'option': event.tag,
                        'address': event.input
                    })
        else:

            if event.type == KEYDOWN:
                if event.key in KB_UP:
                    self.cursor_up()
                elif event.key in KB_DOWN:
                    self.cursor_down()
                elif event.key in KB_CONFIRM:
                    self.confirm()
                elif event.key in KB_CANCEL or event.key in KB_MENU:
                    self.cancel()
            elif event.type == MOUSEMOTION:
                self.set_cursor_pos_to_mouse_coords()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CONFIRM:
                    self.confirm()
                elif event.button in KB_CANCEL or event.button in KB_MENU:
                    self.cancel()
                elif event.button in KB_SCROLL_DOWN:
                    self.scroll_menu_pos_down()
                    self.set_cursor_pos_to_mouse_coords()
                elif event.button in KB_SCROLL_UP:
                    self.scroll_menu_pos_up()
                    self.set_cursor_pos_to_mouse_coords()

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        if self.text_input:
            self.text_input.render(game_screen, ui_screen)
        else:
            # Draw text for the menu title
            game_screen.blit(get_text(main_menu_strings, self.current_menu[0]), (self.root_x - 12, self.root_y))

            # Draw text for each menu option
            row_y = 1
            displayable_options = self.current_menu[1][self.current_menu_min:self.current_menu_max]
            for option in displayable_options:
                is_selected = self.current_menu_pos == self.current_menu[1].index(option)
                if is_selected:
                    x_offset = 0
                else:
                    x_offset = 16

                position_x, position_y = self.root_x, self.root_y + row_y * 24
                box_width = 24 * 6
                game_screen.fill(light_color, (position_x - 24 - 1 + x_offset, position_y - 1, box_width + 3 - x_offset, 24))
                game_screen.fill(light_team_color[Team.RED] if is_selected else shadow_color[Team.RED],
                                 (position_x - 24 + x_offset, position_y, box_width - x_offset, 21))

                if isinstance(option[0], str):
                    # Render arbitrary text
                    game_screen.blit(draw_text(option[0], light_color, shadow_color[Team.RED]), (position_x + 8, position_y))
                else:
                    # Display prerendered text
                    game_screen.blit(get_text(main_menu_strings, option[0]), (position_x + 8, position_y))

                row_y += 1

        return game_screen
