from terra.unit.unit import *
from terra.resources.assets import spr_unit_ranger


# A Ranger unit.
# Rangers are light units capable of a short ranged attack. They have no combat strength in melee.
# Cheap and relatively weak.
class Ranger(Unit):
    def __init__(self, army, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(army, battle, game_map, team, gx, gy)

        self.max_hp = 10
        self.attack = 0
        self.ranged_attack = 1
        self.min_range = 1
        self.max_range = 2
        self.movement_type = MovementType.GROUND
        self.movement_range = 2
        self.sprite = spr_unit_ranger

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
