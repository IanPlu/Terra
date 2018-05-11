from terra.constants import HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.menu.menu import Menu
from terra.resources.assets import light_team_color, shadow_color, spr_main_menu_option
from terra.strings import get_text, main_menu_strings
from terra.team.team import Team


# Settings menu for the pre-match lobby.
class LobbySettings(Menu):
    def __init__(self, teams):
        self.options = []

        super().__init__(num_options=len(self.options),
                         max_displayable_options=3,
                         displayable_buffer=1,
                         root_x=HALF_RES_WIDTH,
                         root_y=HALF_RES_HEIGHT + len(teams) * 24,
                         width=168,
                         option_height=24)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.cancel)

    def confirm(self):
        pass

    def cancel(self):
        pass

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        row_y = 0

        # Render any menu options we have
        for option in self.options:
            position_x, position_y = self.root_x, self.root_y + row_y * 24
            is_selected = self.menu_pos == self.options.index(option)
            x_offset = 0 if is_selected else 16

            box = self.draw_menu_box(self.width - x_offset, self.option_height,
                                     background=light_team_color[Team.RED] if is_selected else shadow_color[Team.RED])
            game_screen.blit(box, (position_x - 24 + x_offset, position_y))

            game_screen.blit(spr_main_menu_option[option], (position_x - 24 + x_offset, position_y))
            game_screen.blit(get_text(main_menu_strings, option), (position_x + 24 + 8, position_y + 4))

            row_y += 1