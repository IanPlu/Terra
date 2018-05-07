from pygame import Surface, SRCALPHA

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT, HALF_RES_WIDTH
from terra.engine.gamescreen import GameScreen
from terra.menu.mainmenu import MainMenu
from terra.resources.assets import clear_color, spr_title_text
from terra.team.team import Team


# The main title screen.
# Sets up the screen, and contains + delegates to a main menu object.
class TitleScreen(GameScreen):
    def __init__(self):
        super().__init__()

        self.main_menu = MainMenu()
        self.root_x = HALF_RES_WIDTH

    def destroy(self):
        super().destroy()
        if self.main_menu:
            self.main_menu.destroy()

    def step(self, event):
        super().step(event)

        if self.main_menu:
            self.main_menu.step(event)

    def render(self, ui_screen):
        super().render(ui_screen)

        game_screen = Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), SRCALPHA, 32)
        game_screen.fill(clear_color[Team.RED])

        game_screen.blit(spr_title_text, (self.root_x - spr_title_text.get_width() // 2, 24))

        if self.main_menu:
            self.main_menu.render(game_screen, ui_screen)

        return game_screen
