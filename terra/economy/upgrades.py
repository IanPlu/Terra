import json

from terra.resources.assets import AssetType, get_asset
from terra.util.jsonutil import as_enum


# Read in the base piece attributes from the file '/resources/attributes/upgradeattributes.cfg'.
# File is expected to be in a JSON format.
def read_upgrade_attributes_from_file():
    try:
        attributes_path = get_asset(AssetType.ATTRIBUTES, "upgradeattributes.cfg")

        with open(attributes_path) as attributes_file:
            return json.loads(attributes_file.read().replace('\n', ''), object_hook=as_enum)
    except IOError as e:
        print("Unable to load upgrade attributes. Exception: {}".format(e))
        return None


# All upgrades available for purchase, including prereqs, price, effect, etc.
#   - new_stat: Adds the new stat to the existing stat. Allows for stacking buffs.
#   - new_type: Overwrites the attribute with the provided new attribute. Allows for mutating types.
#   - new_attack_multiplier: Sets the attack multiplier vs. the specified unit to the new value.
#   - new_buildable: Adds the provided piece(s) to the buildable list for the specified piece.
base_upgrades = read_upgrade_attributes_from_file()
