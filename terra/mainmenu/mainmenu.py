from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_CONFIRM, KB_CANCEL
from terra.mainmenu.option import Option
from terra.map.map import get_loadable_maps
from terra.resources.assets import clear_color, text_main_menu, light_color, shadow_color
from terra.team import Team
from terra.util.drawingutil import draw_text
from pygame.constants import KEYDOWN


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

    start_menu_options = []
    if len(loadable_maps) > 0:
        start_menu_options.append((Option.NEW_GAME, loadable_maps))
    if len(loadable_saves) > 0:
        start_menu_options.append((Option.LOAD_GAME, loadable_saves))
    if len(loadable_maps) > 0:
        start_menu_options.append((Option.LEVEL_EDITOR, loadable_maps))

    start_menu_options.append((Option.SETTINGS, []))
    start_menu_options.append((Option.QUIT, []))

    return Option.START, start_menu_options


# Main menu for the game.
# Allows player to load or start games, access the level editor, and so on
class MainMenu(GameScreen):
    def __init__(self):
        super().__init__()

        self.current_menu = generate_menu()
        self.current_menu_pos = 0
        self.num_options = len(self.current_menu[1])

    def cursor_up(self):
        self.current_menu_pos -= 1
        if self.current_menu_pos < 0:
            self.current_menu_pos = self.num_options - 1

    def cursor_down(self):
        self.current_menu_pos += 1
        if self.current_menu_pos > self.num_options - 1:
            self.current_menu_pos = 0

    def confirm(self):
        selection = self.current_menu[1][self.current_menu_pos]

        if len(selection[1]) > 0:
            self.current_menu = selection
            self.current_menu_pos = 0
            self.num_options = len(selection[1])
        else:
            self.handle_menu_selection(selection)

    def cancel(self):
        self.current_menu = generate_menu()
        self.current_menu_pos = 0
        self.num_options = len(self.current_menu[1])

    def handle_menu_selection(self, option):
        if self.current_menu[0] in [Option.NEW_GAME, Option.LOAD_GAME, Option.LEVEL_EDITOR]:
            publish_game_event(MENU_SELECT_OPTION, {
                'option': self.current_menu[0],
                'mapname': option[0]
            })
        else:
            publish_game_event(MENU_SELECT_OPTION, {
                'option': option[0]
            })

    def step(self, event):
        super().step(event)

        if event.type == KEYDOWN:
            if event.key in KB_UP:
                self.cursor_up()
            elif event.key in KB_DOWN:
                self.cursor_down()
            elif event.key in KB_CONFIRM:
                self.confirm()
            elif event.key in KB_CANCEL:
                self.cancel()

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        root_x = RESOLUTION_WIDTH // 2
        root_y = RESOLUTION_HEIGHT // 2

        # Draw text for each menu option
        row_y = 0
        for option in self.current_menu[1]:
            if option == self.current_menu[1][self.current_menu_pos]:
                x_offset = 12
            else:
                x_offset = 0

            position = (root_x + x_offset, root_y + row_y * 24)

            if isinstance(option[0], str):
                # Render arbitrary text
                game_screen.blit(draw_text(option[0], light_color, shadow_color[Team.RED]), position)
            else:
                # Display prerendered text
                game_screen.blit(text_main_menu[option[0]], position)

            row_y += 1

        return game_screen
