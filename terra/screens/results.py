from pygame import Surface, SRCALPHA

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
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

        self.winning_teams = results["winning_teams"]
        self.all_teams = results["all_teams"]
        self.team_stats = results["team_stats"]

        Managers.combat_logger.log_results(self.winning_teams, self.all_teams, self.team_stats)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.exit_results)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.exit_results)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.exit_results)

    def exit_results(self):
        publish_game_event(EventType.E_EXIT_RESULTS, {})

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        base_x = 24

        y = 0
        for team in self.winning_teams:
            game_screen.blit(draw_text(get_string(formatted_strings, "RESULTS_HEADER").format(get_string(team_name_strings, team)),
                                       light_color, shadow_color[Team.RED]), (base_x, y * 24))
            y += 1

        x = 0
        last_y = y
        for team in self.all_teams:
            y = last_y + 1
            game_screen.blit(get_text(team_name_strings, team), (base_x + x, y * 24))

            y += 1
            for stat, value in self.team_stats[team].items():
                game_screen.blit(draw_text(get_string(formatted_strings, stat).format(value),
                                           light_color, shadow_color[Team.RED]), (base_x + x, y * 24))
                y += 1

            x += HALF_RES_WIDTH

        game_screen.blit(draw_text(get_string(label_strings, "RESULTS_PROMPT"), light_color, shadow_color[Team.RED]), (base_x, y * 24))

        return game_screen
