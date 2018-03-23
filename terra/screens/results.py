from pygame import Surface, SRCALPHA, KEYDOWN, MOUSEBUTTONDOWN

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH
from terra.engine.gamescreen import GameScreen
from terra.event import publish_game_event, E_EXIT_RESULTS
from terra.keybindings import KB_CONFIRM, KB_CANCEL, KB_MENU
from terra.managers.managers import Managers
from terra.resources.assets import clear_color, light_color, shadow_color
from terra.strings import get_string, get_text, formatted_strings, team_name_strings, label_strings
from terra.team import Team
from terra.util.drawingutil import draw_text


# Screen for displaying the results of a battle.
# Display the winner / loser, and statistics about the match.
class ResultsScreen(GameScreen):
    def __init__(self, results):
        super().__init__()

        self.teams = results["teams"]
        self.losing_teams = results["bases_destroyed"]
        self.team_stats = results["team_stats"]

        Managers.combat_logger.log_results(self.teams, self.losing_teams, self.team_stats)

    def step(self, event):
        super().step(event)

        if event.type == KEYDOWN:
            if event.key in KB_CONFIRM or event.key in KB_CANCEL or event.key in KB_MENU:
                publish_game_event(E_EXIT_RESULTS, {})
        elif event.type == MOUSEBUTTONDOWN:
            if event.button in KB_CONFIRM or event.button in KB_CANCEL or event.button in KB_MENU:
                publish_game_event(E_EXIT_RESULTS, {})

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        y = 0
        for team in self.losing_teams:
            game_screen.blit(draw_text("{} team lost".format(team), light_color, shadow_color[Team.RED]), (0, y * 24))
            y += 1

        x = 0
        last_y = y
        for team in self.teams:
            y = last_y + 1
            game_screen.blit(get_text(team_name_strings, team), (x, y * 24))

            y += 1
            for stat, value in self.team_stats[team].items():
                game_screen.blit(draw_text(get_string(formatted_strings, stat).format(value),
                                           light_color, shadow_color[Team.RED]), (x, y * 24))
                y += 1

            x += HALF_RES_WIDTH

        game_screen.blit(draw_text(get_string(label_strings, "RESULTS_PROMPT"), light_color, shadow_color[Team.RED]), (0, y * 24))

        return game_screen
