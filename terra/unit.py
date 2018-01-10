import pygame
from terra.settings import *
from terra.constants import *
from terra.gameobject import GameObject
from terra.orders import *
from terra.drawingutil import get_nine_slice_sprites
from enum import Enum
import random


class UnitType(Enum):
    COLONIST = 0
    TROOPER = 1


# TODO: Build palette swaps rather than hard-coded team sprites
# Unit graphics
unit_sprites = {
    Team.RED: {
        UnitType.COLONIST: pygame.image.load("resources/sprites/units/Colonist.png"),
        UnitType.TROOPER: pygame.image.load("resources/sprites/units/Trooper.png")
    },
    Team.BLUE: {
        UnitType.COLONIST: pygame.image.load("resources/sprites/units/Colonist-2.png"),
        UnitType.TROOPER: pygame.image.load("resources/sprites/units/Trooper-2.png")
    }
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
    def __init__(self, game_map, unit_type=UnitType.COLONIST, team=Team.RED, gx=0, gy=0):
        super().__init__()
        self.game_map = game_map
        self.unit_type = unit_type
        self.team = team
        self.gx = gx
        self.gy = gy

        self.current_order = None
        self.hp = random.randint(1, 10)

    def step(self, event):
        super().step(event)

        # When the Execute Orders phase begins, carry out our Order
        if event.type == E_EXECUTE_ORDERS and self.current_order:
            self.execute_order()
        # Catch selection events and open the orders menu
        elif event.type == E_SELECT:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                pygame.event.post(pygame.event.Event(E_OPEN_MENU, {
                    'gx': self.gx,
                    'gy': self.gy,
                    'options': [
                        MENU_MOVE_N,
                        MENU_MOVE_E,
                        MENU_MOVE_S,
                        MENU_MOVE_W,
                        MENU_CANCEL_ORDER
                    ]
                }))
        elif event.type == E_CLOSE_MENU and event.option:
            if event.gx == self.gx and event.gy == self.gy and event.team == self.team:
                self.set_order(event.option)
        elif event.type == KEYDOWN and event.key in KB_DEBUG3:
            self.hp -= 1
            if self.hp < 0:
                self.hp = 10

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
                self.gx = self.current_order.dx
                self.gy = self.current_order.dy

            # Pop orders once they're executed
            self.current_order = None

    # Ask the Unit to render itself
    def render(self, screen):
        super().render(screen)
        # Render the unit
        screen.blit(unit_sprites[self.team][self.unit_type],
                    (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        # Render order flag
        if self.current_order:
            screen.blit(translated_order_flags[self.current_order.name],
                        (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT + 16))
        else:
            screen.blit(translated_order_flags[MENU_CANCEL_ORDER],
                        (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT + 16))

        # Render HP flag
        if 0 < self.hp < 10:
            screen.blit(hp_flags[self.hp - 1],
                        (self.gx * GRID_WIDTH + 16, self.gy * GRID_HEIGHT + 16))
