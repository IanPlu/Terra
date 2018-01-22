from terra.engine.gameobject import GameObject
from terra.constants import *
from terra.settings import *
from terra.util.drawingutil import draw_nine_slice_sprite
from terra.resources.assets import spr_textbox


# A toast notification that pops up in the corner of the screen and then dissipates
class ToastNotification(GameObject):
    def __init__(self, parent, text, team):
        super().__init__()
        self.parent = parent
        self.text = text
        self.team = team

        # Number of seconds for the notification to live
        self.lifetime = 3 * TICK_RATE

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.parent.remove_toast_notification()

        x = 0
        y = RESOLUTION_HEIGHT - GRID_HEIGHT - 32

        ui_screen.blit(draw_nine_slice_sprite(spr_textbox[self.team], 8, 24, 4), (x, y))
        ui_screen.blit(self.text, (x + 8, y + 8))
