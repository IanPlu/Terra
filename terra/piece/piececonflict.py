from terra.event import publish_game_event, E_PIECES_IN_CONFLICT
from terra.piece.damagetype import DamageType
from terra.piece.pieceattributes import Attribute
from terra.managers.managers import Managers


# Manager for rounds of melee direct conflict between two pieces.
class PieceConflict:
    def __init__(self, piece1, piece2):
        super().__init__()

        self.piece1 = piece1
        self.piece2 = piece2

        Managers.combat_logger.log_contesting_pieces(piece1, piece2)

    # Get the attack rating for this piece.
    def get_attack_damage(self, piece1, piece2):
        if Managers.team_manager.attr(piece1.team, piece1.piece_type, Attribute.DAMAGE_TYPE) == DamageType.MELEE:
            return piece1.get_attack_rating(piece2)
        else:
            # This piece can't fight back in this conflict
            return 0

    # Get any defense bonuses this piece may have. Defense bonuses apply a 10% damage reduction per.
    def get_defense_bonuses(self, piece1, piece2):
        return piece1.get_defense_rating()

    # Conduct one round of combat
    def resolve(self):
        publish_game_event(E_PIECES_IN_CONFLICT, {
            'gx': self.piece1.gx,
            'gy': self.piece1.gy
        })

        # Get the first piece's attack value against the second
        first_piece_attack = self.get_attack_damage(self.piece1, self.piece2)
        # Get defense bonuses the first piece has
        first_piece_defense = self.get_defense_bonuses(self.piece1, self.piece2)

        # Get the second piece's attack value against the first
        second_piece_attack = self.get_attack_damage(self.piece2, self.piece1)
        # Get defense bonuses the second piece has
        second_piece_defense = self.get_defense_bonuses(self.piece2, self.piece1)

        # Determine health loss per piece
        piece1_damage_taken = int(second_piece_attack * (1 - first_piece_defense / 10))
        piece2_damage_taken = int(first_piece_attack * (1 - second_piece_defense / 10))

        self.piece1.damage_hp(piece1_damage_taken, self.piece2)
        self.piece2.damage_hp(piece2_damage_taken, self.piece1)
