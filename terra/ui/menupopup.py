from pygame.constants import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN

from terra.constants import GRID_WIDTH, GRID_HEIGHT, RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_CONFIRM, KB_CANCEL
from terra.piece.piece import spr_order_flags
from terra.piece.pieceprice import piece_prices
from terra.resources.assets import spr_cursor, spr_textbox, spr_units, text_menu_option, text_unit_name, clear_color, \
    spr_resource_icon_carbon, spr_resource_icon_minerals, spr_resource_icon_gas, spr_digit_icons
from terra.settings import SCREEN_SCALE
from terra.team import Team
from terra.util.drawingutil import draw_nine_slice_sprite, draw_resource_count

# Constants for rendering textboxes
subgrid_size = 8
option_height = 24


# A menu popup containing multiple selectable menu options
class MenuPopup(GameObject):
    def __init__(self, cursor, tx=0, ty=0, team=Team.RED, options=None, buildable_units=None, centered=False):
        super().__init__()

        self.cursor = cursor
        self.team = team

        self.subgrid_width = 12
        self.subgrid_height = 3 * len(options)

        self.options = options
        self.num_options = len(options)
        self.buildable_units = buildable_units

        self.option_pos = 0

        # Tile the menu is for
        self.tx = tx
        self.ty = ty

        # Rendered coords
        if centered:
            self.x = (RESOLUTION_WIDTH - self.subgrid_width * subgrid_size) // 2 + self.cursor.camera_x
            self.y = (RESOLUTION_HEIGHT - self.subgrid_height * subgrid_size) // 2 + self.cursor.camera_y
        else:
            self.x = (self.tx + 1) * GRID_WIDTH
            self.y = self.ty * GRID_HEIGHT

        # Avoid collisions with edges of the screen
        if self.x > self.cursor.camera_x + RESOLUTION_WIDTH - self.subgrid_width * subgrid_size:
            self.x -= self.subgrid_width * subgrid_size + 24
        if self.y > self.cursor.camera_y + RESOLUTION_HEIGHT - self.subgrid_height * subgrid_size * 2:
            self.y -= self.subgrid_height * subgrid_size - 12

    def confirm(self):
        if self.buildable_units:
            selected_option = self.buildable_units[self.option_pos]
        else:
            selected_option = self.options[self.option_pos]

        publish_game_event(E_CLOSE_MENU, {
            'gx': self.tx,
            'gy': self.ty,
            'option': selected_option,
            'team': self.team
        })

    def cancel(self):
        publish_game_event(E_CLOSE_MENU, {
            'gx': self.tx,
            'gy': self.ty,
            'option': None,
            'team': self.team
        })

    def cursor_up(self):
        self.option_pos -= 1
        if self.option_pos < 0:
            self.option_pos = self.num_options - 1

    def cursor_down(self):
        self.option_pos += 1
        if self.option_pos > self.num_options - 1:
            self.option_pos = 0

    def step(self, event):
        super().step(event)

        if event.type == KEYDOWN:
            if event.key in KB_UP:
                self.cursor_up()
            elif event.key in KB_DOWN:
                self.cursor_down()
            elif event.key in KB_CONFIRM:
                self.confirm()
            elif event.key in KB_CANCEL:
                self.cancel()
        elif event.type == MOUSEMOTION:
            # Determine if the mouse is in the popup window
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mousex = int(mouse_x / SCREEN_SCALE + self.cursor.camera_x)
            mousey = int(mouse_y / SCREEN_SCALE + self.cursor.camera_y)

            min_x = self.x
            min_y = self.y + 8
            max_x = min_x + self.subgrid_width * subgrid_size
            max_y = min_y + self.subgrid_height * subgrid_size

            if min_x < mousex < max_x and min_y < mousey < max_y:
                # Determine where in the menu we are for the option pos
                self.option_pos = (mousey - min_y) // option_height
        elif event.type == MOUSEBUTTONDOWN:
            if event.button in KB_CONFIRM:
                self.confirm()
            elif event.button in KB_CANCEL:
                self.cancel()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        game_screen.blit(draw_nine_slice_sprite(spr_textbox[self.team], subgrid_size,
                                                self.subgrid_width, self.subgrid_height + 1),
                         (self.x, self.y))

        row_y = 0
        if self.buildable_units:
            # Render buildable units
            for buildable_unit in self.buildable_units:
                game_screen.fill(clear_color[self.team], (self.x + 2, self.y + 10 + row_y * option_height, 20, 20))
                game_screen.blit(spr_units[self.team][buildable_unit], (self.x, self.y + 8 + row_y * option_height))
                game_screen.blit(text_unit_name[buildable_unit], (self.x + 24, self.y + 16 + row_y * option_height))

                resource_price = draw_resource_count([spr_resource_icon_carbon, spr_resource_icon_minerals,
                                                      spr_resource_icon_gas], spr_digit_icons, self.team,
                                                     piece_prices[buildable_unit])
                game_screen.blit(resource_price, (self.x + self.subgrid_width * subgrid_size - 2,
                                                  self.y + row_y * option_height + subgrid_size))

                row_y += 1
        else:
            for option in self.options:
                # Render menu option icons
                game_screen.fill(clear_color[self.team], (self.x + 2, self.y + 10 + row_y * option_height, 20, 20))
                game_screen.blit(spr_order_flags[option], (self.x + 8, self.y + 16 + row_y * option_height))
                game_screen.blit(text_menu_option[option], (self.x + 24, self.y + 16 + row_y * option_height))
                row_y += 1

        # Render the option cursor
        game_screen.blit(spr_cursor[self.team], (self.x, self.y + 8 + self.option_pos * option_height))
