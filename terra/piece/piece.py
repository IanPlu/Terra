from terra.battlephase import BattlePhase
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.engine.animatedgameobject import AnimatedGameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.managers import Managers
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType, MovementAttribute, movement_types
from terra.piece.orders import MoveOrder, RangedAttackOrder, BuildOrder, UpgradeOrder, TerraformOrder, DemolishOrder
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, spr_order_flags, clear_color, spr_upgrade_icons, \
    spr_target, light_team_color, spr_digit_icons, spr_resource_icon_small
from terra.strings import piece_name_strings, LANGUAGE
from terra.team import Team
from terra.util.drawingutil import draw_small_resource_count


# Base object in play belonging to a player, like a unit or a building.
# They belong to a team and exist somewhere on the map.
# Pieces have HP and can accept and execute orders.
class Piece(AnimatedGameObject):
    def __init__(self, piece_type=PieceType.COLONIST, team=Team.RED, gx=0, gy=0, hp=None):
        self.team = team
        self.gx = gx
        self.gy = gy

        # Look up values based on our piece type
        self.piece_type = piece_type
        self.piece_subtype = self.attr(Attribute.SUBTYPE)
        self.piece_archetype = self.attr(Attribute.ARCHETYPE)

        # Interpreted variables. Don't touch!
        if hp:
            self.hp = hp
        else:
            self.hp = self.attr(Attribute.MAX_HP)
        self.current_order = None
        self.in_conflict = False
        self.entrenchment = 0

        self.temporary_armor = 0
        self.last_attacker = None
        self.temporary_aoe_on_death = 0
        self.temporary_money_lost_on_death = 0

        self.previewing_order = False

        super().__init__(spr_pieces[self.team][self.piece_type], 24, 2, indexed=False, use_global_animation_frame=True)

    def __str__(self):
        return "{} {} at tile ({}, {}) with {} HP" \
            .format(self.team.name, piece_name_strings[LANGUAGE][self.piece_type], self.gx, self.gy, self.hp)

    # Return an attribute about this piece.
    def attr(self, attribute):
        return Managers.team_manager.attr(self.team, self.piece_type, attribute)

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_BUILD, self.handle_phase_build)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_MOVE, self.handle_phase_move)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_COMBAT, self.handle_phase_combat)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_RANGED, self.handle_phase_ranged)
        event_bus.register_handler(EventType.START_PHASE_EXECUTE_SPECIAL, self.handle_phase_special)

        event_bus.register_handler(EventType.END_PHASE_MOVE, self.handle_end_phase_move)

        event_bus.register_handler(EventType.START_PHASE_ORDERS, self.handle_phase_orders)
        event_bus.register_handler(EventType.START_PHASE_START_TURN, self.handle_phase_start_turn)
        event_bus.register_handler(EventType.E_CLEANUP, self.cleanup)

        event_bus.register_handler(EventType.E_SELECT, self.select)
        event_bus.register_handler(EventType.E_CLOSE_MENU, self.close_menu)
        event_bus.register_handler(EventType.E_SELECT_TILE, self.tile_selected)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.start_previewing_orders)
        input_handler.register_handler(InputAction.RELEASE, Key.MENU2, self.stop_previewing_orders)

    def is_accepting_events(self):
        return Managers.current_mode == Mode.BATTLE

    # Return a list of actions to show in the selection UI.
    def get_available_actions(self):
        actions = []

        if self.get_movement_range() > 0:
            actions.append(Option.MENU_MOVE)
        if self.attr(Attribute.DAMAGE_TYPE) == DamageType.RANGED:
            actions.append(Option.MENU_RANGED_ATTACK)
        if len(self.get_valid_buildable_pieces()):
            actions.append(Option.MENU_BUILD_PIECE)
        if len(self.get_valid_purchaseable_upgrades()):
            actions.append(Option.MENU_PURCHASE_UPGRADE)
        if len(self.get_valid_tiles_for_terraforming(raising=True)):
            actions.append(Option.MENU_RAISE_TILE)
        if len(self.get_valid_tiles_for_terraforming(raising=False)):
            actions.append(Option.MENU_LOWER_TILE)
        if self.piece_subtype == PieceSubtype.BUILDING and self.piece_type is not PieceType.BASE:
            actions.append(Option.MENU_DEMOLISH_SELF)

        if len(actions) > 0 and self.current_order:
            actions.append(Option.MENU_CANCEL_ORDER)

        return actions

    # Trim the list of innately buildable pieces to ones that can be placed nearby, taking tile type etc. into account
    def get_valid_buildable_pieces(self):
        valid_pieces = []

        tiles_to_check = [(self.gx + 1, self.gy),
                          (self.gx - 1, self.gy),
                          (self.gx, self.gy + 1),
                          (self.gx, self.gy - 1)]
        unoccupied_tiles = []

        # Remove tiles that already have allies on it that can't move
        for tile_x, tile_y in tiles_to_check:
            immobile_allies = []
            for piece in Managers.piece_manager.get_pieces_at(tile_x, tile_y, team=self.team):
                if piece.attr(Attribute.MOVEMENT_RANGE) <= 0:
                    immobile_allies.append(piece)

            if len(immobile_allies) <= 0:
                unoccupied_tiles.append((tile_x, tile_y))

        # For each buildable piece, if there exists at least one valid adjacent tile for its movement type that we can
        # place it onto, add it to the list
        for piece in self.attr(Attribute.BUILDABLE_PIECES):
            valid_tile_types = movement_types[Managers.team_manager.attr(self.team, piece, Attribute.MOVEMENT_TYPE)][MovementAttribute.PASSABLE]
            unoccupied_tile_types = set([Managers.battle_map.get_tile_type_at(coord[0], coord[1]) for coord in unoccupied_tiles])

            if not unoccupied_tile_types.isdisjoint(valid_tile_types):
                valid_pieces.append(piece)

        return valid_pieces

    # Get the list of upgrades that can be purchased by this piece
    def get_valid_purchaseable_upgrades(self):
        return self.attr(Attribute.PURCHASEABLE_UPGRADES)

    # Return a list of adjacent tiles that can be traversed by this movement type
    def get_valid_tiles_for_terraforming(self, raising=True):
        if self.attr(Attribute.TERRAFORMING):
            return Managers.battle_map.get_valid_adjacent_tiles_for_movement_type(
                self.gx, self.gy, MovementType.RAISE if raising else MovementType.LOWER)
        else:
            return []

    # Return this piece's attack strength against a target
    def get_attack_rating(self, target):
        attack = self.attr(Attribute.ATTACK)
        multiplier = self.attr(Attribute.ATTACK_MULTIPLIER)[target.piece_archetype]

        return attack * multiplier

    # Return the combination of any innate armor, entrenchment bonuses, etc. this piece has
    def get_defense_rating(self):
        return self.entrenchment + \
               self.attr(Attribute.ARMOR) + \
               self.temporary_armor

    # Get movement range, plus any bonuses
    def get_movement_range(self):
        movement_range = self.attr(Attribute.MOVEMENT_RANGE)

        if self.attr(Attribute.KICKOFF):
            movement_range += len(Managers.piece_manager.get_adjacent_pieces(self.gx, self.gy, self.team))

        return movement_range

    # Clean ourselves up at the end of phases, die as appropriate
    def cleanup(self, event):
        if self.hp <= 0:
            self.on_death()
        else:
            self.last_attacker = None
            self.temporary_armor = 0
            self.temporary_aoe_on_death = 0
            self.temporary_money_lost_on_death = 0

    # Do anything special on death
    def on_death(self):
        publish_game_event(EventType.E_PIECE_DEAD, {
            'gx': self.gx,
            'gy': self.gy,
            'team': self.team
        })

        # Bases being destroyed ends the game
        if self.piece_type == PieceType.BASE:
            publish_game_event(EventType.E_BASE_DESTROYED, {
                'team': self.team
            })

        if self.last_attacker:
            # TODO: Add effects for these special cases
            # Explode if we've been hit by a temporary AoE debuff
            if self.temporary_aoe_on_death > 0:
                for ally in Managers.piece_manager.get_adjacent_pieces(self.gx, self.gy, self.team):
                    ally.damage_hp(self.temporary_aoe_on_death, self.last_attacker)

            # Drain resources when killed if we've been hit by the steal debuff
            if self.temporary_money_lost_on_death > 0:
                Managers.team_manager.deduct_resources(self.team, self.temporary_money_lost_on_death)
                Managers.team_manager.add_resources(self.last_attacker.team, self.temporary_money_lost_on_death)

    # Cancel our current order, usually if we're contested.
    def abort_order(self):
        publish_game_event(EventType.E_ORDER_CANCELED, {
            'gx': self.gx,
            'gy': self.gy,
            'team': self.team
        })

        Managers.combat_logger.log_failed_order_execution(self, self.current_order)

        # Abort the order
        self.current_order = None

    # Return true if this piece is contested by an enemy piece occupying the same tile.
    # Caveats: the enemy might not be able to contest us, or can't be contested
    def is_contested(self):
        if self.attr(Attribute.IGNORE_CONTESTING):
            return False
        else:
            enemy_pieces = Managers.piece_manager.get_enemy_pieces_at(self.gx, self.gy, self.team)
            contesting_pieces = []
            for piece in enemy_pieces:
                # Cannot contest if the enemy can't attack a building (and we're a building) or it has no melee attack
                if piece.attr(Attribute.ATTACK) > 0 and \
                        piece.attr(Attribute.DAMAGE_TYPE) == DamageType.MELEE and not \
                        (piece.attr(Attribute.CANT_ATTACK_BUILDINGS) and self.piece_subtype is PieceSubtype.BUILDING):
                    contesting_pieces.append(piece)

            return len(contesting_pieces) > 0

    # Deal damage to this piece
    def damage_hp(self, damage, source=None):
        self.hp -= damage

        # Add any additional effects or debuffs from the source
        if source and isinstance(source, Piece):
            self.last_attacker = source

            aoe_on_death_gained = source.attr(Attribute.AOE_ON_KILL)
            if aoe_on_death_gained > 0:
                self.temporary_aoe_on_death = aoe_on_death_gained

            money_lost_on_death_gained = source.attr(Attribute.STEAL)
            if money_lost_on_death_gained > 0:
                self.temporary_money_lost_on_death = money_lost_on_death_gained

        Managers.combat_logger.log_damage(self, damage, source)

    # Heal this piece for the specified amount
    def heal_hp(self, heal):
        max_hp = self.attr(Attribute.MAX_HP)
        if self.hp < max_hp:
            self.hp = min(self.hp + heal, max_hp)
            publish_game_event(EventType.E_PIECE_HEALED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })
            Managers.combat_logger.log_healing(self, heal)

    # Apply an entrenchment bonus per unused movement range (up to 2)
    def apply_entrenchment(self, distance):
        self.entrenchment = (min(self.attr(Attribute.MOVEMENT_RANGE), 2) - distance) * \
                            self.attr(Attribute.ENTRENCHMENT_MODIFIER)

    # Phase handlers. Other than the orders handler, these are only triggered when we have orders.
    def handle_phase_start_turn(self, event):
        # Produce resources
        if self.attr(Attribute.RESOURCE_PRODUCTION) > 0:
            Managers.team_manager.add_resources(self.team, self.attr(Attribute.RESOURCE_PRODUCTION))

        # Regen health
        regen = self.attr(Attribute.REGEN)
        if regen > 0:
            self.heal_hp(regen)

        # Apply medic healing to adjacent allies
        medic = self.attr(Attribute.MEDIC)
        if medic > 0:
            adjacent_allies = Managers.piece_manager.get_adjacent_pieces(self.gx, self.gy, self.team)
            for ally in adjacent_allies:
                ally.heal_hp(medic)

        # Apply aura damage to adjacent enemies
        aura = self.attr(Attribute.AURA_DAMAGE)
        if aura > 0 and not self.is_contested():
            adjacent_enemies = Managers.piece_manager.get_adjacent_enemies(self.gx, self.gy, self.team)
            for enemy in adjacent_enemies:
                enemy.damage_hp(self.get_attack_rating(enemy) * aura, self)

        # Pieces occupying tiles they can't traverse take damage each turn.
        if not Managers.battle_map.is_tile_passable(self.gx, self.gy, self.attr(Attribute.MOVEMENT_TYPE)):
            tile_type = Managers.battle_map.get_tile_type_at(self.gx, self.gy)
            self.damage_hp(30, tile_type)

            Managers.combat_logger.log_damage(self, 50, tile_type)

            publish_game_event(EventType.E_PIECE_ON_INVALID_TERRAIN, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })

    def handle_phase_orders(self, event):
        pass

    def handle_phase_build(self, event):
        # Execute build orders
        if isinstance(self.current_order, BuildOrder):
            if self.is_contested():
                # Can't build if there's an enemy piece here
                self.abort_order()
            else:
                publish_game_event(EventType.E_PIECE_BUILT, {
                    'tx': self.current_order.tx,
                    'ty': self.current_order.ty,
                    'team': self.team,
                    'new_piece_type': self.current_order.new_piece_type
                })

                Managers.combat_logger.log_successful_order_execution(self, self.current_order)

                # Deduct unit price
                Managers.team_manager.deduct_resources(
                    self.team, Managers.team_manager.attr(self.team, self.current_order.new_piece_type, Attribute.PRICE))
                # Pop orders once they're executed
                self.current_order = None

    def handle_phase_move(self, event):
        # Execute move orders
        if isinstance(self.current_order, MoveOrder):
            # Note: we don't change our own gx and gy-- the piece manager will do that when it changes our 'address'
            publish_game_event(EventType.E_UNIT_MOVED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'dx': self.current_order.dx,
                'dy': self.current_order.dy
            })

            # Apply entrenchment bonus based on distance moved
            self.apply_entrenchment(abs(self.gx - self.current_order.dx) + abs(self.gy - self.current_order.dy))

            Managers.combat_logger.log_successful_order_execution(self, self.current_order)

            # Pop orders once they're executed
            self.current_order = None
        else:
            # Apply the full entrenchment bonus
            self.apply_entrenchment(0)

    def handle_end_phase_move(self, event):
        # Apply buffs to allies on adjacent tiles, if necessary
        armor_share = self.attr(Attribute.ARMOR_SHARE)
        if armor_share > 0:
            adjacent_allies = Managers.piece_manager.get_adjacent_pieces(self.gx, self.gy, self.team)

            for ally in adjacent_allies:
                ally.temporary_armor += armor_share
                publish_game_event(EventType.E_ARMOR_GRANTED, {
                    'gx': ally.gx,
                    'gy': ally.gy,
                    'team': ally.team
                })

    def handle_phase_combat(self, event):
        pass

    def handle_phase_ranged(self, event):
        # Execute ranged attack orders
        if isinstance(self.current_order, RangedAttackOrder):
            if self.is_contested():
                # Can't conduct a ranged attack if there's an enemy on our tile
                publish_game_event(EventType.E_ORDER_CANCELED, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team
                })

                Managers.combat_logger.log_failed_order_execution(self, self.current_order)

                # Abort the order
                self.current_order = None
            else:
                publish_game_event(EventType.E_UNIT_RANGED_ATTACK, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'tx': self.current_order.tx,
                    'ty': self.current_order.ty
                })

                Managers.combat_logger.log_successful_order_execution(self, self.current_order)

                # Pop orders once they're executed
                self.current_order = None

    def handle_phase_special(self, event):
        # Execute upgrade orders
        if isinstance(self.current_order, UpgradeOrder):
            if self.is_contested():
                # Can't upgrade if there's an enemy piece here
                self.abort_order()
            else:
                publish_game_event(EventType.E_UPGRADE_BUILT, {
                    'team': self.team,
                    'new_upgrade_type': self.current_order.new_upgrade_type
                })

                Managers.combat_logger.log_successful_order_execution(self, self.current_order)

                # Deduct upgrade price
                Managers.team_manager.deduct_resources(self.team, base_upgrades[self.current_order.new_upgrade_type][UpgradeAttribute.UPGRADE_PRICE])

                # Pop orders once they're executed
                self.current_order = None

        # Execute terraforming orders
        elif isinstance(self.current_order, TerraformOrder):
            if self.is_contested():
                # Can't terraform if there's an enemy piece here
                self.abort_order()
            else:
                publish_game_event(EventType.E_TILE_TERRAFORMED, {
                    'gx': self.current_order.tx,
                    'gy': self.current_order.ty,
                    'raising': self.current_order.raising
                })

                Managers.combat_logger.log_successful_order_execution(self, self.current_order)

                # Pop orders once they're executed
                self.current_order = None

        # Execute demolition orders
        elif isinstance(self.current_order, DemolishOrder):
            self.damage_hp(self.hp)

            Managers.combat_logger.log_successful_order_execution(self, self.current_order)
            self.current_order = None

    # Handle menu events concerning us
    def handle_menu_option(self, event):
        if event.option == Option.MENU_MOVE:
            publish_game_event(EventType.E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': self.get_movement_range(),
                'movement_type': self.attr(Attribute.MOVEMENT_TYPE),
                'piece_type': self.piece_type,
                'team': self.team,
                'option': event.option
            })
        elif event.option == Option.MENU_RANGED_ATTACK:
            publish_game_event(EventType.E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': self.attr(Attribute.MIN_RANGE),
                'max_range': self.attr(Attribute.MAX_RANGE),
                'movement_type': None,
                'piece_type': None,
                'team': self.team,
                'option': event.option
            })
        elif event.option == Option.MENU_BUILD_PIECE:
            # Open the build menu and allow selecting a buildable piece
            publish_game_event(EventType.E_OPEN_BUILD_MENU, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'options': self.get_valid_buildable_pieces()
            })
        elif event.option in PieceType:
            # Attempting to build something, so open the tile selection
            publish_game_event(EventType.E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'movement_type': Managers.team_manager.attr(self.team, event.option, Attribute.MOVEMENT_TYPE),
                'piece_type': event.option,
                'team': self.team,
                'option': event.option
            })
        elif event.option == Option.MENU_PURCHASE_UPGRADE:
            # Open the build menu and allow selecting an upgrade to purchase
            publish_game_event(EventType.E_OPEN_UPGRADE_MENU, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'options': self.get_valid_purchaseable_upgrades()
            })
        elif event.option in [Option.MENU_RAISE_TILE, Option.MENU_LOWER_TILE]:
            # Attempting to terraform, so open the tile selection
            publish_game_event(EventType.E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'movement_type': MovementType.RAISE if event.option == Option.MENU_RAISE_TILE else MovementType.LOWER,
                'piece_type': None,
                'team': self.team,
                'option': event.option
            })
        else:
            self.set_order(event)

    # Save orders to this piece
    def set_order(self, event):
        if event.option == Option.MENU_MOVE:
            self.current_order = MoveOrder(event.dx, event.dy)
        elif event.option == Option.MENU_RANGED_ATTACK:
            self.current_order = RangedAttackOrder(event.dx, event.dy)
        elif event.option in PieceType:
            self.current_order = BuildOrder(event.dx, event.dy, event.option)
        elif event.option in UpgradeType:
            self.current_order = UpgradeOrder(event.option)
        elif event.option == Option.MENU_CANCEL_ORDER:
            self.current_order = None
        elif event.option == Option.MENU_RAISE_TILE:
            self.current_order = TerraformOrder(event.dx, event.dy, raising=True)
        elif event.option == Option.MENU_LOWER_TILE:
            self.current_order = TerraformOrder(event.dx, event.dy, raising=False)
        elif event.option == Option.MENU_DEMOLISH_SELF:
            self.current_order = DemolishOrder()
        else:
            self.current_order = None

    # Triggered when this piece might be selected
    def select(self, event):
        if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
            available_actions = self.get_available_actions()

            if not event.selecting_movement and len(available_actions) > 0:
                publish_game_event(EventType.E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'options': available_actions
                })

    # Triggered when this piece's menu might have closed
    def close_menu(self, event):
        if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
            self.handle_menu_option(event)

    # Triggered when this piece's tile selection might have closed
    def tile_selected(self, event):
        if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
            self.set_order(event)

    def step(self, event):
        super().step(event)

        # Check if we're in conflict
        self.in_conflict = Managers.turn_manager.phase == BattlePhase.ORDERS and \
                           len(Managers.piece_manager.get_enemy_pieces_at(self.gx, self.gy, self.team)) > 0

    def start_previewing_orders(self):
        self.previewing_order = True

    def stop_previewing_orders(self):
        self.previewing_order = False

    # Render a preview of the piece's current orders.
    def preview_order(self, game_screen):
        if self.current_order:
            if isinstance(self.current_order, MoveOrder):
                target_sprite = self.sprite.copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.dx * GRID_WIDTH,
                                                 self.current_order.dy * GRID_HEIGHT))
            elif isinstance(self.current_order, RangedAttackOrder):
                target_sprite = spr_target[self.team].copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.tx * GRID_WIDTH,
                                                 self.current_order.ty * GRID_HEIGHT))
            elif isinstance(self.current_order, BuildOrder):
                target_sprite = spr_pieces[self.team][self.current_order.new_piece_type].subsurface((0, 0, 24, 24)).copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.tx * GRID_WIDTH,
                                                 self.current_order.ty * GRID_HEIGHT))
                game_screen.blit(draw_small_resource_count(clear_color, spr_resource_icon_small, spr_digit_icons, self.team,
                                                 Managers.team_manager.attr(self.team, self.current_order.new_piece_type, Attribute.PRICE)),
                                 (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT + 16))

            elif isinstance(self.current_order, UpgradeOrder):
                target_sprite = spr_upgrade_icons[self.team][self.current_order.new_upgrade_type].copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.gx * GRID_WIDTH,
                                                 self.gy * GRID_HEIGHT))
                game_screen.blit(draw_small_resource_count(clear_color, spr_resource_icon_small, spr_digit_icons, self.team,
                                                           base_upgrades[self.current_order.new_upgrade_type][UpgradeAttribute.UPGRADE_PRICE]),
                                 (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT + 16))

    # Ask the Unit to render itself
    def render(self, game_screen, ui_screen):
        # Only render if we're within the camera view
        if Managers.player_manager.is_within_camera_view((self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)):
            super().render(game_screen, ui_screen)

            xoffset = 0
            yoffset = 0

            if self.in_conflict:
                if self.team == Team.RED:
                    xoffset = -3
                    yoffset = -3
                elif self.team == Team.BLUE:
                    xoffset = 3
                    yoffset = 3
                elif self.team == Team.GREEN:
                    xoffset = -3
                    yoffset = 3
                elif self.team == Team.YELLOW:
                    xoffset = 3
                    yoffset = -3

            # Render the unit
            game_screen.blit(self.sprite, (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset))

            # Render health bar if damaged
            max_hp = self.attr(Attribute.MAX_HP)
            if self.hp < max_hp:
                displayable_hp = int((self.hp / max_hp) * 20)

                game_screen.fill(clear_color[self.team],
                                 (self.gx * GRID_WIDTH + xoffset + 2, self.gy * GRID_HEIGHT + yoffset + 21, 18, 3))
                game_screen.fill(light_team_color[self.team],
                                 (self.gx * GRID_WIDTH + xoffset + 2, self.gy * GRID_HEIGHT + yoffset + 21, displayable_hp, 2))

            # Render order flag
            if self.current_order and Managers.player_manager.active_team == self.team:
                game_screen.blit(spr_order_flags[self.current_order.name],
                                 (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset + 16))

            if self.previewing_order:
                self.preview_order(game_screen)
