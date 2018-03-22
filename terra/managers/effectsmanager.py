from terra.effects.animatedeffect import AnimatedEffect
from terra.effects.effecttype import EffectType
from terra.engine.gameobject import GameObject
from terra.event import is_event_type, E_PIECE_DEAD, E_ORDER_CANCELED, E_INVALID_MOVE_ORDERS, E_INVALID_BUILD_ORDERS, \
    E_ARMOR_GRANTED, E_PIECE_HEALED, E_INVALID_UPGRADE_ORDERS, E_PIECE_ON_INVALID_TERRAIN, E_TILE_TERRAFORMED, \
    START_PHASE_START_TURN
from terra.managers.managers import Managers
from terra.piece.orders import BuildOrder, UpgradeOrder
from terra.effects.turnbanner import TurnBanner


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
            pieces_with_build_orders = [piece for piece in Managers.piece_manager.get_all_pieces_for_team(event.team)
                                        if isinstance(piece.current_order, (BuildOrder, UpgradeOrder))]
            for piece in pieces_with_build_orders:
                self.create_effect(piece.gx, piece.gy, EffectType.NO_MONEY, event.team)
        elif is_event_type(event, E_INVALID_UPGRADE_ORDERS):
            pieces_with_upgrade_orders = [piece for piece in Managers.piece_manager.get_all_pieces_for_team(event.team)
                                          if isinstance(piece.current_order, UpgradeOrder) and
                                          piece.current_order.new_upgrade_type in event.duplicate_upgrades]
            for piece in pieces_with_upgrade_orders:
                self.create_effect(piece.gx, piece.gy, EffectType.DUPLICATE_UPGRADE, event.team)
        elif is_event_type(event, E_ARMOR_GRANTED):
            self.create_effect(event.gx, event.gy, EffectType.ARMOR_GRANTED, None)
        elif is_event_type(event, E_PIECE_HEALED):
            self.create_effect(event.gx, event.gy, EffectType.HP_HEALED, None)
        elif is_event_type(event, E_PIECE_ON_INVALID_TERRAIN):
            self.create_effect(event.gx, event.gy, EffectType.ALERT, None)
        elif is_event_type(event, E_TILE_TERRAFORMED):
            self.create_effect(event.gx, event.gy, EffectType.PIECE_DESTROYED, None)
        elif is_event_type(event, START_PHASE_START_TURN):
            self.effects.append(TurnBanner(self, event.turn_number))

        for effect in self.effects:
            effect.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        for effect in self.effects:
            effect.render(game_screen, ui_screen)
