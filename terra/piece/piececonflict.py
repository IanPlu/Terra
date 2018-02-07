from terra.event import publish_game_event, E_PIECES_IN_CONFLICT
from terra.piece.damagetype import DamageType
from terra.piece.pieceattributes import Attribute


# Manager for rounds of melee direct conflict between two pieces.
class PieceConflict:
    def __init__(self, piece1, piece2, team_manager):
        super().__init__()

        self.piece1 = piece1
        self.piece2 = piece2
        self.team_manager = team_manager

    # Get the attack rating for this piece
    def get_attack_damage(self, piece1, piece2):
        if self.team_manager.attr(piece1.team, piece1.piece_type, Attribute.DAMAGE_TYPE) == DamageType.MELEE:
            attack = self.team_manager.attr(piece1.team, piece1.piece_type, Attribute.ATTACK)
            multiplier = self.team_manager.attr(piece1.team, piece1.piece_type, Attribute.ATTACK_MULTIPLIER)[piece2.piece_type]

            return attack * multiplier
        else:
            # This piece can't fight back in this conflict
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
