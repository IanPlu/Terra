from terra.constants import GRID_HEIGHT, RESOLUTION_HEIGHT, TICK_RATE
from terra.engine.gameobject import GameObject
from terra.resources.assets import light_color, clear_color
from terra.event import is_event_type, E_NEXT_PHASE


# A toast notification that pops up in the corner of the screen and then dissipates
class ToastNotification(GameObject):
    def __init__(self, parent, text, team):
        super().__init__()
        self.parent = parent
        self.text = text
        self.team = team

        self.x = 0
        self.y = RESOLUTION_HEIGHT
        self.desired_y = RESOLUTION_HEIGHT - GRID_HEIGHT * 2

        # Number of seconds for the notification to live
        self.lifetime = 3 * TICK_RATE

    def step(self, event):
        super().step(event)

        # Clear self on phase changes
        if is_event_type(event, E_NEXT_PHASE):
            self.lifetime = 0

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.parent.remove_toast_notification()

        if self.y > self.desired_y:
            self.y -= 2

        ui_screen.fill(light_color, (self.x, self.y, 192, 24))
        ui_screen.fill(clear_color[self.team], (self.x + 1, self.y + 1, 189, 22))

        ui_screen.blit(self.text, (self.x + 8, self.y + 8))
