import itertools
import unittest
from math import ceil

from terra.piece.attribute import Attribute
from terra.piece.piece import Piece
from terra.piece.pieceattributes import base_piece_attributes
from terra.piece.piececonflict import dmg_formula
from terra.piece.piecetype import PieceType

piece_strings = {
    PieceType.COLONIST:     "[COLONIST]",
    PieceType.TROOPER:      "[TROOPER ]",
    PieceType.RANGER:       "[RANGER  ]",
    PieceType.GHOST:        "[GHOST   ]",

    PieceType.GUARDIAN:     "[GUARDIAN]",
    PieceType.BOLTCASTER:   "[BOLTCAST]",
    PieceType.BANSHEE:      "[BANSHEE ]",

    PieceType.TITAN:        "[TITAN   ]",
    PieceType.EARTHRENDER:  "[EARTHREN]",
    PieceType.DEMON:      "[DEMON   ]",

    PieceType.BASE:         "[BASE    ]",
    PieceType.GENERATOR:    "[GENERATO]",
    PieceType.BARRACKS:     "[BARRACKS]",
    PieceType.TOWER:        "[TOWER   ]",
    PieceType.TECHLAB:      "[TECHLAB ]",
}


excluded_types = [PieceType.DEFAULT]
# types_to_test = [member for member in PieceType if member not in excluded_types]
types_to_test = [PieceType.TROOPER, PieceType.RANGER, PieceType.GHOST, PieceType.COLONIST, PieceType.BASE, PieceType.GENERATOR]


class MockPiece:
    def __init__(self, piece_type, entrenchment=0, temporary_armor=0):
        self.piece_type = piece_type
        self.piece_subtype = self.attr(Attribute.SUBTYPE)
        self.piece_archetype = self.attr(Attribute.ARCHETYPE)
        self.hp = self.attr(Attribute.MAX_HP)

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
        # Generate combinations of pieces
        itertools.combinations(types_to_test, 2)

        template = "|{} vs {} |  {: >3d}  |  {: >3d}  |  {}  |  {}  |\n"

        output = "_________________________________________________________\n" \
                 "|[piece 1 ] vs [piece 2 ] |  dmg  |  dmg  | ttk  | ttk  |\n"
        for piece1, piece2 in itertools.combinations(types_to_test, 2):
            p1 = MockPiece(piece1)
            p2 = MockPiece(piece2)

            # Calculate damage done
            attack1 = p1.get_attack_rating(p2)
            attack2 = p2.get_attack_rating(p1)

            defense1 = p1.get_defense_rating()
            defense2 = p2.get_defense_rating()

            dmg1 = dmg_formula(attack1, defense2)
            dmg2 = dmg_formula(attack2, defense1)

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
