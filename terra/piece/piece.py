from math import ceil

from pygame import KEYDOWN, KEYUP

from terra.battlephase import BattlePhase
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.economy.upgrades import UpgradeType, base_upgrades
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_MENU2
from terra.managers.managers import Managers
from terra.piece.damagetype import DamageType
from terra.piece.movementtype import passable_terrain_types
from terra.piece.orders import MoveOrder, RangedAttackOrder, BuildOrder, UpgradeOrder
from terra.piece.pieceattributes import Attribute
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, spr_order_flags, spr_digit_icons, clear_color, spr_upgrade_icons, \
    spr_target
from terra.settings import LANGUAGE
from terra.strings import piece_name_strings
from terra.team import Team


# Base object in play belonging to a player, like a unit or a building.
# They belong to a team and exist somewhere on the map.
# Pieces have HP and can accept and execute orders.
class Piece(GameObject):
    def __init__(self, piece_type=PieceType.COLONIST, team=Team.RED, gx=0, gy=0, hp=None):
        super().__init__()
        self.team = team
        self.gx = gx
        self.gy = gy

        # Look up values based on our piece type
        self.piece_type = piece_type
        self.piece_subtype = Managers.team_manager.attr(self.team, self.piece_type, Attribute.SUBTYPE)

        # Interpreted variables. Don't touch!
        if hp:
            self.hp = hp
        else:
            self.hp = Managers.team_manager.attr(self.team, self.piece_type, Attribute.MAX_HP)
        self.current_order = None
        self.in_conflict = False
        self.tile_selection = None
        self.entrenchment = 0
        self.previewing_order = False

    def __str__(self):
        return "{} {} at tile ({}, {}) with {} HP" \
            .format(self.team.name, piece_name_strings[LANGUAGE][self.piece_type], self.gx, self.gy, self.hp)

    def get_sprite(self):
        return spr_pieces[self.team][self.piece_type]

    # Return a list of actions to show in the selection UI.
    def get_available_actions(self):
        actions = []

        if Managers.team_manager.attr(self.team, self.piece_type, Attribute.MOVEMENT_RANGE) > 0:
            actions.append(MENU_MOVE)
        if Managers.team_manager.attr(self.team, self.piece_type, Attribute.DAMAGE_TYPE) == DamageType.RANGED:
            actions.append(MENU_RANGED_ATTACK)
        if len(self.get_valid_buildable_pieces()):
            actions.append(MENU_BUILD_PIECE)
        if len(self.get_valid_purchaseable_upgrades()):
            actions.append(MENU_PURCHASE_UPGRADE)

        if len(actions) > 0:
            actions.append(MENU_CANCEL_ORDER)

        return actions

    # Trim the list of innately buildable pieces to ones that can be placed nearby, taking tile type etc. into account
    def get_valid_buildable_pieces(self):
        valid_pieces = []

        # For each buildable piece, if there exists at least one valid adjacent tile for its movement type that we can
        # place it onto, add it to the list
        for piece in Managers.team_manager.attr(self.team, self.piece_type, Attribute.BUILDABLE_PIECES):
            valid_tiles = passable_terrain_types[Managers.team_manager.attr(self.team, piece, Attribute.MOVEMENT_TYPE)]
            adjacent_tile_types = {
                Managers.battle_map.get_tile_type_at(self.gx + 1, self.gy),
                Managers.battle_map.get_tile_type_at(self.gx - 1, self.gy),
                Managers.battle_map.get_tile_type_at(self.gx, self.gy + 1),
                Managers.battle_map.get_tile_type_at(self.gx, self.gy - 1),
            }

            if not adjacent_tile_types.isdisjoint(valid_tiles):
                valid_pieces.append(piece)

        return valid_pieces

    def get_valid_purchaseable_upgrades(self):
        return Managers.team_manager.attr(self.team, self.piece_type, Attribute.PURCHASEABLE_UPGRADES)

    # Clean ourselves up at the end of phases, die as appropriate
    def cleanup(self):
        if self.hp < 5:
            publish_game_event(E_PIECE_DEAD, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })
            self.on_death()

    # Do anything special on death
    def on_death(self):
        pass

    # Cancel our current order, usually if we're contested.
    def abort_order(self):
        publish_game_event(E_ORDER_CANCELED, {
            'gx': self.gx,
            'gy': self.gy,
            'team': self.team
        })

        Managers.combat_logger.log_failed_order_execution(self, self.current_order)

        # Abort the order
        self.current_order = None

    # Return true if this piece is contested by an enemy piece occupying the same tile
    def is_contested(self):
        return len(Managers.piece_manager.get_enemy_pieces_at(self.gx, self.gy, self.team)) > 0

    # Phase handlers. Other than the orders handler, these are only triggered when we have orders.
    def handle_phase_start_turn(self, event):
        # Produce resources
        if not Managers.team_manager.attr(self.team, self.piece_type, Attribute.RESOURCE_PRODUCTION) == (0, 0, 0):
            Managers.team_manager.add_resources(self.team, Managers.team_manager.attr(
                self.team, self.piece_type, Attribute.RESOURCE_PRODUCTION))

    def handle_phase_orders(self, event):
        pass

    def handle_phase_build(self, event):
        # Execute build orders
        if isinstance(self.current_order, BuildOrder):
            if self.is_contested():
                # Can't build if there's an enemy piece here
                self.abort_order()
            else:
                publish_game_event(E_PIECE_BUILT, {
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
            publish_game_event(E_UNIT_MOVED, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'dx': self.current_order.dx,
                'dy': self.current_order.dy
            })

            # Apply entrenchment bonus based on distance moved
            self.apply_entrenchment(abs(self.gx - self.current_order.dx) + abs(self.gy - self.current_order.dy))

            self.gx = self.current_order.dx
            self.gy = self.current_order.dy

            Managers.combat_logger.log_successful_order_execution(self, self.current_order)

            # Pop orders once they're executed
            self.current_order = None
        else:
            # Apply the full entrenchment bonus
            self.apply_entrenchment(0)

    # Apply an entrenchment bonus per unused movement range (up to 2)
    def apply_entrenchment(self, distance):
        self.entrenchment = min(Managers.team_manager.attr(self.team, self.piece_type, Attribute.MOVEMENT_RANGE), 2) - distance
        pass

    def handle_phase_combat(self, event):
        pass

    def handle_phase_ranged(self, event):
        # Execute ranged attack orders
        if isinstance(self.current_order, RangedAttackOrder):
            if self.is_contested():
                # Can't conduct a ranged attack if there's an enemy on our tile
                publish_game_event(E_ORDER_CANCELED, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team
                })

                Managers.combat_logger.log_failed_order_execution(self, self.current_order)

                # Abort the order
                self.current_order = None
            else:
                publish_game_event(E_UNIT_RANGED_ATTACK, {
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
                publish_game_event(E_UPGRADE_BUILT, {
                    'team': self.team,
                    'new_upgrade_type': self.current_order.new_upgrade_type
                })

                Managers.combat_logger.log_successful_order_execution(self, self.current_order)

                # Deduct upgrade price
                Managers.team_manager.deduct_resources(self.team, base_upgrades[self.current_order.new_upgrade_type]["upgrade_price"])

                # Pop orders once they're executed
                self.current_order = None

    # Handle menu events concerning us
    def handle_menu_option(self, event):
        if event.option == MENU_MOVE:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': Managers.team_manager.attr(self.team, self.piece_type, Attribute.MOVEMENT_RANGE),
                'movement_type': Managers.team_manager.attr(self.team, self.piece_type, Attribute.MOVEMENT_TYPE),
                'team': self.team,
                'option': event.option
            })
        elif event.option == MENU_RANGED_ATTACK:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': Managers.team_manager.attr(self.team, self.piece_type, Attribute.MIN_RANGE),
                'max_range': Managers.team_manager.attr(self.team, self.piece_type, Attribute.MAX_RANGE),
                'movement_type': None,
                'team': self.team,
                'option': event.option
            })
        elif event.option == MENU_BUILD_PIECE:
            # Open the build menu and allow selecting a buildable piece
            publish_game_event(E_OPEN_BUILD_MENU, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'options': self.get_valid_buildable_pieces()
            })
        elif event.option in PieceType:
            # Attempting to build something, so open the tile selection
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': 1,
                'movement_type': Managers.team_manager.attr(self.team, event.option, Attribute.MOVEMENT_TYPE),
                'team': self.team,
                'option': event.option
            })
        elif event.option == MENU_PURCHASE_UPGRADE:
            # Open the build menu and allow selecting an upgrade to purchase
            publish_game_event(E_OPEN_UPGRADE_MENU, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'options': self.get_valid_purchaseable_upgrades()
            })
        else:
            self.set_order(event)

    # Save orders to this piece
    def set_order(self, event):
        if event.option == MENU_MOVE:
            self.current_order = MoveOrder(event.dx, event.dy)
        elif event.option == MENU_RANGED_ATTACK:
            self.current_order = RangedAttackOrder(event.dx, event.dy)
        elif event.option in PieceType:
            self.current_order = BuildOrder(event.dx, event.dy, event.option)
        elif event.option in UpgradeType:
            self.current_order = UpgradeOrder(event.option)
        elif event.option == MENU_CANCEL_ORDER:
            self.current_order = None
        else:
            self.current_order = None

    # Handle tile selection events concerning us
    def handle_tile_selection(self, event):
        self.set_order(event)

    def step(self, event):
        super().step(event)

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.step(event)

        # Check if we're in conflict
        self.in_conflict = Managers.turn_manager.phase == BattlePhase.ORDERS and \
                           len(Managers.piece_manager.get_enemy_pieces_at(self.gx, self.gy, self.team)) > 0

        # React to phase changes
        if is_event_type(event, START_PHASE_EXECUTE_BUILD):
            self.handle_phase_build(event)
        elif is_event_type(event, START_PHASE_EXECUTE_MOVE):
            self.handle_phase_move(event)
        elif is_event_type(event, START_PHASE_EXECUTE_COMBAT):
            self.handle_phase_combat(event)
        elif is_event_type(event, START_PHASE_EXECUTE_RANGED):
            self.handle_phase_ranged(event)
        elif is_event_type(event, START_PHASE_EXECUTE_SPECIAL):
            self.handle_phase_special(event)

        # Handle start of orders phase, if necessary
        if is_event_type(event, START_PHASE_ORDERS):
            self.handle_phase_orders(event)
        # Handle start of turn
        elif is_event_type(event, START_PHASE_START_TURN):
            self.handle_phase_start_turn(event)
        # Conduct cleanup when prompted
        elif is_event_type(event, E_CLEANUP):
            self.cleanup()
        # Catch selection events and open the orders menu
        elif is_event_type(event, E_SELECT):
            available_actions = self.get_available_actions()

            if event.gx == self.gx and event.gy == self.gy and \
                    event.team == self.team and not event.selecting_movement and len(available_actions) > 0:
                publish_game_event(E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'options': available_actions
                })
        # Catch menu events and set orders if they don't require tile selection or a submenu
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_menu_option(event)
        # Catch tile selection events and set orders involving tile selection
        elif is_event_type(event, E_SELECT_TILE) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_tile_selection(event)

        if self.team == Managers.player_manager.active_team:
            if event.type == KEYDOWN and event.key in KB_MENU2:
                self.previewing_order = True
            elif event.type == KEYUP and event.key in KB_MENU2:
                self.previewing_order = False

    # Render a preview of the piece's current orders.
    def preview_order(self, game_screen):
        if self.current_order:
            if isinstance(self.current_order, MoveOrder):
                target_sprite = self.get_sprite().copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.dx * GRID_WIDTH,
                                                 self.current_order.dy * GRID_HEIGHT))
            elif isinstance(self.current_order, RangedAttackOrder):
                target_sprite = spr_target[self.team].copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.tx * GRID_WIDTH,
                                                 self.current_order.ty * GRID_HEIGHT))
            elif isinstance(self.current_order, BuildOrder):
                target_sprite = spr_pieces[self.team][self.current_order.new_piece_type].copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.current_order.tx * GRID_WIDTH,
                                                 self.current_order.ty * GRID_HEIGHT))
            elif isinstance(self.current_order, UpgradeOrder):
                target_sprite = spr_upgrade_icons[self.team][self.current_order.new_upgrade_type].copy()
                target_sprite.set_alpha(128)
                game_screen.blit(target_sprite, (self.gx * GRID_WIDTH,
                                                 self.gy * GRID_HEIGHT))

    # Ask the Unit to render itself
    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        xoffset = 0
        yoffset = 0

        if self.in_conflict:
            if self.team == Team.RED:
                xoffset = -3
                yoffset = -3
            else:
                xoffset = 3
                yoffset = 3

        # Render the unit
        game_screen.blit(self.get_sprite(),
                         (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset))

        # Render order flag
        if self.current_order and Managers.player_manager.active_team == self.team:
            game_screen.blit(spr_order_flags[self.current_order.name],
                             (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset + 16))

        # Render HP flag
        displayable_hp = int(ceil(self.hp / Managers.team_manager.attr(self.team, self.piece_type, Attribute.MAX_HP) * 10))

        if 0 < displayable_hp * 10 < Managers.team_manager.attr(self.team, self.piece_type, Attribute.MAX_HP):
            game_screen.fill(clear_color[self.team],
                             (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16, 8, 8))
            game_screen.blit(spr_digit_icons[self.team][displayable_hp],
                             (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16))

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.render(game_screen, ui_screen)

        if self.previewing_order:
            self.preview_order(game_screen)
