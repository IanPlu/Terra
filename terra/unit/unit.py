from terra.settings import *
from terra.constants import *
from terra.engine.gameobject import GameObject
from terra.unit.orders import *
from terra.util.drawingutil import get_nine_slice_sprites
from terra.event import *
from terra.map import MovementType


default_sprite = {
    Team.RED: pygame.image.load("resources/sprites/units/Colonist.png"),
    Team.BLUE: pygame.image.load("resources/sprites/units/Colonist-2.png")
}

# Additional data rendered over the unit, like HP, Orders, etc.
# Each one gets sliced and rendered separately.
order_flags_base = pygame.image.load("resources/sprites/units/OrderFlags.png")
hp_flags_base = pygame.image.load("resources/sprites/units/HPFlags.png")

order_flags = get_nine_slice_sprites(order_flags_base, 8)
hp_flags = get_nine_slice_sprites(hp_flags_base, 8)

translated_order_flags = {
    MENU_CANCEL_ORDER: order_flags[0],
    MENU_MOVE: order_flags[1],
    MENU_RANGED_ATTACK: order_flags[2]
}


# A single unit on the map.
class Unit(GameObject):
    # Create a new Unit at the provided grid coordinates for the specified team
    def __init__(self, army, battle, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__()
        self.battle = battle
        self.game_map = game_map
        self.army = army
        self.team = team
        self.gx = gx
        self.gy = gy

        # Overrideable unit variables. Subclasses of Unit should override this.
        self.max_hp = 10                            # Units start at max HP and can't be healed past this number.
        self.attack = 0                             # How much damage base the unit does in melee combat.
        self.ranged_attack = 0                      # How much damage base the unit does when conducting ranged attacks.
        self.min_range = 0                          # Minimum range that a ranged attack can hit.
        self.max_range = 0                          # Maximum range that a ranged attack can hit.
        self.movement_type = MovementType.GROUND    # Movement type. Affects what tiles it can traverse.
        self.movement_range = 0                     # How far the unit can move in one turn.
        self.sprite = default_sprite

        self.hp = self.max_hp
        self.current_order = None
        self.in_conflict = False

        self.tile_selection = None

    def __str__(self):
        return "{} {} at tile ({}, {})".format(self.team, self.__class__.__name__, self.gx, self.gy)

    def get_available_actions(self):
        actions = []
        if self.movement_range > 0:
            actions.append(MENU_MOVE)
        if self.ranged_attack > 0 and not self.in_conflict:
            actions.append(MENU_RANGED_ATTACK)

        actions.append(MENU_CANCEL_ORDER)

        return actions

    def step(self, event):
        super().step(event)

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.step(event)

        # Check if we're in conflict
        self.in_conflict = self.battle.phase == BattlePhase.ORDERS and \
                           len(self.army.get_enemy_units_at(self.gx, self.gy, self.team)) > 0

        # Carry out our orders when appropriate
        self.execute_order(event)

        # Conduct cleanup when prompted
        if is_event_type(event, E_CLEANUP_UNITS):
            self.cleanup()

        # Catch selection events and open the orders menu
        elif is_event_type(event, E_SELECT):
            if event.gx == self.gx and event.gy == self.gy and \
                    event.team == self.team and not event.selecting_movement:
                publish_game_event(E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'options': self.get_available_actions()
                })

        # Catch menu events and set orders if they don't require tile selection
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_menu_option(event)

        # Catch tile selection events and set movement or ranged attack orders
        elif is_event_type(event, E_SELECT_TILE) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.handle_tile_selection(event)

    def handle_menu_option(self, event):
        if event.option == MENU_MOVE:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': 1,
                'max_range': self.movement_range,
                'game_map': self.game_map,
                'movement_type': self.movement_type,
                'team': self.team,
                'army': self.army,
                'option': event.option
            })
        elif event.option == MENU_RANGED_ATTACK:
            publish_game_event(E_OPEN_TILE_SELECTION, {
                'gx': self.gx,
                'gy': self.gy,
                'min_range': self.min_range,
                'max_range': self.max_range,
                'game_map': self.game_map,
                'movement_type': None,
                'team': self.team,
                'army': self.army,
                'option': event.option
            })
        else:
            self.set_order(event)

    def handle_tile_selection(self, event):
        if event.option == MENU_MOVE:
            self.set_order(event)
        elif event.option == MENU_RANGED_ATTACK:
            self.set_order(event)

    def set_order(self, event):
        order = None
        if event.option == MENU_MOVE:
            order = MoveOrder(self, event.option, event.dx, event.dy)
        elif event.option == MENU_RANGED_ATTACK:
            order = RangedAttackOrder(self, event.option, event.dx, event.dy)
        elif event.option == MENU_CANCEL_ORDER:
            order = None

        self.current_order = order

    def execute_order(self, event):
        if self.current_order:
            if is_event_type(event, START_PHASE_EXECUTE_MOVE) and isinstance(self.current_order, MoveOrder):
                publish_game_event(E_UNIT_MOVED, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'dx': self.current_order.dx,
                    'dy': self.current_order.dy
                })

                self.gx = self.current_order.dx
                self.gy = self.current_order.dy

                # Pop orders once they're executed
                self.current_order = None
            elif is_event_type(event, START_PHASE_EXECUTE_RANGED) and isinstance(self.current_order, RangedAttackOrder):
                publish_game_event(E_UNIT_RANGED_ATTACK, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'team': self.team,
                    'tx': self.current_order.tx,
                    'ty': self.current_order.ty
                })

                # Pop orders once they're executed
                self.current_order = None

    def cleanup(self):
        if self.hp <= 0:
            publish_game_event(E_UNIT_DEAD, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team
            })

    # Ask the Unit to render itself
    def render(self, screen):
        super().render(screen)

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
        screen.blit(self.sprite[self.team],
                    (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset))

        # Render order flag
        if self.current_order:
            screen.blit(translated_order_flags[self.current_order.name],
                        (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset + 16))

        # Render HP flag
        if 0 < self.hp < self.max_hp:
            screen.blit(hp_flags[self.hp - 1],
                        (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16))

        # Allow our tile selection UI to function if alive
        if self.tile_selection:
            self.tile_selection.render(screen)
