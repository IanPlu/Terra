from terra.effects.animatedeffect import AnimatedEffect
from terra.effects.effecttype import EffectType
from terra.engine.gameobject import GameObject
from terra.event import is_event_type, E_PIECE_DEAD, E_ORDER_CANCELED, E_INVALID_MOVE_ORDERS, E_INVALID_BUILD_ORDERS
from terra.managers.managers import Managers
from terra.piece.piecetype import PieceType


# Manager for multiple effects objects. Handles creating and destroying special effects.
class EffectsManager(GameObject):
    def __init__(self):
        super().__init__()

        self.effects = []

    # Create an effect of the specified type.
    def create_effect(self, gx, gy, effect_type, team):
        self.effects.append(AnimatedEffect(self, effect_type, gx, gy, team))

    # Remove and delete the provided effect.
    def destroy_effect(self, effect):
        self.effects.remove(effect)

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_PIECE_DEAD):
            self.create_effect(event.gx, event.gy, EffectType.PIECE_DESTROYED, None)
        elif is_event_type(event, E_ORDER_CANCELED):
            self.create_effect(event.gx, event.gy, EffectType.ORDER_BLOCKED, None)
        elif is_event_type(event, E_INVALID_MOVE_ORDERS):
            for coordinate in event.invalid_coordinates:
                self.create_effect(coordinate[0], coordinate[1], EffectType.ALERT, event.team)
        elif is_event_type(event, E_INVALID_BUILD_ORDERS):
            base = Managers.piece_manager.get_all_pieces_for_team(event.team, piece_type=PieceType.BASE)[0]
            self.create_effect(base.gx, base.gy, EffectType.NO_MONEY, event.team)

        for effect in self.effects:
            effect.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for effect in self.effects:
            effect.render(game_screen, ui_screen)