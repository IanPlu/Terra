from terra.engine.gameobject import GameObject
from terra.constants import TICK_RATE
from terra.util.mathutil import clamp


# Game object class with support for rendering animation.
# Automatically ticks the frame to display over time.
# Size: H&W of each frame of animation. The image passed in is assumed to be a horizontal strip of square frames.
# Framerate: How many times per second to progress the animation
# Indexed: Whether the sprite is of the format image[animation_frame][index], instead of just image[animation_frame]
# Use Global Animation Frame: If true, uses a global frame to keep things synced to the same animation frame
class AnimatedGameObject(GameObject):
    global_animation_frame = 0
    global_animation_framerate = 1
    global_num_frames = 4

    def __init__(self, image, size=24, framerate=1, indexed=False, use_global_animation_frame=False):
        super().__init__()
        self.image = image
        self.size = size
        self.framerate = framerate

        self.tick = 0
        self.current_frame = 0

        self.indexed = indexed
        self.use_global_animation_frame = use_global_animation_frame

        self.sprite = self.image.subsurface(self.size * int(self.current_frame), 0,
                                            self.size, self.size)

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

            self.current_frame = clamp(AnimatedGameObject.global_animation_frame, 0, self.image.get_width() // self.size - 1)
        else:
            # Tick the image and update the frame
            self.current_frame += self.framerate / TICK_RATE
            if self.current_frame >= self.image.get_width() // self.size:
                self.current_frame = 0
                self.on_animation_reset()

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        old_frame = self.current_frame
        self.update_frame()

        # Only update the sprite if it's changed
        if not self.current_frame == old_frame:
            if self.indexed:
                self.sprite = self.image.subsurface(self.size * self.get_index(), self.size * int(self.current_frame),
                                                    self.size, self.size)
            else:
                # Set the image to display
                self.sprite = self.image.subsurface(self.size * int(self.current_frame), 0, self.size, self.size)
