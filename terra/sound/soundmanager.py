from terra.resources.assets import all_sounds
from terra.settings import SETTINGS, Setting


# Manager for playing sound effects.
class SoundManager:
    def __init__(self):
        super().__init__()

    def play_sound(self, sound_type):
        sound = sound_type.value

        sound.set_volume(SETTINGS.get(Setting.SFX_VOLUME) / 100)
        sound.stop()
        sound.play()

    def adjust_volume(self, new_volume):
        for sound in all_sounds:
            sound.set_volume(new_volume)


SOUND = SoundManager()
