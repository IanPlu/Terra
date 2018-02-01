from terra.mainmenu.option import Option
from terra.settings import *
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, Team
from terra.engine.gamescreen import GameScreen
from terra.resources.assets import clear_color, text_main_menu, light_color, shadow_color
from terra.util.drawingutil import draw_text
from terra.map.map import get_loadable_maps
from terra.event import *


# Convert a list of loadable maps to selectable options: [(display name, filename), (...)]
def convert_loadable_maps_to_options():
    options = []
    for mapname in get_loadable_maps():
        options.append((mapname, []))
    return options


menu_map = (
    Option.START, [
        (Option.NEW_GAME, convert_loadable_maps_to_options()),
        (Option.LEVEL_EDITOR, convert_loadable_maps_to_options()),
        (Option.SETTINGS, []),
        (Option.QUIT, [])
    ]
)


# Main menu for the game.
# Allows player to load or start games, access the level editor, and so on
class MainMenu(GameScreen):
    def __init__(self):
        super().__init__()

        self.current_menu = menu_map
        self.current_menu_pos = 0
        self.num_options = len(menu_map[1])

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
        self.current_menu = menu_map
        self.current_menu_pos = 0
        self.num_options = len(menu_map[1])

    def handle_menu_selection(self, option):
        if self.current_menu[0] == Option.NEW_GAME or self.current_menu[0] == Option.LEVEL_EDITOR:
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
