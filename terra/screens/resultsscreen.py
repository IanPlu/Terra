from pygame import Surface, SRCALPHA

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.resources.assets import clear_color
from terra.team.team import Team
from terra.ui.results import Results


# Screen for displaying the results of a battle.
# Display the winner / loser, and statistics about the match.
class ResultsScreen(GameScreen):
    def __init__(self, results):
        super().__init__()

        self.results = Results(results)

    def destroy(self):
        super().destroy()
        if self.results:
            self.results.destroy()

    def render(self, ui_screen):
        super().render(ui_screen)
        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        self.results.render(game_screen, ui_screen)

        return game_screen
