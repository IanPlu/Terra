from terra.event import *


# Manager for rounds of conflict between two units.
class PieceConflict:
    def __init__(self, red_unit, blue_unit):
        super().__init__()

        # TODO: Make more generic
        self.red_unit = red_unit
        self.blue_unit = blue_unit

    # Conduct one round of combat
    def resolve(self):
        publish_game_event(E_PIECES_IN_CONFLICT, {
            'gx': self.red_unit.gx,
            'gy': self.red_unit.gy
        })

        self.red_unit.hp -= self.blue_unit.attack
        self.blue_unit.hp -= self.red_unit.attack
