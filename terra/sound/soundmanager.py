from terra.engine.gameobject import GameObject
from terra.settings import SETTINGS, Setting
from terra.resources.assets import all_sounds


# Manager for playing sound effects.
class SoundManager(GameObject):
    def __init__(self):
        super().__init__()

    def play_sound(self, sound_type):
        sound = sound_type.value

        sound.set_volume(SETTINGS.get(Setting.SFX_VOLUME) / 100)
        sound.play()

    def adjust_volume(self, new_volume):
        for sound in all_sounds:
            sound.set_volume(new_volume)

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
