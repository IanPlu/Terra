from terra.constants import GRID_WIDTH, GRID_HEIGHT, TICK_RATE
from terra.engine.animatedgameobject import AnimatedGameObject
from terra.managers.session import Manager
from terra.resources.assets import spr_effects


# An animated special effect / particle. Renders its animation once and then expires.
class AnimatedEffect(AnimatedGameObject):
    def __init__(self, parent, effect_type, gx, gy, team=None):
        self.parent = parent
        self.effect_type = effect_type
        self.gx = gx
        self.gy = gy
        self.team = team
        self.is_alive = True

        super().__init__(spr_effects[self.effect_type], 24, TICK_RATE / 8)

    # Handler for what to do when the animation loops.
    # By default, effects destroy themselves on loop.
    def on_animation_reset(self):
        super().on_animation_reset()

        # Give the signal to destroy ourselves
        self.is_alive = False
        self.parent.destroy_effect(self)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.is_alive and (self.get_manager(Manager.PLAYER).active_team == self.team or not self.team):
            game_screen.blit(self.sprite, (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

