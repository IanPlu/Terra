import sys
from enum import Enum
from os import path


# External assets are divided into subdirectories by their type
class AssetType(Enum):
    SPRITE = "resources/sprites/"
    SOUND = "resources/sfx/"
    MAP = "resources/maps/"
    SAVE = "resources/saves"
    ATTRIBUTES = "resources/attributes/"
    LOG = "logs/"


# Resources might be located somewhere strange depending on how the application is packaged.
# Locate the directory we ask for regardless of whether we're an executable or not.
def get_base_path(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen / packaged into an executable
        datadir = path.dirname(sys.executable)
    else:
        # The application is not frozen (debugging or otherwise not packaged)
        datadir = path.dirname(__file__)

    return path.join(datadir, filename)


# Return a properly formatted path to the specified resource
def get_asset(asset_type, resource_name):
    return get_base_path(path.abspath(path.join(asset_type.value, resource_name)))