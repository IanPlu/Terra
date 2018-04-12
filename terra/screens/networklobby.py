from pygame import Surface, SRCALPHA
from pygame.mouse import get_pos

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
from terra.map.minimap import draw_map_preview
from terra.menu.option import Option
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color, dark_color
from terra.settings import SETTINGS, Setting
from terra.strings import get_text, label_strings, main_menu_strings
from terra.team.team import Team
from terra.util.drawingutil import draw_text
from terra.util.mathutil import clamp
from terra.managers.session import Session, Manager

menu_width = 168


# Pre-match screen for network games.
# Gives room for players to trickle into an online game, change team assignments, etc.
class NetworkLobby(GameScreen):
    def __init__(self, is_host, map_name=None, map_type=None, address=None):
        super().__init__()

        if is_host:
            self.map_name, self.bitmap, self.pieces, self.team_data, self.upgrades, self.meta = \
                Session.set_up_network_game_as_host(map_name, map_type, address)
        else:
            self.map_name, self.bitmap, self.pieces, self.team_data, self.upgrades, self.meta = \
                Session.set_up_network_game_as_client(address)

        self.teams = [Team[team.split(' ')[0]] for team in self.teams]

        self.root_x = HALF_RES_WIDTH
        self.root_y = HALF_RES_HEIGHT - 48

        self.options = [Option.LEAVE_LOBBY]
        self.option_pos = 0

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_ALL_TEAMS_FILLED, self.on_all_teams_filled)
        event_bus.register_handler(EventType.E_TEAM_LEFT, self.on_team_left)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.UP, self.cursor_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.cursor_down)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.exit_lobby)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.exit_lobby)
        input_handler.register_handler(InputAction.MOTION, None, self.set_cursor_pos_to_mouse_coords)

    def on_all_teams_filled(self, event):
        if self.get_manager(Manager.NETWORK).is_host:
            self.options.insert(0, Option.START_BATTLE)

    def on_team_left(self, event):
        if Option.START_BATTLE in self.options:
            self.options.remove(Option.START_BATTLE)
            self.option_pos = 0

    def normalize_option_pos(self):
        if self.option_pos < 0:
            self.option_pos = len(self.options) - 1
        if self.option_pos > len(self.options) - 1:
            self.option_pos = 0

    def cursor_up(self):
        self.option_pos -= 1
        self.normalize_option_pos()

    def cursor_down(self):
        self.option_pos += 1
        self.normalize_option_pos()

    def cursor_in_menu_bounds(self):
        mouse_x = get_pos()[0] / SETTINGS.get(Setting.SCREEN_SCALE)
        mouse_y = get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE)

        x_in = self.root_x - 24 <= mouse_x <= self.root_x + menu_width - 24
        y_in = self.root_y <= mouse_y <= self.root_y + 24 * (len(self.teams) + len(self.options)) + 24

        return x_in and y_in

    def set_cursor_pos_to_mouse_coords(self):
        if self.cursor_in_menu_bounds():
            self.option_pos = clamp((int(get_pos()[1] / SETTINGS.get(Setting.SCREEN_SCALE))
                                     - self.root_y - 24 - 24 * len(self.teams)) // 24, 0, len(self.options) - 1)

    def exit_lobby(self):
        publish_game_event(EventType.E_EXIT_LOBBY, {})

    def start_battle(self):
        publish_game_event(EventType.E_START_BATTLE, {
            'team': self.teams[0]
        })

    def confirm(self):
        option = self.options[self.option_pos]

        if option == Option.LEAVE_LOBBY:
            self.exit_lobby()
        elif option == Option.START_BATTLE:
            self.start_battle()

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        # Render a minimap preview of the current map
        minimap = draw_map_preview(menu_width - 24, 120, self.bitmap, self.pieces, self.team_data)
        game_screen.blit(minimap, (self.root_x - menu_width, self.root_y + 23))

        # Render the current lobby status-- open and filled teams
        row_y = 1
        for team in self.teams:
            position_x, position_y = self.root_x, self.root_y + row_y * 24

            filled_teams = self.get_manager(Manager.NETWORK).filled_teams
            is_filled = team in filled_teams.keys()
            x_offset = 0 if is_filled else 16

            game_screen.fill(light_color, (position_x - 24 - 1 + x_offset, position_y - 1, menu_width + 3 - x_offset, 24))
            game_screen.fill(light_team_color[team] if is_filled else shadow_color[team],
                             (position_x - 24 + x_offset, position_y, menu_width - x_offset, 21))

            if team in filled_teams:
                game_screen.blit(draw_text(filled_teams[team], light_color, dark_color), (position_x + 8, position_y + 4))
            else:
                game_screen.blit(get_text(label_strings, "OPEN_TEAM"), (position_x + 8, position_y + 4))

            row_y += 1

        # Render any menu options we have
        for option in self.options:
            position_x, position_y = self.root_x, self.root_y + row_y * 24
            is_selected = self.option_pos == self.options.index(option)
            x_offset = 0 if is_selected else 16

            game_screen.fill(light_color, (position_x - 24 - 1 + x_offset, position_y - 1, menu_width + 3 - x_offset, 24))
            game_screen.fill(light_team_color[Team.RED] if is_selected else shadow_color[Team.RED],
                             (position_x - 24 + x_offset, position_y, menu_width - x_offset, 21))

            game_screen.blit(get_text(main_menu_strings, option), (position_x + 8, position_y + 4))

            row_y += 1

        return game_screen
