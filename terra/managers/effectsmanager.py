from terra.effects.animatedeffect import AnimatedEffect
from terra.effects.effecttype import EffectType
from terra.effects.turnbanner import TurnBanner
from terra.engine.gameobject import GameObject
from terra.event.event import EventType

event_type_to_effect = {
    EventType.E_PIECE_DEAD: EffectType.PIECE_DESTROYED,
    EventType.E_ORDER_CANCELED: EffectType.ORDER_BLOCKED,
    EventType.E_ARMOR_GRANTED: EffectType.ARMOR_GRANTED,
    EventType.E_PIECE_HEALED: EffectType.HP_HEALED,
    EventType.E_PIECE_ON_INVALID_TERRAIN: EffectType.ALERT,
    EventType.E_TILE_TERRAFORMED: EffectType.PIECE_DESTROYED,
    EventType.E_INVALID_BUILD_ORDERS: EffectType.NO_MONEY,
    EventType.E_INVALID_UPGRADE_ORDERS: EffectType.DUPLICATE_UPGRADE,
}


# Manager for multiple effects objects. Handles creating and destroying special effects.
class EffectsManager(GameObject):
    def __init__(self):
        super().__init__()

        self.effects = []

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        for event_type, effect in event_type_to_effect.items():
            event_bus.register_handler(event_type, self.create_piece_effect_from_event)

        event_bus.register_handler(EventType.START_PHASE_START_TURN, self.create_turn_banner)
        event_bus.register_handler(EventType.E_INVALID_MOVE_ORDERS, self.create_invalid_coordinate_effects)

    # Create an effect of the specified type.
    def create_effect(self, gx, gy, effect_type, team):
        self.effects.append(AnimatedEffect(self, effect_type, gx, gy, team))

    # Remove and delete the provided effect.
    def destroy_effect(self, effect):
        self.effects.remove(effect)

    # Create an effect from a notification event.
    def create_piece_effect_from_event(self, event):
        if hasattr(event, 'affected_pieces'):
            for piece in event.affected_pieces:
                self.create_effect(piece.gx, piece.gy, event_type_to_effect[event.event_type], event.team)
        else:
            self.create_effect(event.gx, event.gy, event_type_to_effect[event.event_type], None)

    def create_turn_banner(self, event):
        self.effects.append(TurnBanner(self, event.turn_number))

    def create_invalid_coordinate_effects(self, event):
        for coordinate in event.invalid_coordinates:
            self.create_effect(coordinate[0], coordinate[1], EffectType.ALERT, event.team)

    def step(self, event):
        super().step(event)

        for effect in self.effects:
            effect.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for effect in self.effects:
            effect.render(game_screen, ui_screen)
