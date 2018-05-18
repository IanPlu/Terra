import pygame

from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_turn_submitted_indicator, spr_wait_icon
from terra.sound.soundtype import SoundType
from terra.turn.battlephase import BattlePhase
from terra.ui.cursor import Cursor
from terra.ui.menupopup import MenuPopup
from terra.ui.tileselection import TileSelection
from terra.ui.detailbox import DetailBox


# Controllable cursor on the battle map.
# Contains submenus for piece orders and piece movement.
class BattleCursor(Cursor):
    def __init__(self, team):
        self.menu = None
        self.move_ui = None
        self.detail_box = None

        super().__init__(team)

        base = self.get_manager(Manager.PIECE).get_all_pieces_for_team(team, piece_type=PieceType.BASE)
        if len(base):
            self.gx = base[0].gx
            self.gy = base[0].gy
        else:
            self.gx = 0
            self.gy = 0

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_OPEN_MENU, self.open_menu)
        event_bus.register_handler(EventType.E_CLOSE_MENU, self.close_menu)
        event_bus.register_handler(EventType.E_SELECT_BUILD_UNIT, self.close_menu)
        event_bus.register_handler(EventType.E_CANCEL_BUILD_UNIT, self.close_menu)
        event_bus.register_handler(EventType.E_SELECT_UPGRADE, self.close_menu)
        event_bus.register_handler(EventType.E_CANCEL_UPGRADE, self.close_menu)
        event_bus.register_handler(EventType.E_OPEN_TILE_SELECTION, self.open_move_ui)
        event_bus.register_handler(EventType.E_SELECT_TILE, self.close_move_ui)
        event_bus.register_handler(EventType.E_CANCEL_TILE_SELECTION, self.close_move_ui)
        event_bus.register_handler(EventType.E_OPEN_BUILD_MENU, self.open_build_ui)
        event_bus.register_handler(EventType.E_OPEN_UPGRADE_MENU, self.open_upgrade_ui)
        event_bus.register_handler(EventType.E_CLOSE_DETAILBOX, self.close_detailbox)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.open_pause_menu)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.open_detailbox)

    def is_accepting_events(self):
        return self.get_manager(Manager.PLAYER).active_team == self.team \
               and self.get_mode() in [Mode.BATTLE, Mode.CAMPAIGN, Mode.NETWORK_BATTLE, Mode.EDIT]

    def is_accepting_input(self):
        return self.menu is None and self.detail_box is None and \
               self.get_manager(Manager.PLAYER).active_team == self.team and \
               self.get_mode() in [Mode.BATTLE, Mode.CAMPAIGN, Mode.NETWORK_BATTLE, Mode.EDIT]

    def can_confirm_or_cancel(self):
        return self.get_manager(Manager.TURN).phase == BattlePhase.ORDERS

    def confirm(self):
        super().confirm()
        if self.can_confirm_or_cancel():
            if not self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                if not self.get_manager(Manager.PIECE).get_piece_at(int(self.gx), int(self.gy), self.team) and \
                        not self.move_ui:
                    self.open_pause_menu()
                else:
                    publish_game_event(EventType.E_SELECT, {
                        'gx': int(self.gx),
                        'gy': int(self.gy),
                        'team': self.team,
                        'selecting_movement': self.move_ui is not None
                    })

    def cancel(self):
        super().cancel()
        if self.can_confirm_or_cancel():
            if not self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                publish_game_event(EventType.E_CANCEL, {})

    def is_active(self):
        return not self.menu and not self.detail_box and pygame.mouse.get_focused()

    # Creates a generic menu popup from the provided event.
    def open_menu(self, event):
        if self.can_confirm_or_cancel():
            self.menu = MenuPopup(self, event.team, event.gx, event.gy, event.options)

    def close_menu(self, event):
        if self.can_confirm_or_cancel():
            if self.menu:
                self.menu.destroy()
            self.menu = None

    def open_pause_menu(self):
        self.play_sound(SoundType.CURSOR_SELECT)
        if self.can_confirm_or_cancel():
            if self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                menu_options = [Option.MENU_REVISE_TURN]
            else:
                menu_options = [Option.MENU_SUBMIT_TURN]

            if self.get_manager(Manager.PLAYER).is_hotseat_mode():
                menu_options.append(Option.MENU_SWAP_ACTIVE_PLAYER)

            menu_options.extend([Option.MENU_SAVE_GAME, Option.MENU_CONCEDE, Option.MENU_QUIT_BATTLE])

            self.menu = MenuPopup(self, self.team, self.gx, self.gy, menu_options, centered=True)

    def open_move_ui(self, event):
        self.move_ui = TileSelection(event.gx, event.gy, event.min_range, event.max_range,
                                     event.movement_type, event.piece_type, event.team, event.option)

    def close_move_ui(self, event):
        if self.move_ui:
            self.move_ui.destroy()
            self.move_ui = None

    def open_build_ui(self, event):
        self.menu = MenuPopup(self, event.team, event.gx, event.gy, event.options)

    def open_upgrade_ui(self, event):
        self.menu = MenuPopup(self, event.team, event.gx, event.gy, event.options)

    def open_detailbox(self):
        if self.can_confirm_or_cancel():
            pieces = self.get_manager(Manager.PIECE).get_pieces_at(self.gx, self.gy)
            if len(pieces) > 0:
                self.detail_box = DetailBox([
                    (piece.piece_type, piece.team) for piece in pieces
                ])

    def close_detailbox(self, event=None):
        if self.can_confirm_or_cancel():
            if self.detail_box:
                self.detail_box.destroy()
            self.detail_box = None

    def step(self, event):
        super().step(event)

        if self.menu:
            self.menu.step(event)
        if self.move_ui:
            self.move_ui.step(event)
        if self.detail_box:
            self.detail_box.step(event)

    def render(self, game_screen, ui_screen):
        if self.move_ui:
            self.move_ui.render(game_screen, ui_screen)

        super().render(game_screen, ui_screen)

        if self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
            game_screen.blit(spr_turn_submitted_indicator[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.get_manager(Manager.TURN).phase != BattlePhase.ORDERS:
            game_screen.blit(spr_wait_icon[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.menu:
            self.menu.render(game_screen, ui_screen)
        if self.detail_box:
            self.detail_box.render(game_screen, ui_screen)











