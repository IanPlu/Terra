from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgradetype import UpgradeType

# Whitelist of enums that this util method is able to convert to
KNOWN_ENUMS = {
    'PieceType': PieceType,
    'Attribute': Attribute,
    'PieceSubtype': PieceSubtype,
    'PieceArchetype': PieceArchetype,
    'DamageType': DamageType,
    'MovementType': MovementType,
    'UpgradeAttribute': UpgradeAttribute,
    'UpgradeType': UpgradeType,
}


# Handler for decoding enums from JSON into their proper classes. Supports keys being enums.
def as_enum(d):
    new_dict = {}

    # Return the provided string parsed to a known enum if its prefix matches known enums.
    # Otherwise return the provided string.
    def parse_enum(obj):
        if isinstance(obj, str):
            split_str = obj.split(".")
            if split_str[0] in KNOWN_ENUMS.keys():
                return getattr(KNOWN_ENUMS[split_str[0]], split_str[1])
            else:
                return obj
        elif isinstance(obj, list):
            # Parse each element in the list
            return [parse_enum(element) for element in obj]
        else:
            return obj

    # Parse each key and value into an enum if necessary
    for key, value in d.items():
        new_dict[parse_enum(key)] = parse_enum(value)

    return new_dict
