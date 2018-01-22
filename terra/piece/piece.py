from terra.engine.gameobject import GameObject
from terra.constants import Team, BattlePhase
from terra.resources.assets import spr_units, spr_order_flags, spr_digit_icons, clear_color
from terra.event import *
from terra.settings import *
from terra.piece.unit.unittype import UnitType


# Base object in play belonging to a player, like a unit or a building.
# They belong to a team and exist somewhere on the map.
# Pieces have HP and can accept and execute orders.
class Piece(GameObject):
    def __init__(self, piece_manager, team_manager, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__()
        self.battle = battle
        self.game_map = game_map
        self.team_manager = team_manager
        self.piece_manager = piece_manager
        self.team = team
        self.gx = gx
        self.gy = gy

        # Overrideable variables. Subclasses should override this.
        self.max_hp = 10
        self.attack = 0

        # Interpreted variables. Don't touch!
        self.hp = self.max_hp
        self.current_order = None
        self.in_conflict = False
        self.tile_selection = None

    def __str__(self):
        return "{} {} at tile ({}, {}) with {} HP" \
            .format(self.team.name, self.__class__.__name__, self.gx, self.gy, self.hp)

    def get_sprite(self):
        return spr_units[self.team][UnitType.UNIT]

    # Return a list of actions to show in the selection UI.
    def get_available_actions(self):
        return [MENU_CANCEL_ORDER]

    # Clean ourselves up at the end of phases, die as appropriate
    def cleanup(self):
        if self.hp <= 0:
            publish_game_event(E_PIECE_DEAD, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })
            self.on_death()

    # Do anything special on death
    def on_death(self):
        pass

    # Phase handlers. Other than the orders handler, these are only triggered when we have orders.
    def handle_phase_start_turn(self, event):
        pass

    def handle_phase_orders(self, event):
        pass

    def handle_phase_build(self, event):
        pass

    def handle_phase_move(self, event):
        pass

    def handle_phase_combat(self, event):
        pass

    def handle_phase_ranged(self, event):
        pass

    def handle_phase_special(self, event):
        pass

    # Handle menu events concerning us
    def handle_menu_option(self, event):
        pass

    def handle_tile_selection(self, event):
        pass

    def step(self, event):
        super().step(event)

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.step(event)

        # Check if we're in conflict
        self.in_conflict = self.battle.phase == BattlePhase.ORDERS and \
                           len(self.piece_manager.get_enemy_pieces_at(self.gx, self.gy, self.team)) > 0

        # React to phase changes when we have an order
        if self.current_order:
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
            if event.gx == self.gx and event.gy == self.gy and \
                    event.team == self.team and not event.selecting_movement:
                publish_game_event(E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'options': self.get_available_actions()
                })
        # Catch menu events and set orders if they don't require tile selection
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_menu_option(event)
        # Catch tile selection events and set orders involving tile selection
        elif is_event_type(event, E_SELECT_TILE) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_tile_selection(event)

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
        if self.current_order and self.battle.active_team == self.team:
            game_screen.blit(spr_order_flags[self.current_order.name],
                             (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset + 16))

        # Render HP flag
        if 0 < self.hp < self.max_hp:
            game_screen.fill(clear_color[self.team],
                             (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16, 8, 8))
            game_screen.blit(spr_digit_icons[self.team][int(self.hp / self.max_hp * 10)],
                             (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16))

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.render(game_screen, ui_screen)
