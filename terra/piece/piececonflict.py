from terra.event import *
from terra.piece.unit.damagetype import DamageType
from terra.piece.unit.piecedamage import piece_damage
from terra.piece.unit.unittype import UnitType


# Manager for rounds of melee direct conflict between two pieces.
class PieceConflict:
    def __init__(self, piece1, piece2):
        super().__init__()

        self.piece1 = piece1
        self.piece2 = piece2

    def get_piece_type(self, piece):
        if hasattr(piece, 'unit_type'):
            return piece.unit_type
        elif hasattr(piece, 'building_type'):
            return piece.building_type
        else:
            return None

    # Get the attack rating for this unit
    def get_attack_damage(self, piece1, piece2):
        piece1_type = self.get_piece_type(piece1)
        piece2_type = self.get_piece_type(piece2)

        if piece1_type in UnitType:
            if piece1.damage_type == DamageType.MELEE:
                return piece_damage[piece1.team][piece1_type][piece2_type]
            else:
                # Ranged units can't deal melee damage
                return 0
        else:
            # Buildings deal no damage to their assailants
            return 0

    # Conduct one round of combat
    def resolve(self):
        publish_game_event(E_PIECES_IN_CONFLICT, {
            'gx': self.piece1.gx,
            'gy': self.piece1.gy
        })

        # Get the first piece's attack value against the second
        first_piece_attack = self.get_attack_damage(self.piece1, self.piece2)

        # Get the second piece's attack value against the first
        second_piece_attack = self.get_attack_damage(self.piece2, self.piece1)

        self.piece1.hp -= second_piece_attack
        self.piece2.hp -= first_piece_attack
