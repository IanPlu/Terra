from terra.piece.unit.unit import *


# A Ranger unit.
# Rangers are light units capable of a short ranged attack. They have no combat strength in melee.
# Cheap and relatively weak.
class Ranger(Unit):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)
        self.unit_type = UnitType.RANGER

        self.max_hp = 10
        self.damage_type = DamageType.RANGED
        self.min_range = 1
        self.max_range = 2
        self.movement_type = MovementType.GROUND
        self.movement_range = 2

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
