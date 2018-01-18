from terra.engine.gameobject import GameObject
from terra.settings import TICK_RATE


# Game object class with support for rendering animation.
# Automatically ticks the frame to display over time.
# Framerate: How many times per second to progress the animation
class AnimatedGameObject(GameObject):
    def __init__(self, images=[], framerate=1):
        super().__init__()
        self.images = images
        self.framerate = framerate

        self.tick = 0
        self.current_frame = 0

        self.sprite = images[0]

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        # Tick the image and update the frame
        self.current_frame = self.current_frame + self.framerate / TICK_RATE
        if self.current_frame >= len(self.images):
            self.current_frame = 0

        # Set the image to display
        self.sprite = self.images[int(self.current_frame)]
