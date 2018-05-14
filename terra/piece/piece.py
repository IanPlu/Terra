import pygame

from terra.ai.pathfinder import get_path_to_destination
from terra.constants import GRID_WIDTH, GRID_HEIGHT, NETWORK_ANIMATION_SPEED
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.engine.animatedgameobject import AnimatedGameObject
from terra.engine.animationstate import AnimationState
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType
from terra.piece.movementtype import MovementType, MovementAttribute, movement_types
from terra.piece.orders import MoveOrder, RangedAttackOrder, BuildOrder, UpgradeOrder, TerraformOrder, DemolishOrder, \
    HealOrder
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, spr_order_flags, clear_color, spr_upgrade_icons, \
    spr_target, light_team_color, spr_digit_icons, spr_resource_icon_small, light_color, spr_cursor
from terra.settings import SETTINGS, Setting
from terra.strings import piece_name_strings, LANGUAGE
from terra.team.team import Team
from terra.turn.battlephase import BattlePhase
from terra.util.drawingutil import draw_small_resource_count, draw_text

team_offsets = {
    Team.RED: (-3, -3),
    Team.BLUE: (3, 3),
    Team.GREEN: (-3, 3),
    Team.YELLOW: (3, -3),
    Team.NONE: (-2, 2)
}


# Base object in play belonging to a player, like a unit or a building.
# They belong to a team and exist somewhere on the map.
# Pieces have HP and can accept and execute orders.
class Piece(AnimatedGameObject):
    def __init__(self, piece_type=PieceType.COLONIST, team=Team.RED, gx=0, gy=0, hp=None):
        self.team = team
        self.gx = gx
        self.gy = gy

        # Rendered grid coordinates. Will line up with the grid coords over time for smoothish animation.
        self.rendered_gx = self.gx * GRID_WIDTH
        self.rendered_gy = self.gy * GRID_HEIGHT

        # How quickly pieces will animate and scroll to their correct locations. Higher number = slower movement
        self.move_animation_speed = 12 / (NETWORK_ANIMATION_SPEED if self.is_network_game() else
                                          SETTINGS.get(Setting.ANIMATION_SPEED))
        self.move_animation_snap_dist = 1

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

        self.temporary_armor = 0
        self.last_attacker = None
        self.temporary_aoe_on_death = 0
        self.temporary_money_lost_on_death = 0

        self.previewing_order = False

        # AI pathfinding caching
        self.current_goal = None
        self.current_path = None

        indexed_pieces = [PieceType.COLONIST, PieceType.TROOPER, PieceType.RANGER, PieceType.GHOST,
                          PieceType.GUARDIAN, PieceType.BOLTCASTER, PieceType.BANSHEE,
                          PieceType.TITAN, PieceType.EARTHRENDER, PieceType.DEMON]

        framerate = 8 if team is not Team.NONE else 0

        super().__init__(spr_pieces[self.team][self.piece_type], 24, framerate, indexed=self.piece_type in indexed_pieces,
                         use_global_animation_frame=team is not Team.NONE, own_frames_for_index=True)

    def __str__(self):
        return "{} {} at tile ({}, {}) with {} HP" \
            .format(self.team.name, piece_name_strings[LANGUAGE][self.piece_type], self.gx, self.gy, self.hp)

    # Return an attribute about this piece.
    def attr(self, attribute):
        return self.get_manager(Manager.TEAM).attr(self.team, self.piece_type, attribute)

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
        return self.get_mode() in [Mode.BATTLE, Mode.NETWORK_BATTLE]

    # Get the sprite index to display.
    def get_index(self):
        if (self.rendered_gx != self.gx * GRID_WIDTH or self.rendered_gy != self.gy * GRID_HEIGHT) or \
                (isinstance(self.current_order, MoveOrder) and self.get_manager(Manager.TURN).phase == BattlePhase.EXECUTE_MOVE):
            animation_state = AnimationState.MOVING
        else:
            animation_state = AnimationState.IDLE

        return animation_state.value

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
        if self.hp < self.attr(Attribute.MAX_HP):
            actions.append(Option.MENU_HEAL_SELF)

        if len(actions) > 0 and self.current_order:
            actions.append(Option.MENU_CANCEL_ORDER)

        return actions

    # Trim the list of innately buildable pieces to ones that can be placed nearby, taking tile type etc. into account
    # TODO: Use 'can_build_piece_onto_tile()'
    def get_valid_buildable_pieces(self):
        valid_pieces = []

        unoccupied_tiles = self.get_base_buildable_tiles()

        # For each buildable piece, if there exists at least one valid adjacent tile for its movement type that we can
        # place it onto, add it to the list
        for piece in self.attr(Attribute.BUILDABLE_PIECES):
            valid_tile_types = movement_types[self.get_manager(Manager.TEAM).attr(self.team, piece, Attribute.MOVEMENT_TYPE)][MovementAttribute.PASSABLE]
            unoccupied_tile_types = set([self.get_manager(Manager.MAP).get_tile_type_at(coord[0], coord[1]) for coord in unoccupied_tiles])

            if not unoccupied_tile_types.isdisjoint(valid_tile_types):
                valid_pieces.append(piece)

        return valid_pieces

    # Return a list of the adjacent tiles we could potentially build onto
    def get_base_buildable_tiles(self):
        tiles_to_check = [(self.gx + 1, self.gy),
                          (self.gx - 1, self.gy),
                          (self.gx, self.gy + 1),
                          (self.gx, self.gy - 1)]
        unoccupied_tiles = []

        # Remove tiles that already have allies on it that can't move, and tiles that are off the map
        for tile_x, tile_y in tiles_to_check:
            if self.get_manager(Manager.MAP).get_tile_at(tile_x, tile_y):
                immobile_allies = []
                for piece in self.get_manager(Manager.PIECE).get_pieces_at(tile_x, tile_y, team=self.team):
                    if piece.attr(Attribute.MOVEMENT_RANGE) <= 0:
                        immobile_allies.append(piece)

                # Can't build onto tiles where enemy buildings are
                enemy_buildings = self.get_manager(Manager.PIECE).get_enemy_pieces_at(tile_x, tile_y, self.team, piece_subtype=PieceSubtype.BUILDING)

                if len(immobile_allies) <= 0 and len(enemy_buildings) <= 0:
                    unoccupied_tiles.append((tile_x, tile_y))

        return unoccupied_tiles

    # Return true if the provided piece type could be built onto the specified tile
    def can_build_piece_onto_tile(self, piece_type, tile):
        valid_tile_types = movement_types[self.get_manager(Manager.TEAM).attr(self.team, piece_type, Attribute.MOVEMENT_TYPE)][MovementAttribute.PASSABLE]
        tile_type = self.get_manager(Manager.MAP).get_tile_type_at(tile[0], tile[1])

        # Can't build onto tiles where enemy buildings are
        enemy_buildings = self.get_manager(Manager.PIECE).get_enemy_pieces_at(tile[0], tile[1], self.team, piece_subtype=PieceSubtype.BUILDING)

        return tile_type in valid_tile_types and len(enemy_buildings) == 0

    # Get the list of upgrades that can be purchased by this piece
    def get_valid_purchaseable_upgrades(self):
        return self.attr(Attribute.PURCHASEABLE_UPGRADES)

    # Return a list of adjacent tiles that can be traversed by this movement type
    def get_valid_tiles_for_terraforming(self, raising=True):
        if self.attr(Attribute.TERRAFORMING):
            return self.get_manager(Manager.MAP).get_valid_adjacent_tiles_for_movement_type(
                self.gx, self.gy, MovementType.RAISE if raising else MovementType.LOWER)
        else:
            return []

    # Return this piece's attack strength against a target
    def get_attack_rating(self, target):
        attack = self.attr(Attribute.ATTACK)
        multiplier = self.attr(Attribute.ATTACK_MULTIPLIER)[target.piece_archetype]
        health_modifier = self.hp / self.attr(Attribute.MAX_HP)

        # Round up-- always do at least one point of damage
        return int(max(attack * multiplier * health_modifier, 1))

    # Return the combination of any innate armor, entrenchment bonuses, etc. this piece has
    def get_defense_rating(self):
        return self.attr(Attribute.ARMOR) + \
               self.temporary_armor

    # Get movement range, plus any bonuses
    def get_movement_range(self):
        movement_range = self.attr(Attribute.MOVEMENT_RANGE)

        if self.attr(Attribute.KICKOFF):
            movement_range += len(self.get_manager(Manager.PIECE).get_adjacent_pieces(self.gx, self.gy, self.team))

        return movement_range

    # Clean ourselves up at the end of turns, die as appropriate
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
            'team': self.team,
            'piece': self
        })

        # Bases being destroyed ends the game
        if self.piece_type == PieceType.BASE:
            publish_game_event(EventType.E_BASE_DESTROYED, {
                'team': self.team
            })

        if self.last_attacker:
            # Explode if we've been hit by a temporary AoE debuff
            if self.temporary_aoe_on_death > 0:
                publish_game_event(EventType.E_DEATH_AOE, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                })

                for ally in self.get_manager(Manager.PIECE).get_adjacent_pieces(self.gx, self.gy, self.team):
                    ally.damage_hp(self.temporary_aoe_on_death, self.last_attacker)

            # Drain resources when killed if we've been hit by the steal debuff
            if self.temporary_money_lost_on_death > 0:
                self.get_manager(Manager.TEAM).deduct_resources(self.team, self.temporary_money_lost_on_death)
                self.get_manager(Manager.TEAM).add_resources(self.last_attacker.team, self.temporary_money_lost_on_death)
                publish_game_event(EventType.E_DEATH_MONEY_LOSS, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                })

    # Cancel our current order, usually if we're contested.
    def abort_order(self):
        publish_game_event(EventType.E_ORDER_CANCELED, {
            'gx': self.gx,
            'gy': self.gy,
            'team': self.team
        })

        # Abort the order
        self.current_order = None

    # Return true if this piece is contested by an enemy piece occupying the same tile.
    # Caveats: the enemy might not be able to contest us, or can't be contested
    def is_contested(self):
        if self.attr(Attribute.IGNORE_CONTESTING):
            return False
        else:
            enemy_pieces = self.get_manager(Manager.PIECE).get_enemy_pieces_at(self.gx, self.gy, self.team)
            contesting_pieces = []
            for piece in enemy_pieces:
                # Contests if all of the following are true:
                # - Enemy can attack us (some pieces can't attack buildings, which we might be)
                # - Enemy deals melee damage (not ranged)
                # - Enemy has an attack rating (so they'll actually hurt us)
                # - Enemy is moving to or staying on our tile, not moving away
                can_attack_us = not (piece.attr(Attribute.CANT_ATTACK_BUILDINGS) and self.piece_subtype is PieceSubtype.BUILDING)
                is_melee = piece.attr(Attribute.DAMAGE_TYPE) == DamageType.MELEE
                has_attack_damage = piece.attr(Attribute.ATTACK) > 0
                is_moving_to_our_tile = piece.current_order is MoveOrder and piece.current_order.dx == self.gx and piece.current_order.dy == self.gy
                is_staying_on_our_tile = piece.current_order is not MoveOrder and piece.gx == self.gx and piece.gy == self.gy

                if can_attack_us and is_melee and has_attack_damage and (is_moving_to_our_tile or is_staying_on_our_tile):
                    contesting_pieces.append(piece)

            return len(contesting_pieces) > 0

    # Hook for any effects that should trigger on dealing damage, like lifesteal
    def on_damaging_enemy(self, damage, enemy):
        lifesteal = damage * self.attr(Attribute.LIFESTEAL)
        if lifesteal > 0:
            self.heal_hp(lifesteal)

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

        publish_game_event(EventType.E_PIECE_DAMAGED, {
            'piece': self,
            'damage': damage,
            'source': source,
        })

    # Heal this piece for the specified amount
    def heal_hp(self, heal):
        max_hp = self.attr(Attribute.MAX_HP)
        if self.hp < max_hp:
            self.hp = min(self.hp + heal, max_hp)
            publish_game_event(EventType.E_PIECE_HEALED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'health': heal
            })

    # Return a score for moving from tile A to tile B. Lower numbers are preferred.
    def get_move_score(self, a, b, blocked):
        piece_manager = self.get_manager(Manager.PIECE)
        x1, y1 = a
        x2, y2 = b

        distance = abs(x1 - x2) + abs(y1 - y2)
        ally_building_score = 10 if piece_manager.get_piece_at(x2, y2, self.team, PieceSubtype.BUILDING) else 0

        enemies = piece_manager.get_enemy_pieces_at(x2, y2, self.team)
        enemy_score = 0
        for enemy in enemies:
            # If this piece can't enter buildings, score appropriately
            if enemy.piece_subtype == PieceSubtype.BUILDING and self.attr(Attribute.CANT_ATTACK_BUILDINGS):
                enemy_score += 9999

            multiplier = self.attr(Attribute.ATTACK_MULTIPLIER)[enemy.piece_archetype] * self.attr(Attribute.ATTACK)
            if multiplier >= 1:
                enemy_score -= 1 * multiplier
            else:
                enemy_score += 2 * multiplier

        # Avoid blocked tiles whenever possible
        avoid_score = 5 if (a, b) in blocked else 0

        # print("{} | {} {} {}".format(distance, ally_building_score, enemy_score, avoid_score))
        return distance + ally_building_score + enemy_score + avoid_score

    def is_enemy_at_tile(self, tile):
        return len(self.get_manager(Manager.PIECE).get_enemy_pieces_at(tile[0], tile[1], self.team)) > 0 \
                             and not self.attr(Attribute.IGNORE_IMPEDANCE)

    # Return true if this piece can move to and occupy this tile
    def is_tile_occupyable(self, tile):
        return not self.get_manager(Manager.PIECE).get_piece_at(tile[0], tile[1], self.team, PieceSubtype.BUILDING)

    # Find a path to the target.
    # If a minimum and maximum range is provided, will attempt to path to within that range of the target. 0=Exact tile.
    # If blocked is provided, will navigate around the specified blocked tiles
    def get_path_to_target(self, target, blocked=None, min_range=0, max_range=0, movement_type=None):
        destinations = self.get_manager(Manager.MAP).get_tiles_in_range(target[0], target[1],
                                                                        min_range, max_range, movement_type)
        # Sort destinations by the closest
        destinations.sort(key=lambda tile: abs(tile[0] - self.gx) + abs(tile[1] - self.gy))

        # Remove blocked tiles from the destinations
        for blocker in blocked:
            if blocker in destinations:
                destinations.remove(blocker)

        if len(destinations) > 0:
            potential_paths = []
            for destination in destinations:
                potential_path = get_path_to_destination((self.gx, self.gy), destination,
                                                         self.get_manager(Manager.MAP), self, blocked)
                if potential_path:
                    potential_paths.append(potential_path)

            if len(potential_paths) > 0:
                potential_paths.sort(key=lambda path: len(path))
                self.current_path = potential_paths[0]
            else:
                self.current_path = None

            return self.current_path
        else:
            return []

    # Figure out how many steps along the path we can take, return the end point
    def step_along_path(self, path, blocked):
        current_steps = 0
        max_steps = min(self.attr(Attribute.MOVEMENT_RANGE), len(path) - 1)
        last_possible_destination = (self.gx, self.gy)
        while current_steps <= max_steps:
            path_dest = path[current_steps]

            # If the tile is clear of planned ally positions, mark our last possible destination
            if not path_dest in blocked:
                last_possible_destination = path_dest

            # If there's no impedance in our way, or if it's our first move, continue stepping forward
            if not self.is_enemy_at_tile(path_dest) or current_steps == 0:
                current_steps += 1
            else:
                break

        return last_possible_destination

    # Phase handlers. Other than the orders handler, these are only triggered when we have orders.
    def handle_phase_start_turn(self, event):
        # Produce resources
        if self.attr(Attribute.RESOURCE_PRODUCTION) > 0:
            self.get_manager(Manager.TEAM).add_resources(self.team, self.attr(Attribute.RESOURCE_PRODUCTION))

        # Regen health
        regen = self.attr(Attribute.REGEN)
        if regen > 0:
            self.heal_hp(regen)

        # Apply medic healing to adjacent allies
        medic = self.attr(Attribute.MEDIC)
        if medic > 0:
            adjacent_allies = self.get_manager(Manager.PIECE).get_adjacent_pieces(self.gx, self.gy, self.team)
            for ally in adjacent_allies:
                ally.heal_hp(medic)

        # Apply aura damage to adjacent enemies
        aura = self.attr(Attribute.AURA_DAMAGE)
        if aura > 0 and not self.is_contested():
            adjacent_enemies = self.get_manager(Manager.PIECE).get_adjacent_enemies(self.gx, self.gy, self.team)
            for enemy in adjacent_enemies:
                enemy.damage_hp(self.get_attack_rating(enemy) * aura, self)

        # Pieces occupying tiles they can't traverse take damage each turn.
        if not self.get_manager(Manager.MAP).is_tile_passable(self.gx, self.gy, self.attr(Attribute.MOVEMENT_TYPE)):
            tile_type = self.get_manager(Manager.MAP).get_tile_type_at(self.gx, self.gy)
            damage = 30
            self.damage_hp(damage, tile_type)

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

                # Deduct unit price
                self.get_manager(Manager.TEAM).deduct_resources(
                    self.team, self.get_manager(Manager.TEAM).attr(self.team, self.current_order.new_piece_type, Attribute.PRICE))
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

            # Pop orders once they're executed
            self.current_order = None

    def handle_end_phase_move(self, event):
        # Apply buffs to allies on adjacent tiles, if necessary
        armor_share = self.attr(Attribute.ARMOR_SHARE)
        if armor_share > 0:
            adjacent_allies = self.get_manager(Manager.PIECE).get_adjacent_pieces(self.gx, self.gy, self.team)

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

                # Deduct upgrade price
                self.get_manager(Manager.TEAM).deduct_resources(self.team, base_upgrades[self.current_order.new_upgrade_type][UpgradeAttribute.UPGRADE_PRICE])

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

                # Pop orders once they're executed
                self.current_order = None

        # Execute demolition orders
        elif isinstance(self.current_order, DemolishOrder):
            self.damage_hp(self.hp)

            publish_game_event(EventType.E_PIECE_DEMOLISHED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })

            self.current_order = None

        # Execute heal orders
        elif isinstance(self.current_order, HealOrder):
            if self.is_contested():
                # Can't heal if there's an enemy piece here
                self.abort_order()
            else:
                self.heal_hp(self.attr(Attribute.HEAL_POWER))
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
                'movement_type': self.get_manager(Manager.TEAM).attr(self.team, event.option, Attribute.MOVEMENT_TYPE),
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
        elif event.option == Option.MENU_HEAL_SELF:
            self.current_order = HealOrder()
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
        self.in_conflict = self.get_manager(Manager.TURN).phase == BattlePhase.ORDERS and \
                           len(self.get_manager(Manager.PIECE).get_enemy_pieces_at(self.gx, self.gy, self.team)) > 0

    def start_previewing_orders(self):
        self.previewing_order = True

    def stop_previewing_orders(self):
        self.previewing_order = False

    def preview_path(self, game_screen):
        if self.current_path:
            for tile in self.current_path:
                game_screen.blit(spr_cursor[self.team], (tile[0] * 24, tile[1] * 24))

        # for x in range(self.get_manager(Manager.MAP).width):
        #     for y in range(self.get_manager(Manager.MAP).height):
        #         score = draw_text(str(self.get_move_score((self.gx, self.gy), (x, y), [])), light_color)
        #         game_screen.blit(score, (x * 24 + 8, y * 24 + 8))

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
                                                           self.get_manager(Manager.TEAM).attr(self.team, self.current_order.new_piece_type, Attribute.PRICE)),
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
        if self.get_manager(Manager.PLAYER).is_within_camera_view((self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT, GRID_WIDTH, GRID_HEIGHT)):
            super().render(game_screen, ui_screen)

            # Animate pieces moving to their destinations
            desired_x = self.gx * GRID_WIDTH
            desired_y = self.gy * GRID_WIDTH

            if self.rendered_gx != desired_x:
                self.rendered_gx += (desired_x - self.rendered_gx) / self.move_animation_speed
                if abs(self.rendered_gx - desired_x) <= self.move_animation_snap_dist:
                    self.rendered_gx = desired_x
            if self.rendered_gy != desired_y:
                self.rendered_gy += (desired_y - self.rendered_gy) / self.move_animation_speed
                if abs(self.rendered_gy - desired_y) <= self.move_animation_snap_dist:
                    self.rendered_gy = desired_y

            xoffset, yoffset = team_offsets[self.team] if self.in_conflict else (0, 0)

            actual_x = self.rendered_gx + xoffset
            actual_y = self.rendered_gy + yoffset

            # Render the unit
            game_screen.blit(self.sprite, (actual_x, actual_y))

            # Render health bar if damaged
            max_hp = self.attr(Attribute.MAX_HP)
            if self.hp < max_hp:
                displayable_hp = int((self.hp / max_hp) * 20)

                game_screen.fill(clear_color[self.team],
                                 (actual_x + 2, actual_y + 21, 18, 3))
                game_screen.fill(light_team_color[self.team],
                                 (actual_x + 2, actual_y + 21, displayable_hp, 2))

            # Render order flag
            if self.current_order and self.get_manager(Manager.PLAYER).active_team == self.team:
                game_screen.blit(spr_order_flags[self.current_order.name],
                                 (actual_x, actual_y + 16))

                # Render order preview
                if self.previewing_order:
                    self.preview_order(game_screen)
                    self.preview_path(game_screen)

            # Render ranged attacks
            if self.get_manager(Manager.TURN).phase == BattlePhase.EXECUTE_COMBAT and isinstance(self.current_order, RangedAttackOrder):
                pygame.draw.line(game_screen, light_team_color[self.team], (self.gx * GRID_WIDTH + 12, self.gy * GRID_HEIGHT + 12),
                                 (self.current_order.tx * GRID_WIDTH + 12, self.current_order.ty * GRID_HEIGHT + 12), 3)
                pygame.draw.line(game_screen, light_color, (self.gx * GRID_WIDTH + 12, self.gy * GRID_HEIGHT + 12),
                                 (self.current_order.tx * GRID_WIDTH + 12, self.current_order.ty * GRID_HEIGHT + 12), 1)
