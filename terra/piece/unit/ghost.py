from terra.piece.unit.unit import *


# A Ghost unit.
# Ghosts are basic harassment and mobility units.
# Cheap and relatively weak. Strong against ranged units and not impeded by enemy units when moving.
class Ghost(Unit):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__(piece_manager, team_manager, battle, game_map, team, gx, gy)
        self.unit_type = UnitType.GHOST

        self.max_hp = 10
        self.attack = 1
        self.ranged_attack = 0
        self.min_range = 0
        self.max_range = 0
        self.movement_type = MovementType.GHOST
        self.movement_range = 3

    def step(self, event):
        super().step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
