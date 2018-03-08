from pygame.constants import KEYDOWN, MOUSEMOTION, MOUSEBUTTONDOWN

from terra.constants import GRID_WIDTH, GRID_HEIGHT, RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.economy.upgrades import UpgradeType, base_upgrades
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_UP, KB_DOWN, KB_CONFIRM, KB_CANCEL, KB_SCROLL_UP, KB_SCROLL_DOWN, KB_MENU, KB_MENU2
from terra.managers.managers import Managers
from terra.piece.pieceattributes import Attribute
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_cursor, spr_textbox, spr_pieces, clear_color, spr_digit_icons, \
    spr_upgrade_icons, spr_resource_icon_carbon_small, spr_resource_icon_minerals_small, spr_resource_icon_gas_small, \
    spr_order_options
from terra.settings import SCREEN_SCALE
from terra.strings import menu_option_strings, piece_name_strings, upgrade_name_strings, get_text
from terra.ui.detailbox import DetailBox
from terra.util.drawingutil import draw_nine_slice_sprite, draw_small_resource_count
from terra.util.mathutil import clamp

# Constants for rendering textboxes
subgrid_size = 8
option_height = 24
max_displayable_options = 4
displayable_buffer = 1


# A menu popup containing multiple selectable menu options
class MenuPopup(GameObject):
    def __init__(self, cursor, tx, ty, team, options=None, centered=False):
        super().__init__()

        self.cursor = cursor
        self.team = team
        self.detailbox = None

        self.options = options
        self.num_options = len(options)

        self.subgrid_width = 12
        # If any of our options need to show a price display, widen the menu to accommodate the price display
        for option in options:
            if option in UpgradeType or option in PieceType:
                self.subgrid_width = 15

        self.subgrid_height = 3 * min(self.num_options, max_displayable_options)

        self.option_pos = 0
        self.option_min = 0
        self.option_max = max_displayable_options

        # Tile the menu is for
        self.tx = tx
        self.ty = ty

        # Rendered coords
        if centered:
            self.x = (RESOLUTION_WIDTH - self.subgrid_width * subgrid_size) // 2
            self.y = (RESOLUTION_HEIGHT - self.subgrid_height * subgrid_size) // 2
        else:
            self.x = (self.tx + 1 - self.cursor.camera_x // GRID_WIDTH) * GRID_WIDTH
            self.y = (self.ty - self.cursor.camera_y // GRID_HEIGHT) * GRID_HEIGHT

        # Avoid collisions with edges of the screen
        if self.x > RESOLUTION_WIDTH - self.subgrid_width * subgrid_size:
            self.x -= self.subgrid_width * subgrid_size + 24
        if self.y > RESOLUTION_HEIGHT - self.subgrid_height * subgrid_size * 2:
            self.y -= self.subgrid_height * subgrid_size - 12

    def confirm(self):
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
        self.normalize_cursor_pos()

    def cursor_down(self):
        self.option_pos += 1
        self.normalize_cursor_pos()

    # Clamp the cursor position to within possible bounds. Scroll the menu if necessary.
    def normalize_cursor_pos(self):
        if self.option_pos < 0:
            self.option_pos = self.num_options - 1
        elif self.option_pos > self.num_options - 1:
            self.option_pos = 0

        # Scroll the displayable area
        if self.option_pos < self.option_min + displayable_buffer:
            self.option_min = self.option_pos - displayable_buffer
        if self.option_pos >= self.option_max - displayable_buffer:
            self.option_min = self.option_pos + displayable_buffer - max_displayable_options + 1

        # Clamp to the bounds of the option list
        self.option_min = clamp(self.option_min, 0, self.num_options - max_displayable_options)
        self.option_max = self.option_min + max_displayable_options

    # Return true if the mouse coordinates are within the boundaries of our menu window
    def is_mouse_in_menu_bounds(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mousex = int(mouse_x / SCREEN_SCALE)
        mousey = int(mouse_y / SCREEN_SCALE)

        min_x = self.x
        min_y = self.y + 8
        max_x = min_x + self.subgrid_width * subgrid_size
        max_y = min_y + self.subgrid_height * subgrid_size

        return min_x < mousex < max_x and min_y < mousey < max_y

    def set_cursor_pos_to_mouse_coords(self):
        self.option_pos = (int(pygame.mouse.get_pos()[1] / SCREEN_SCALE) - self.y - 8) \
                          // option_height + self.option_min

    def scroll_option_up(self):
        self.option_min = clamp(self.option_min - 1, 0, self.num_options - max_displayable_options)
        self.option_max = self.option_min + max_displayable_options

    def scroll_option_down(self):
        self.option_min = clamp(self.option_min + 1, 0, self.num_options - max_displayable_options)
        self.option_max = self.option_min + max_displayable_options

    def show_detailbox(self):
        self.detailbox = DetailBox(self.cursor, self.team, self.options[self.option_pos])

    def close_detailbox(self):
        self.detailbox = None

    def step(self, event):
        super().step(event)

        # Allow the detail box to run if it's alive
        if self.detailbox:
            self.detailbox.step(event)

            # Only listen for events that can close the box
            if event.type == KEYDOWN and (event.key in KB_MENU2 or event.key in KB_CANCEL or event.key in KB_MENU):
                self.close_detailbox()
            elif event.type == MOUSEBUTTONDOWN and (event.button in KB_MENU2 or event.button in KB_CANCEL or event.button in KB_MENU):
                self.close_detailbox()
        else:
            if event.type == KEYDOWN:
                if event.key in KB_UP:
                    self.cursor_up()
                elif event.key in KB_DOWN:
                    self.cursor_down()
                elif event.key in KB_CONFIRM:
                    self.confirm()
                elif event.key in KB_CANCEL or event.key in KB_MENU:
                    self.cancel()
                elif event.key in KB_MENU2:
                    self.show_detailbox()
            if event.type == MOUSEMOTION and self.is_mouse_in_menu_bounds():
                self.set_cursor_pos_to_mouse_coords()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CANCEL:
                    self.cancel()
                elif self.is_mouse_in_menu_bounds():
                    if event.button in KB_CONFIRM:
                        self.confirm()
                    elif event.button in KB_SCROLL_UP:
                        self.scroll_option_up()
                        self.set_cursor_pos_to_mouse_coords()
                    elif event.button in KB_SCROLL_DOWN:
                        self.scroll_option_down()
                        self.set_cursor_pos_to_mouse_coords()
                    elif event.button in KB_MENU2:
                        self.show_detailbox()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.detailbox:
            self.detailbox.render(game_screen, ui_screen)
        else:
            ui_screen.blit(draw_nine_slice_sprite(spr_textbox[self.team], subgrid_size,
                                                    self.subgrid_width, self.subgrid_height + 1), (self.x, self.y))

            row_y = 0
            displayable_options = self.options[self.option_min:self.option_max]
            for option in displayable_options:
                if option in PieceType:
                    # Render buildable pieces
                    ui_screen.fill(clear_color[self.team], (self.x + 4, self.y + 12 + row_y * option_height, 16, 16))

                    ui_screen.blit(spr_pieces[self.team][option], (self.x, self.y + 8 + row_y * option_height))
                    ui_screen.blit(get_text(piece_name_strings, option, light=False), (self.x + 25, self.y + 16 + row_y * option_height))

                    if self.option_pos == row_y + self.option_min:
                        resource_price = draw_small_resource_count([spr_resource_icon_carbon_small,
                                                                    spr_resource_icon_minerals_small,
                                                                    spr_resource_icon_gas_small],
                                                                   spr_digit_icons, clear_color, self.team,
                                                                   Managers.team_manager.attr(self.team, option, Attribute.PRICE))
                        ui_screen.blit(resource_price, (self.x + self.subgrid_width * subgrid_size - 26,
                                                          self.y + row_y * option_height + subgrid_size))

                    row_y += 1
                elif option in UpgradeType:
                    # Render purchaseable upgrades
                    ui_screen.blit(spr_upgrade_icons[self.team][option], (self.x, self.y + 8 + row_y * option_height))
                    ui_screen.blit(get_text(upgrade_name_strings, option, light=False), (self.x + 25, self.y + 16 + row_y * option_height))

                    if self.option_pos == row_y + self.option_min:
                        resource_price = draw_small_resource_count([spr_resource_icon_carbon_small,
                                                                    spr_resource_icon_minerals_small,
                                                                    spr_resource_icon_gas_small],
                                                                   spr_digit_icons, clear_color, self.team,
                                                                   base_upgrades[option]["upgrade_price"])
                        ui_screen.blit(resource_price, (self.x + self.subgrid_width * subgrid_size - 26,
                                                          self.y + row_y * option_height + subgrid_size))

                    row_y += 1
                else:
                    # Render menu option icons
                    ui_screen.blit(spr_order_options[self.team][option], (self.x, self.y + 8 + row_y * option_height))
                    ui_screen.blit(get_text(menu_option_strings, option, light=False), (self.x + 25, self.y + 16 + row_y * option_height))
                    row_y += 1

            # Render the option cursor
            ui_screen.blit(spr_cursor[self.team], (self.x, self.y + 8 + (self.option_pos - self.option_min) * option_height))
