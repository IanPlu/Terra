from terra.settings import *
from terra.constants import *
from terra.gameobject import GameObject
from terra.unit.orders import *
from terra.drawingutil import get_nine_slice_sprites
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
    MENU_MOVE_N: order_flags[1],
    MENU_MOVE_E: order_flags[2],
    MENU_MOVE_S: order_flags[3],
    MENU_MOVE_W: order_flags[4]
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
        self.sprite = default_sprite

        self.hp = self.max_hp
        self.current_order = None
        self.in_conflict = False

    def __str__(self):
        return "{} {} at tile ({}, {})".format(self.team, self.__class__.__name__, self.gx, self.gy)

    def step(self, event):
        super().step(event)

        # Check if we're in conflict
        self.in_conflict = self.battle.phase == BattlePhase.ORDERS and \
                           len(self.army.get_enemy_units_at(self.gx, self.gy, self.team)) > 0

        # Carry out our orders when appropriate
        if is_event_type(event, START_PHASE_EXECUTE_MOVE) and self.current_order:
            self.execute_order()

        # Catch selection events and open the orders menu
        elif is_event_type(event, E_SELECT):
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                publish_game_event(E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'options': [
                        MENU_MOVE_N,
                        MENU_MOVE_E,
                        MENU_MOVE_S,
                        MENU_MOVE_W,
                        MENU_CANCEL_ORDER
                    ]
                })
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.set_order(event.option)
        elif event.type == KEYDOWN and event.key in KB_DEBUG3:
            self.hp -= 1
            if self.hp < 0:
                self.hp = self.max_hp

    def set_order(self, option):
        order = None
        if option == MENU_MOVE_N:
            order = MoveOrder(self, option, self.gx, self.gy - 1)
        elif option == MENU_MOVE_E:
            order = MoveOrder(self, option, self.gx + 1, self.gy)
        elif option == MENU_MOVE_S:
            order = MoveOrder(self, option, self.gx, self.gy + 1)
        elif option == MENU_MOVE_W:
            order = MoveOrder(self, option, self.gx - 1, self.gy)
        elif option == MENU_CANCEL_ORDER:
            order = None

        self.current_order = order

    def execute_order(self):
        if self.current_order:
            if isinstance(self.current_order, MoveOrder):
                # We trust MoveOrders to be valid. TODO: Rethink enforcing validity here too
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

    def cleanup(self):
        pass

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
        else:
            screen.blit(translated_order_flags[MENU_CANCEL_ORDER],
                        (self.gx * GRID_WIDTH + xoffset, self.gy * GRID_HEIGHT + yoffset + 16))

        # Render HP flag
        if 0 < self.hp < self.max_hp:
            screen.blit(hp_flags[self.hp - 1],
                        (self.gx * GRID_WIDTH + xoffset + 16, self.gy * GRID_HEIGHT + yoffset + 16))
