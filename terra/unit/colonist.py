from terra.unit.unit import *
from terra.resources.assets import spr_unit_colonist


# A Colonist unit.
# Colonists have limited combat capabilities and are mainly for building and gathering resources.
class Colonist(Unit):
    def __init__(self, army, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(army, battle, game_map, team, gx, gy)

        self.max_hp = 5
        self.attack = 0
        self.ranged_attack = 0
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GROUND
        self.movement_range = 3
        self.sprite = spr_unit_colonist

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
