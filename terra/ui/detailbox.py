import pygame

from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradetype import UpgradeType
from terra.engine.gameobject import GameObject
from terra.event.event import EventType, publish_game_event
from terra.managers.managers import Managers
from terra.piece.attribute import Attribute
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, spr_upgrade_icons, spr_order_options, clear_color, spr_textbox, \
    spr_piece_attribute_icons, dark_color
from terra.strings import get_text, get_multiline_text, piece_name_strings, upgrade_name_strings, \
    menu_option_strings, menu_help_strings, attribute_value_strings
from terra.util.drawingutil import draw_nine_slice_sprite, draw_text

subgrid_size = 8
subgrid_width = 24
subgrid_height = 24


# A UI box showing a long text description of a piece or upgrade.
class DetailBox(GameObject):
    def __init__(self, team, target):
        super().__init__()

        self.team = team
        self.target = target

        self.x = (RESOLUTION_WIDTH - subgrid_width * subgrid_size) // 2
        self.y = (RESOLUTION_HEIGHT - subgrid_height * subgrid_size) // 2 - 16

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.close)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.close)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.close)

    def close(self):
        publish_game_event(EventType.E_CLOSE_DETAILBOX, {})

    # Return a surface containing a single attribute with icon and value text
    def render_attribute(self, attribute):
        surface = pygame.Surface((96, 12), pygame.SRCALPHA, 32)
        surface.blit(spr_piece_attribute_icons[self.team][attribute], (0, 0))

        value = Managers.team_manager.attr(self.team, self.target, attribute)
        if attribute in [Attribute.ARCHETYPE, Attribute.MOVEMENT_TYPE]:
            surface.blit(get_text(attribute_value_strings, value, light=False), (14, 0))
        else:
            surface.blit(draw_text(str(value), dark_color), (14, 0))

        return surface

    # Display the provided piece type's attributes with icons and text
    def render_piece_attributes(self, ui_screen):
        attributes = [self.render_attribute(attribute) for attribute in [
            Attribute.ARCHETYPE, Attribute.MAX_HP, Attribute.ATTACK, Attribute.ARMOR, Attribute.MIN_RANGE,
            Attribute.MAX_RANGE, Attribute.MOVEMENT_TYPE, Attribute.MOVEMENT_RANGE
        ]]

        x = 0
        y = 0
        y_limit = 52
        for attribute in attributes:
            ui_screen.blit(attribute, (self.x + 4 + x, self.y + 32 + y))
            y += 13
            if y >= y_limit:
                y = 0
                x += 60

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        ui_screen.blit(draw_nine_slice_sprite(spr_textbox[self.team], subgrid_size,
                                                subgrid_width, subgrid_height + 1), (self.x, self.y))

        y_offset = 0

        if self.target in PieceType:
            # Render piece icons
            ui_screen.fill(clear_color[self.team], (self.x + 4, self.y + 12, 16, 16))
            ui_screen.blit(spr_pieces[self.team][self.target], (self.x + 2, self.y + 8))

            ui_screen.blit(get_text(piece_name_strings, self.target, light=False), (self.x + 24, self.y + 16))

            self.render_piece_attributes(ui_screen)
            y_offset = 52

        elif self.target in UpgradeType:
            # Render upgrade icons
            ui_screen.blit(spr_upgrade_icons[self.team][self.target], (self.x + 4, self.y + 8))

            ui_screen.blit(get_text(upgrade_name_strings, self.target, light=False), (self.x + 32, self.y + 16))
        else:
            # Render menu option icons
            ui_screen.blit(spr_order_options[self.team][self.target], (self.x + 4, self.y + 8))

            ui_screen.blit(get_text(menu_option_strings, self.target, light=False), (self.x + 32, self.y + 16))

        # Render the description text
        ui_screen.blit(get_multiline_text(menu_help_strings, self.target, light=False,
                                            width=subgrid_width * subgrid_size - 8),
                         (self.x + 4, self.y + 40 + y_offset))
