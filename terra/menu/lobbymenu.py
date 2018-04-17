from terra.constants import HALF_RES_HEIGHT, HALF_RES_WIDTH
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.menu.lobbysettings import LobbySettings
from terra.menu.menu import Menu
from terra.menu.option import Option
from terra.resources.assets import light_team_color, shadow_color, spr_main_menu_option
from terra.strings import get_text, main_menu_strings


# Menu for the pre-match lobby.
class LobbyMenu(Menu):
    def __init__(self, teams, is_host=False):
        self.teams = teams
        self.is_host = is_host

        self.options = self.generate_menu_options()
        self.settings = None

        super().__init__(num_options=len(self.options),
                         max_displayable_options=3,
                         displayable_buffer=1,
                         root_x=HALF_RES_WIDTH,
                         root_y=HALF_RES_HEIGHT + len(teams) * 24,
                         width=168,
                         option_height=24)

    def destroy(self):
        super().destroy()
        if self.settings:
            self.settings.destroy()
            self.settings = None

    def generate_menu_options(self):
        options = [Option.LEAVE_LOBBY]

        # if self.is_host:
        #     options.append(Option.SETTINGS)

        if not self.is_network_game():
            options.append(Option.START_BATTLE)

        options.reverse()

        return options

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_ALL_TEAMS_FILLED, self.on_all_teams_filled)
        event_bus.register_handler(EventType.E_TEAM_LEFT, self.on_team_left)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.cancel)

    def is_accepting_input(self):
        return self.settings is None

    def confirm(self):
        super().confirm()
        option = self.options[self.menu_pos]

        if option == Option.LEAVE_LOBBY:
            self.exit_lobby()
        elif option == Option.START_BATTLE:
            self.start_battle()
        elif option == Option.SETTINGS:
            self.open_settings()

    def cancel(self):
        super().cancel()
        self.exit_lobby()

    def start_battle(self):
        publish_game_event(EventType.E_START_BATTLE, {})

    def exit_lobby(self):
        publish_game_event(EventType.E_EXIT_LOBBY, {})

    def on_all_teams_filled(self, event):
        if self.get_manager(Manager.NETWORK).is_host:
            self.options.insert(0, Option.START_BATTLE)
            self.num_options += 1

    def on_team_left(self, event):
        if Option.START_BATTLE in self.options:
            self.options.remove(Option.START_BATTLE)
            self.menu_pos = 0
            self.num_options -= 1

    def open_settings(self):
        self.settings = LobbySettings(self.teams)

    def close_settings(self):
        if self.settings:
            self.settings.destroy()
            self.settings = None

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
                                     background=light_team_color if is_selected else shadow_color)
            game_screen.blit(box, (position_x - 24 + x_offset, position_y))

            game_screen.blit(spr_main_menu_option[option], (position_x - 24 + x_offset, position_y))
            game_screen.blit(get_text(main_menu_strings, option), (position_x + 24 + 8, position_y + 4))

            row_y += 1
