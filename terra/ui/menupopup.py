from terra.constants import GRID_WIDTH, GRID_HEIGHT, RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.menu.menu import Menu
from terra.menu.option import contestable_options
from terra.piece.attribute import Attribute
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, clear_color, spr_digit_icons, spr_upgrade_icons, \
    spr_resource_icon, spr_order_options, spr_menu_option_item_background, light_team_color, spr_contested_icon
from terra.strings import menu_option_strings, piece_name_strings, upgrade_name_strings, get_text
from terra.ui.detailbox import DetailBox
from terra.util.drawingutil import draw_resource_count

# Constants for rendering textboxes
option_height = 24
menu_edge_buffer = 24


# A menu popup containing multiple selectable menu options
class MenuPopup(Menu):
    def __init__(self, cursor, team, tx=None, ty=None, options=None, centered=False):
        self.cursor = cursor
        self.team = team
        self.detailbox = None

        self.options = options

        self.width = 120
        # If any of our options need to show a price display, widen the menu to accommodate the price display
        for option in options:
            if option in UpgradeType or option in PieceType:
                self.width = 144

        max_displayable_options = 4
        height = option_height * min(len(options), max_displayable_options)

        # Tile the menu is for
        self.tx = tx
        self.ty = ty

        # Rendered coords
        if centered:
            x = (RESOLUTION_WIDTH - self.width) // 2
            y = (RESOLUTION_HEIGHT - height) // 2
        elif self.tx is not None and self.ty is not None:
            x = (self.tx + 1 - self.cursor.camera_x // GRID_WIDTH) * GRID_WIDTH
            y = (self.ty - self.cursor.camera_y // GRID_HEIGHT) * GRID_HEIGHT

            # Avoid collisions with edges of the screen
            if x > RESOLUTION_WIDTH - self.width - menu_edge_buffer:
                x -= self.width + menu_edge_buffer
            if y > RESOLUTION_HEIGHT - height - menu_edge_buffer:
                y -= height - menu_edge_buffer
        else:
            x = 0
            y = 0

        super().__init__(num_options=len(options),
                         max_displayable_options=max_displayable_options,
                         displayable_buffer=1,
                         root_x=x,
                         root_y=y,
                         width=self.width,
                         option_height=24)

    def destroy(self):
        super().destroy()
        if self.detailbox:
            self.detailbox.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_CLOSE_DETAILBOX, self.close_detailbox)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.cancel)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.show_detailbox)

    def is_accepting_input(self):
        return self.get_manager(Manager.PLAYER).active_team == self.team and not self.detailbox

    def confirm(self):
        super().confirm()
        selected_option = self.options[self.menu_pos]

        publish_game_event(EventType.E_CLOSE_MENU, {
            'gx': self.tx,
            'gy': self.ty,
            'option': selected_option,
            'team': self.team
        })

    def cancel(self):
        super().cancel()
        publish_game_event(EventType.E_CLOSE_MENU, {
            'gx': self.tx,
            'gy': self.ty,
            'option': None,
            'team': self.team
        })

    def show_detailbox(self):
        self.detailbox = DetailBox(self.team, self.options[self.menu_pos])

    def close_detailbox(self, event):
        if self.detailbox:
            self.detailbox.destroy()
            self.detailbox = None

    # Return true if the chosen menu option is at risk of being contested.
    # If this menu isn't for a specific tile, this always returns False.
    def is_option_contested(self, option):
        if self.tx and self.ty:
            piece = self.get_manager(Manager.PIECE).get_piece_at(self.tx, self.ty, self.team)
            if piece:
                return piece.is_contested()
            else:
                # No piece, so can't be contested
                return False
        else:
            return False

    def step(self, event):
        super().step(event)

        # Allow the detail box to run if it's alive
        if self.detailbox:
            self.detailbox.step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.detailbox:
            self.detailbox.render(game_screen, ui_screen)
        else:
            row_y = 0
            displayable_options = self.options[self.menu_min:self.menu_max]

            # Draw a scrollbar if necessary
            if self.should_show_scroll_bar(self.max_displayable_options, self.num_options):
                width = 6
                height = self.option_height * min(self.max_displayable_options, self.num_options)
                ui_screen.blit(self.draw_scroll_bar(width, height, self.max_displayable_options, self.menu_min, self.num_options),
                                 (self.root_x + self.width, self.root_y))

            for option in displayable_options:
                is_selected = self.menu_pos == self.options.index(option)
                x_offset = 0 if is_selected else 4

                # Draw the row
                position_x, position_y = self.root_x, \
                                         self.root_y + row_y * self.option_height
                box = self.draw_menu_box(self.width - x_offset, self.option_height,
                                         background=light_team_color if is_selected else clear_color, team=self.team)
                ui_screen.blit(box, (position_x + x_offset, position_y))

                if option in PieceType:
                    # Render buildable pieces
                    ui_screen.blit(spr_menu_option_item_background[self.team], (self.root_x + x_offset, self.root_y + row_y * option_height))

                    ui_screen.blit(spr_pieces[self.team][option].subsurface(0, 0, 24, 24), (self.root_x + x_offset, self.root_y + row_y * option_height))
                    ui_screen.blit(get_text(piece_name_strings, option, light=True), (self.root_x + 29, self.root_y + 8 + row_y * option_height))

                    # if self.option_pos == row_y + self.option_min:
                    ui_screen.blit(draw_resource_count(spr_resource_icon, spr_digit_icons, self.team,
                                                       self.get_manager(Manager.TEAM).attr(self.team, option, Attribute.PRICE)),
                                   (self.root_x + self.width - 20,
                                    self.root_y + row_y * option_height))

                    row_y += 1
                elif option in UpgradeType:
                    # Render purchaseable upgrades
                    ui_screen.blit(spr_upgrade_icons[self.team][option], (self.root_x + x_offset, self.root_y + row_y * option_height))
                    ui_screen.blit(get_text(upgrade_name_strings, option, light=True), (self.root_x + 29, self.root_y + 8 + row_y * option_height))

                    # if self.option_pos == row_y + self.option_min:
                    ui_screen.blit(draw_resource_count(spr_resource_icon, spr_digit_icons, self.team,
                                                       base_upgrades[option][UpgradeAttribute.UPGRADE_PRICE]),
                                   (self.root_x + self.width - 24,
                                    self.root_y + row_y * option_height))

                    row_y += 1
                else:
                    # Render menu option icons
                    ui_screen.blit(spr_order_options[self.team][option], (self.root_x + x_offset, self.root_y + row_y * option_height))

                    # Render 'contested' indicator if necessary
                    if option in contestable_options and self.is_option_contested(option):
                        ui_screen.blit(spr_contested_icon[self.team], (self.root_x + x_offset, self.root_y + row_y * option_height))

                    ui_screen.blit(get_text(menu_option_strings, option, light=True), (self.root_x + 29, self.root_y + 8 + row_y * option_height))
                    row_y += 1
