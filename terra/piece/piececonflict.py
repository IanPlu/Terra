from terra.event.event import publish_game_event, EventType
from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType


# Manager for rounds of melee direct conflict between two pieces.
class PieceConflict:
    def __init__(self, pieces):
        super().__init__()

        self.pieces = pieces

    # Get the attack rating for this piece.
    # Note that attack damage is divided by the number of enemies in this conflict
    def get_attack_damage(self, piece1, piece2):
        num_enemies = len(self.pieces) - 1

        if piece1.attr(Attribute.DAMAGE_TYPE) == DamageType.MELEE:
            return piece1.get_attack_rating(piece2) / num_enemies
        else:
            # This piece can't fight back in this conflict
            return 0

    # Get any defense bonuses this piece may have. Defense bonuses apply a 10% damage reduction per.
    def get_defense_bonuses(self, piece1, piece2):
        return piece1.get_defense_rating()

    def attack(self, piece1, piece2):
        attack = self.get_attack_damage(piece1, piece2)
        defense = self.get_defense_bonuses(piece2, piece1)

        return int(attack * (1 - defense / 10))

    # Conduct one round of combat
    def resolve(self):
        publish_game_event(EventType.E_PIECES_IN_CONFLICT, {
            'gx': self.pieces[0].gx,
            'gy': self.pieces[0].gy,
            'teams': [piece.team for piece in self.pieces]
        })

        # Have each piece fight!
        for piece in self.pieces:
            enemy_pieces = self.pieces.copy()
            enemy_pieces.remove(piece)

            for enemy in enemy_pieces:
                piece_attack = self.attack(piece, enemy)
                enemy_attack = self.attack(enemy, piece)

                piece.damage_hp(enemy_attack, enemy)
                enemy.damage_hp(piece_attack, piece)

                if piece_attack > 0:
                    piece.on_damaging_enemy(piece_attack, enemy)
                if enemy_attack > 0:
                    enemy.on_damaging_enemy(enemy_attack, piece)
