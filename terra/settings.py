from enum import Enum
from io import StringIO

from terra.resources.assetloading import get_asset, AssetType
from terra.util.mathutil import clamp


# Individual settings the player can change on the main menu.
class Setting(Enum):
    SCREEN_SCALE = "SCREEN_SCALE"
    SFX_VOLUME = "SFX_VOLUME"
    BGM_VOLUME = "BGM_VOLUME"


# Upper and lower bounds for specific settings
setting_bounds = {
    Setting.SCREEN_SCALE: (1, 4),
    Setting.SFX_VOLUME: (0, 100),
    Setting.BGM_VOLUME: (0, 100),
}

# How much one press modifies the setting
setting_interval = {
    Setting.SCREEN_SCALE: 1,
    Setting.SFX_VOLUME: 10,
    Setting.BGM_VOLUME: 10,
}

# Default values for each setting
default_settings = {
    Setting.SCREEN_SCALE: 3,
    Setting.SFX_VOLUME: 10,
    Setting.BGM_VOLUME: 0,
}


class Settings:
    def __init__(self):
        # Current values for all settings
        self.current_settings = self.load_settings_from_file()
        # Current changes to the settings
        self.unsaved_settings = self.current_settings.copy()

    def load_settings_from_file(self):
        try:
            settings_path = get_asset(AssetType.ATTRIBUTES, "settings.cfg")
            file_settings = {}

            with open(settings_path) as settings_file:
                lines = settings_file.read()
                for line in StringIO(lines):
                    values = line.split(' ')
                    if len(values) == 2:
                        file_settings[Setting[values[0]]] = int(values[1])
            return file_settings
        except (IOError, KeyError) as e:
            print("Unable to load settings file. Using defaults. Exception: {}".format(e))
            return default_settings.copy()

    def save_settings_to_file(self, settings):
        try:
            settings_path = get_asset(AssetType.ATTRIBUTES, "settings.cfg")

            with open(settings_path, 'w') as settings_file:
                for key, value in settings.items():
                    settings_file.write("{} {}\n".format(key.value, value))
        except IOError as e:
            print("Unable to save settings file. Exception: {}".format(e))

    # Return the actual value of the setting
    def get(self, setting):
        return self.current_settings[setting]

    # Return the unsaved value of the setting
    def get_unsaved(self, setting):
        return self.unsaved_settings[setting]

    # Lower the unsaved value of the setting
    def lower_setting(self, setting):
        self.set_setting(setting, self.unsaved_settings[setting] - setting_interval[setting])

    # Raise the unsaved value of the setting
    def raise_setting(self, setting):
        self.set_setting(setting, self.unsaved_settings[setting] + setting_interval[setting])

    # Set the unsaved value of the setting
    def set_setting(self, setting, new_value):
        self.unsaved_settings[setting] = clamp(new_value, setting_bounds[setting][0], setting_bounds[setting][1])

    # Save unsaved settings, making them the actual values
    def save_settings(self):
        for key, value in self.unsaved_settings.items():
            self.current_settings[key] = value

        for key, value in self.current_settings.items():
            self.unsaved_settings[key] = value

        self.save_settings_to_file(self.current_settings)

    # Reset unsaved settings back to what the current actual values are
    def reset_settings(self):
        for key, value in self.current_settings.items():
            self.unsaved_settings[key] = value


SETTINGS = Settings()
