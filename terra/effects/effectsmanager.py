from terra.engine.gameobject import GameObject
from terra.effects.effecttype import EffectType
from terra.effects.animatedeffect import AnimatedEffect


# Manager for multiple effects objects. Handles creating and destroying special effects.
class EffectsManager(GameObject):
    def __init__(self):
        super().__init__()

        self.effects = []

    def create_effect(self, gx=0, gy=0, effect_type=EffectType.ALERT):
        self.effects.append(AnimatedEffect(self, effect_type, gx, gy))

    def destroy_effect(self, effect):
        self.effects.remove(effect)

    def step(self, event):
        super().step(event)

        for effect in self.effects:
            effect.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for effect in self.effects:
            effect.render(game_screen, ui_screen)