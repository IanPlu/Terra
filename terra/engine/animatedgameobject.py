from terra.engine.gameobject import GameObject
from terra.settings import TICK_RATE


# Game object class with support for rendering animation.
# Automatically ticks the frame to display over time.
# Framerate: How many times per second to progress the animation
# Indexed: Whether the sprite is of the format image[animation_frame][index], instead of just image[animation_frame]
# Use Global Animation Frame: If true, uses a global frame to keep things synced to the same animation frame
class AnimatedGameObject(GameObject):
    global_animation_frame = 0
    global_animation_framerate = 1
    global_num_frames = 4

    def __init__(self, images, framerate=1, indexed=False, use_global_animation_frame=False):
        super().__init__()
        self.images = images
        self.framerate = framerate

        self.tick = 0
        self.current_frame = 0

        self.sprite = images[0]
        self.indexed = indexed
        self.use_global_animation_frame = use_global_animation_frame

    # Triggered when the animation loops and resets to frame 0.
    def on_animation_reset(self):
        pass

    # If indexed=True, will call this function to determine the sprite index to use
    def get_index(self):
        return 0

    @staticmethod
    def update_global_frame():
        AnimatedGameObject.global_animation_frame += AnimatedGameObject.global_animation_framerate / TICK_RATE
        if AnimatedGameObject.global_animation_frame >= AnimatedGameObject.global_num_frames:
            AnimatedGameObject.global_animation_frame = 0

    def update_frame(self):
        if self.use_global_animation_frame:
            # Use the global frame
            # Update it if no one else has
            if AnimatedGameObject.global_animation_frame == self.current_frame:
                AnimatedGameObject.update_global_frame()

            self.current_frame = AnimatedGameObject.global_animation_frame
        else:
            # Tick the image and update the frame
            self.current_frame += self.framerate / TICK_RATE
            if self.current_frame >= len(self.images):
                self.current_frame = 0
                self.on_animation_reset()

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.update_frame()

        if self.indexed:
            self.sprite = self.images[int(self.current_frame)][self.get_index()]
        else:
            # Set the image to display
            self.sprite = self.images[int(self.current_frame)]
