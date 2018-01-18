from terra.engine.gameobject import GameObject
from terra.constants import *
from terra.settings import *
from terra.util.drawingutil import draw_nine_slice_sprite
from terra.resources.assets import spr_textbox


# A toast notification that pops up in the corner of the screen and then dissipates
class ToastNotification(GameObject):
    def __init__(self, parent, text):
        super().__init__()
        self.text = text
        self.team = Team.RED

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        x = 0
        y = RESOLUTION_HEIGHT - GRID_HEIGHT - 32

        game_screen.blit(draw_nine_slice_sprite(spr_textbox[self.team], 8, 12, 4), (x, y))
