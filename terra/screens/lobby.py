from pygame import Surface, SRCALPHA

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.managers.session import Session, Manager
from terra.map.minimap import draw_map_preview
from terra.menu.lobbymenu import LobbyMenu
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color, dark_color
from terra.strings import get_text, label_strings
from terra.team.team import Team
from terra.util.drawingutil import draw_text

menu_width = 168


# Pre-match screen for games.
# Gives room for players to trickle into an online game, change team assignments, etc.
class Lobby(GameScreen):
    def __init__(self, is_host, map_name=None, map_type=None, address=None):
        super().__init__()

        if address:
            if is_host:
                self.map_name, self.bitmap, self.pieces, self.team_data, self.upgrades, self.meta = \
                    Session.set_up_network_game_as_host(map_name, map_type, address)
            else:
                self.map_name, self.bitmap, self.pieces, self.team_data, self.upgrades, self.meta = \
                    Session.set_up_network_game_as_client(address)
        else:
            self.map_name, self.bitmap, self.pieces, self.team_data, self.upgrades, self.meta = \
                    Session.set_up_local_game(map_name, map_type)

        self.teams = [Team[team.split(' ')[0]] for team in self.team_data]

        self.root_x = HALF_RES_WIDTH
        self.root_y = HALF_RES_HEIGHT - 24

        self.lobby_menu = LobbyMenu(teams=self.teams, is_host=is_host)

    def destroy(self):
        super().destroy()

        if self.lobby_menu:
            self.lobby_menu.destroy()

    def step(self, event):
        super().step(event)

        if self.lobby_menu:
            self.lobby_menu.step(event)

    def render(self, ui_screen):
        super().render(ui_screen)

        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        # Render a minimap preview of the current map
        minimap = draw_map_preview(menu_width - 24, 144, self.bitmap, self.pieces, self.team_data)
        game_screen.blit(minimap, (self.root_x - minimap.get_width() - 24, self.root_y))

        # Render the current lobby status-- open and filled teams
        if self.is_network_game():
            row_y = 0
            for team in self.teams:
                position_x, position_y = self.root_x, self.root_y + row_y * 24 + 1

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

        if self.lobby_menu:
            self.lobby_menu.render(game_screen, ui_screen)

        return game_screen
