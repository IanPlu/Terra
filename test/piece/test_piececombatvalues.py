import itertools
import unittest
from unittest.mock import Mock
from math import ceil

from terra.managers.managers import Managers
from terra.piece.attribute import Attribute
from terra.piece.piece import Piece
from terra.piece.pieceattributes import base_piece_attributes
from terra.piece.piececonflict import PieceConflict
from terra.piece.piecetype import PieceType

piece_strings = {
    PieceType.COLONIST:     "[COLONIST]",
    PieceType.TROOPER:      "[TROOPER ]",
    PieceType.RANGER:       "[RANGER  ]",
    PieceType.GHOST:        "[GHOST   ]",

    PieceType.GUARDIAN:     "[GUARDIAN]",
    PieceType.BOLTCASTER:   "[BOLTCAST]",
    PieceType.BANSHEE:      "[BANSHEE ]",

    PieceType.BASE:         "[BASE    ]",
    PieceType.GENERATOR:    "[GENERATO]",
    PieceType.BARRACKS:     "[BARRACKS]",
    PieceType.TOWER:        "[TOWER   ]",
    PieceType.TECHLAB:      "[TECHLAB ]",
}



class MockPiece:
    def __init__(self, piece_type, entrenchment=0, temporary_armor=0):
        self.piece_type = piece_type
        self.piece_subtype = self.attr(Attribute.SUBTYPE)
        self.piece_archetype = self.attr(Attribute.ARCHETYPE)

        self.entrenchment = entrenchment
        self.temporary_armor = temporary_armor

    def attr(self, attribute):
        return base_piece_attributes[self.piece_type].get(attribute, base_piece_attributes[PieceType.DEFAULT][attribute])

    def get_attack_rating(self, target):
        return Piece.get_attack_rating(self, target)

    def get_defense_rating(self):
        return Piece.get_defense_rating(self)


# Generate a table of each piece's combat data against other pieces.
# e.x. generate data about Troopers fighting in direct combat, including damage dealt each round, time to kill, etc.
class CombatValuesTest(unittest.TestCase):
    def calculate_time_to_kill(self, damage, max_hp):
        if damage > 0:
            return "{: >2d}".format(ceil(max_hp / damage))
        else:
            return "  "

    def test_combat_values(self):
        # Mock out the combat logger
        Managers.combat_logger = Mock()

        # Generate combinations of pieces
        input = [member for member in PieceType if member is not PieceType.DEFAULT]
        itertools.combinations(input, 2)

        template = "|{} vs {} |  {: >3d}  |  {: >3d}  |  {}  |  {}  |\n"

        output = "_________________________________________________________\n" \
                 "|[piece 1 ] vs [piece 2 ] |  dmg  |  dmg  | ttk  | ttk  |\n"
        for piece1, piece2 in itertools.combinations(input, 2):
            p1 = MockPiece(piece1)
            p2 = MockPiece(piece2)

            conflict = PieceConflict([p1, p2])

            # Calculate damage done
            dmg1 = conflict.attack(p1, p2)
            dmg2 = conflict.attack(p2, p1)

            # Calculate number of round of combat it'd take to kill the other piece
            ttk1 = self.calculate_time_to_kill(dmg1, p2.attr(Attribute.MAX_HP))
            ttk2 = self.calculate_time_to_kill(dmg2, p1.attr(Attribute.MAX_HP))

            output += template.format(piece_strings[piece1],
                                      piece_strings[piece2],
                                      dmg1,
                                      dmg2,
                                      ttk1,
                                      ttk2)

        output += "---------------------------------------------------------\n"

        print(output)
