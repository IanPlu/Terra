from terra.piece.unit.unit import *
from terra.resources.assets import spr_unit_trooper


# A Trooper unit.
# Troopers are general purpose close-range combat units.
# Cheap and relatively weak.
class Trooper(Unit):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)

        self.max_hp = 10
        self.attack = 1
        self.ranged_attack = 0
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GROUND
        self.movement_range = 2
        self.sprite = spr_unit_trooper

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
