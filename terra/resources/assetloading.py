from enum import Enum
from pathlib import Path
from definitions import ROOT_DIR


# External assets are divided into subdirectories by their type
class AssetType(Enum):
    SPRITE = "resources/sprites/"
    SOUND = "resources/sfx/"
    MAP = "resources/maps/"
    SAVE = "resources/saves"
    ATTRIBUTES = "resources/attributes/"
    LOG = "logs/"
    FONT = "resources/fonts/"


# Return a properly formatted path to the specified resource
def get_asset(asset_type, resource_name=None):
    if resource_name:
        return str(Path(ROOT_DIR, asset_type.value, resource_name))
    else:
        return str(Path(ROOT_DIR, asset_type.value))
