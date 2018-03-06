from terra.engine.gameobject import GameObject
from terra.settings import SFX_VOLUME
from terra.resources.assets import all_sounds


class SoundManager(GameObject):
    def __init__(self):
        super().__init__()

    def play_sound(self, sound_type):
        sound = sound_type.value

        sound.set_volume(SFX_VOLUME)
        sound.play()

    def adjust_volume(self, new_volume):
        for sound in all_sounds:
            sound.set_volume(new_volume)

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
