from pygame import Surface, SRCALPHA

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
from terra.menu.menu import Menu
from terra.piece.piecesubtype import PieceSubtype
from terra.resources.assets import clear_color, light_color, shadow_color, light_team_color, dark_color, spr_pieces
from terra.strings import get_string, get_text, formatted_strings, team_name_strings, label_strings
from terra.team.team import Team
from terra.util.drawingutil import draw_text


# Screen for displaying the results of a battle.
# Display the winner / loser, and statistics about the match.
class ResultsScreen(GameScreen):
    def __init__(self, results):
        super().__init__()

        self.winning_team = results["winning_team"]
        self.winning_pieces = [piece for piece in results["winning_pieces"] if piece.piece_subtype == PieceSubtype.UNIT]
        self.all_teams = results["all_teams"]
        self.team_stats = results["team_stats"]
        self.turn = results["turn"]

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
        base_y = 24

        # Draw winning team
        game_screen.blit(Menu.draw_menu_box(RESOLUTION_WIDTH - 48, 24, background=light_team_color, team=self.winning_team), (base_x, base_y))
        game_screen.blit(draw_text(get_string(formatted_strings, "RESULTS_HEADER").format(
            get_string(team_name_strings, self.winning_team), self.turn), light_color, dark_color), (base_x + 8, base_y + 8))

        x = 0
        for piece in self.winning_pieces:
            if x < RESOLUTION_WIDTH - 24:
                game_screen.blit(spr_pieces[piece.team][piece.piece_type].subsurface(0, 0, 24, 24), (base_x + x, base_y + 24))
                x += 12

        x = 0
        y = 2
        team_box_width = (RESOLUTION_WIDTH - (36 * len(self.all_teams))) // len(self.all_teams)
        for team in self.all_teams:
            stats = self.team_stats[team].items()

            game_screen.blit(Menu.draw_menu_box(team_box_width, (len(stats) + 1) * 24, team=team), (base_x + x, base_y + (y * 24)))
            game_screen.blit(get_text(team_name_strings, team), (base_x + x + 8, base_y + (y * 24) + 8))

            y += 1
            for stat, value in stats:
                game_screen.blit(draw_text(get_string(formatted_strings, stat).format(value),
                                           light_color, dark_color), (base_x + x + 8, base_y + (y * 24) + 8))
                y += 1

            x += team_box_width + 24
            y = 2

        results_text = draw_text(get_string(label_strings, "RESULTS_PROMPT"), light_color, shadow_color[Team.RED])
        game_screen.blit(results_text, (RESOLUTION_WIDTH - results_text.get_width() - 24, RESOLUTION_HEIGHT - 16))

        return game_screen
