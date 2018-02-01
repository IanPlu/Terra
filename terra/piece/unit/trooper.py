from terra.piece.unit.unit import *


# A Trooper unit.
# Troopers are general purpose close-range combat units.
# Cheap and relatively weak.
class Trooper(Unit):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0, hp=None):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy, hp)
        self.unit_type = UnitType.TROOPER

        self.max_hp = 10
        self.damage_type = DamageType.MELEE
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GROUND
        self.movement_range = 2

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
