from pygame import KEYDOWN, MOUSEBUTTONDOWN

from terra.constants import HALF_RES_WIDTH, HALF_RES_HEIGHT
from terra.engine.gameobject import GameObject
from terra.managers.managers import Managers
from terra.resources.assets import clear_color, light_color
from terra.settings import TICK_RATE
from terra.strings import formatted_strings, get_string
from terra.util.drawingutil import draw_text


# A banner that is displayed on new turns.
# Functions similarly to AnimatedEffect, but doesn't use any sprites.
class TurnBanner(GameObject):
    def __init__(self, parent, turn_number):
        super().__init__()
        self.parent = parent
        self.turn_number = turn_number

        self.tick = 0
        self.is_alive = True

        self.height = 2
        self.max_height = 24

    def step(self, event):
        super().step(event)

        if event.type in [KEYDOWN, MOUSEBUTTONDOWN]:
            self.finish_animation()

    def finish_animation(self):
        self.is_alive = False
        self.parent.destroy_effect(self)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.tick += 2.5 / TICK_RATE

        if self.height < self.max_height and self.tick < 1:
            self.height += 2
        elif self.height > 2 and (2 < self.tick < 3):
            self.height -= 2
        elif (2 < self.tick < 3) and self.height == 2:
            # Finish the animation once we've finished shrinking
            self.finish_animation()

        ui_screen.fill(light_color, (0 + HALF_RES_WIDTH / 2, HALF_RES_HEIGHT - self.height // 2, HALF_RES_WIDTH, self.height))
        ui_screen.fill(clear_color[Managers.player_manager.active_team], (1 + HALF_RES_WIDTH / 2, HALF_RES_HEIGHT + 1 - self.height // 2, HALF_RES_WIDTH - 2, self.height - 3))

        if self.height == self.max_height:
            text_surface = draw_text(get_string(formatted_strings, "NEW_TURN_MESSAGE").format(self.turn_number), light_color)
            ui_screen.blit(text_surface, (HALF_RES_WIDTH - text_surface.get_width() // 2, HALF_RES_HEIGHT - text_surface.get_height() // 2))
