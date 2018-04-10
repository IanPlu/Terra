import pygame

from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.engine.gameobject import GameObject
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.piece.attribute import Attribute
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_pieces, spr_upgrade_icons, spr_order_options, clear_color, \
    spr_piece_attribute_icons, dark_color, light_color, spr_combat_icon, spr_build_icon
from terra.strings import get_text, get_multiline_text, piece_name_strings, upgrade_name_strings, \
    menu_option_strings, menu_help_strings, attribute_value_strings, attribute_label_strings, get_string, \
    formatted_strings
from terra.util.drawingutil import draw_text

subgrid_size = 8
subgrid_width = 24
subgrid_height = 24

piece_archetype_to_type = {
    PieceArchetype.WORKER: PieceType.COLONIST,
    PieceArchetype.GROUND: PieceType.TROOPER,
    PieceArchetype.RANGED: PieceType.RANGER,
    PieceArchetype.MOBILITY: PieceType.GHOST,
    PieceArchetype.GENERATOR: PieceType.GENERATOR,
    PieceArchetype.UTILITY: PieceType.TECHLAB,
}


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

    # Return a surface containing a single piece attribute with icon and value text
    def render_attribute(self, attribute):
        surface = pygame.Surface((96, 12), pygame.SRCALPHA, 32)
        surface.blit(spr_piece_attribute_icons[self.team][attribute], (0, 0))

        value = self.get_manager(Manager.TEAM).attr(self.team, self.target, attribute)
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

        return y_limit + 16

    def render_upgrade_attributes(self, ui_screen):
        upgrade = base_upgrades[self.target]

        y_offset = 24
        if upgrade.get(UpgradeAttribute.NEW_STAT):
            for piece_type, attributes in upgrade[UpgradeAttribute.NEW_STAT].items():
                for attribute in attributes:
                    # Draw the affected piece
                    ui_screen.blit(spr_pieces[self.team][piece_type].subsurface(0, 0, 24, 24), (self.x + 2, self.y + 8 + y_offset))

                    # Render the affected attribute + its new stat
                    text = get_string(attribute_label_strings, attribute)
                    value = upgrade[UpgradeAttribute.NEW_STAT][piece_type][attribute]
                    if not isinstance(value, bool):
                        text += " +" + str(value)

                    ui_screen.blit(draw_text(text, dark_color, light_color), (self.x + 24, self.y + 16 + y_offset))
                    y_offset += 24

        if upgrade.get(UpgradeAttribute.NEW_TYPE):
            for piece_type, attributes in upgrade[UpgradeAttribute.NEW_TYPE].items():
                for attribute in attributes:
                    # Draw the affected piece
                    ui_screen.blit(spr_pieces[self.team][piece_type].subsurface(0, 0, 24, 24), (self.x + 2, self.y + 8 + y_offset))

                    # Render the affected attribute + its new stat
                    text = get_string(attribute_label_strings, attribute)
                    value = upgrade[UpgradeAttribute.NEW_TYPE][piece_type][attribute]
                    if not isinstance(value, bool):
                        text += " -> " + str(value)

                    ui_screen.blit(draw_text(text, dark_color, light_color), (self.x + 24, self.y + 16 + y_offset))
                    y_offset += 24

        if upgrade.get(UpgradeAttribute.NEW_ATTACK_MULTIPLIER):
            for piece_type, multipliers in upgrade[UpgradeAttribute.NEW_ATTACK_MULTIPLIER].items():
                for enemy_archetype, value in multipliers.items():
                    # Render the first piece type
                    ui_screen.blit(spr_pieces[self.team][piece_type].subsurface(0, 0, 24, 24),
                                   (self.x + 2, self.y + 8 + y_offset))

                    # Render the attack icon
                    ui_screen.blit(spr_combat_icon[self.team], (self.x + 2 + 24, self.y + 8 + y_offset))

                    # Render the target piece type
                    ui_screen.blit(spr_pieces[self.team][piece_archetype_to_type[enemy_archetype]].subsurface(0, 0, 24, 24),
                                   (self.x + 2 + 48, self.y + 8 + y_offset))

                    # Render the new multiplier
                    text = get_string(formatted_strings, "QUANTITY")\
                        .format(upgrade[UpgradeAttribute.NEW_ATTACK_MULTIPLIER][piece_type][enemy_archetype])
                    ui_screen.blit(draw_text(text, dark_color, light_color), (self.x + 72, self.y + 16 + y_offset))

                    y_offset += 24

        if upgrade.get(UpgradeAttribute.NEW_BUILDABLE):
            for piece_type, new_pieces in upgrade[UpgradeAttribute.NEW_BUILDABLE].items():
                # Render the affected piece type
                ui_screen.blit(spr_pieces[self.team][piece_type].subsurface(0, 0, 24, 24),
                               (self.x + 2, self.y + 8 + y_offset))

                # Render the build icon
                ui_screen.blit(spr_build_icon[self.team], (self.x + 2 + 24, self.y + 8 + y_offset))

                # Render each new buildable piece
                x_offset = 0
                for new_piece in new_pieces:
                    ui_screen.blit(spr_pieces[self.team][new_piece].subsurface(0, 0, 24, 24),
                                   (self.x + 2 + 48 + x_offset, self.y + 8 + y_offset))
                    x_offset += 24

                y_offset += 24

        return y_offset

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        ui_screen.fill(clear_color[self.team], (self.x, self.y, 24 * 8, 24 * 9))
        ui_screen.fill(light_color, (self.x + 2, self.y + 2, 24 * 8 - 4, 24 * 9 - 5))

        if self.target in PieceType:
            # Render piece icons
            ui_screen.fill(clear_color[self.team], (self.x + 4, self.y + 12, 16, 16))
            ui_screen.blit(spr_pieces[self.team][self.target].subsurface(0, 0, 24, 24), (self.x + 2, self.y + 8))

            ui_screen.blit(get_text(piece_name_strings, self.target, light=False), (self.x + 32, self.y + 16))

            y_offset = self.render_piece_attributes(ui_screen)

        elif self.target in UpgradeType:
            # Render upgrade icons
            ui_screen.blit(spr_upgrade_icons[self.team][self.target], (self.x + 4, self.y + 8))

            ui_screen.blit(get_text(upgrade_name_strings, self.target, light=False), (self.x + 32, self.y + 16))

            y_offset = self.render_upgrade_attributes(ui_screen)
        else:
            # Render menu option icons
            ui_screen.blit(spr_order_options[self.team][self.target], (self.x + 4, self.y + 8))

            ui_screen.blit(get_text(menu_option_strings, self.target, light=False), (self.x + 32, self.y + 16))

            y_offset = 16

        # Render the description text
        description = get_multiline_text(menu_help_strings, self.target, light=False, width=subgrid_width * subgrid_size - 8)
        ui_screen.blit(description, (self.x + 4, self.y + 16 + y_offset))

        # Render any bought upgrades for this piece
        relevant_upgrades = [upgrade for upgrade in self.get_manager(Manager.TEAM).get_owned_upgrades(self.team)
                             if self.target in base_upgrades[upgrade][UpgradeAttribute.DISPLAY_FOR]]

        x_offset = 0
        for upgrade in relevant_upgrades:
            ui_screen.blit(spr_upgrade_icons[self.team][upgrade], (self.x + 4 + x_offset, self.y + subgrid_size * subgrid_height - 4))
            x_offset += 24
