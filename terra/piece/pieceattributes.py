import json

from terra.resources.assets import AssetType, get_asset
from terra.util.jsonutil import as_enum


# Read in the base piece attributes from the file '/resources/attributes/pieceattributes.cfg'.
# File is expected to be in a JSON format.
def read_piece_attributes_from_file():
    try:
        attributes_path = get_asset(AssetType.ATTRIBUTES, "pieceattributes.cfg")

        with open(attributes_path) as attributes_file:
            return json.loads(attributes_file.read().replace('\n', ''), object_hook=as_enum)
    except IOError as e:
        print("Unable to load piece attributes. Exception: {}".format(e))
        return None


# Base table of attributes for all units.
# Contains data on movement type, attack damage, abilities, etc.
base_piece_attributes = read_piece_attributes_from_file()
