from pygame import Surface, SRCALPHA, KEYDOWN, MOUSEBUTTONDOWN

from terra.keybindings import KB_CONFIRM, KB_CANCEL, KB_MENU
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.managers.managers import Managers
from terra.managers.mapmanager import generate_minimap
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color, dark_color
from terra.team import Team
from terra.event import publish_game_event, E_EXIT_LOBBY, E_START_BATTLE
from terra.util.drawingutil import draw_text

menu_width = 168


# Pre-match screen for network games.
# Gives room for players to trickle into an online game, change team assignments, etc.
class NetworkLobby(GameScreen):
    def __init__(self, map_name, bitmap, pieces, teams, upgrades, meta):
        super().__init__()

        self.map_name = map_name
        self.bitmap = bitmap
        self.pieces = pieces
        self.team_data = teams
        self.teams = [Team[team.split(' ')[0]] for team in teams]
        self.upgrades = upgrades
        self.meta = meta

        Managers.initialize_managers(map_name, bitmap, pieces, teams, upgrades, meta)

        self.root_x = HALF_RES_WIDTH
        self.root_y = HALF_RES_HEIGHT - 48

    def step(self, event):
        super().step(event)

        if event.type == KEYDOWN:
            if event.key in KB_CONFIRM and Managers.network_manager.is_host:
                publish_game_event(E_START_BATTLE, {})
            elif event.key in KB_CANCEL or event.key in KB_MENU:
                publish_game_event(E_EXIT_LOBBY, {})
        elif event.type == MOUSEBUTTONDOWN:
            if event.button in KB_CONFIRM and Managers.network_manager.is_host:
                publish_game_event(E_START_BATTLE, {})
            elif event.button in KB_CANCEL or event.button in KB_MENU:
                publish_game_event(E_EXIT_LOBBY, {})

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        # Render a minimap preview of the current map
        minimap = generate_minimap(self.bitmap)
        game_screen.blit(minimap, (self.root_x - 25 - minimap.get_width(), self.root_y + 24))

        # Render the current lobby status for the host-- open and filled teams
        if Managers.network_manager.is_host:
            row_y = 1
            for team in self.teams:
                position_x, position_y = self.root_x, self.root_y + row_y * 24
                is_filled = team in Managers.network_manager.filled_teams.keys()
                x_offset = 0 if is_filled else 16

                game_screen.fill(light_color, (position_x - 24 - 1 + x_offset, position_y - 1, menu_width + 3 - x_offset, 24))
                game_screen.fill(light_team_color[team] if is_filled else shadow_color[team],
                                 (position_x - 24 + x_offset, position_y, menu_width - x_offset, 21))

                if team in Managers.network_manager.filled_teams:
                    game_screen.blit(draw_text(Managers.network_manager.filled_teams[team], light_color, dark_color), (position_x + 8, position_y + 4))

                row_y += 1
        else:
            # TODO: Show something to connected clients
            pass

        return game_screen
