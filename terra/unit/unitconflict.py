from terra.event import *


# Manager for rounds of conflict between two units.
class UnitConflict:
    def __init__(self, red_unit, blue_unit):
        super().__init__()

        self.red_unit = red_unit
        self.blue_unit = blue_unit

    # Conduct one round of combat
    def resolve(self):
        print("Units in conflict: {}, {}".format(self.red_unit, self.blue_unit))
        publish_game_event(E_UNITS_IN_CONFLICT, {
            'gx': self.red_unit.gx,
            'gy': self.blue_unit.gy
        })

        self.red_unit.hp -= self.blue_unit.attack
        self.blue_unit.hp -= self.red_unit.attack
