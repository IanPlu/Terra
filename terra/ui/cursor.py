import pygame

from terra.turn.battlephase import BattlePhase
from terra.constants import CAMERA_WIDTH, CAMERA_HEIGHT
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.piecetype import PieceType
from terra.resources.assets import spr_cursor, spr_turn_submitted_indicator, spr_wait_icon
from terra.settings import SETTINGS, Setting
from terra.sound.soundtype import SoundType
from terra.ui.menupopup import MenuPopup
from terra.ui.tileselection import TileSelection
from terra.util.mathutil import clamp

camera_scroll_speed = 3
camera_lock_distance = 1
camera_scroll_border = 1.5


# Controllable cursor on the map.
# Triggers selection events and allows the player to move around.
# Maintains a camera position roughly centered on the cursor.
class Cursor(GameObject):
    def __init__(self, team):
        super().__init__()

        # Cursors start on their team's base
        base = self.get_manager(Manager.PIECE).get_all_pieces_for_team(team, piece_type=PieceType.BASE)
        if len(base):
            self.gx = base[0].gx
            self.gy = base[0].gy
        else:
            self.gx = 0
            self.gy = 0

        self.team = team

        self.menu = None
        self.move_ui = None

        self.camera_x = self.gx * GRID_WIDTH
        self.camera_y = self.gy * GRID_HEIGHT
        self.camera_dest_x = self.camera_x
        self.camera_dest_y = self.camera_y
        self.scroll_camera()

        # Set the camera position to the destination immediately, otherwise we might scroll out of the map area
        self.camera_x = self.camera_dest_x
        self.camera_y = self.camera_dest_y

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

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.UP, self.move_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.move_down)
        input_handler.register_handler(InputAction.PRESS, Key.LEFT, self.move_left)
        input_handler.register_handler(InputAction.PRESS, Key.RIGHT, self.move_right)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.cancel)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.open_pause_menu)
        input_handler.register_handler(InputAction.MOTION, None, self.convert_mouse_coords_to_cursor)

    def is_accepting_events(self):
        return self.get_manager(Manager.PLAYER).active_team == self.team \
               and self.get_mode() in [Mode.BATTLE, Mode.NETWORK_BATTLE, Mode.EDIT]

    def is_accepting_input(self):
        return self.menu is None and self.get_manager(Manager.PLAYER).active_team == self.team \
               and self.get_mode() in [Mode.BATTLE, Mode.NETWORK_BATTLE, Mode.EDIT]

    def can_confirm_or_cancel(self):
        return self.get_manager(Manager.TURN).phase == BattlePhase.ORDERS

    def convert_mouse_coords_to_cursor(self):
        mousex, mousey = pygame.mouse.get_pos()
        # Convert the screen coordinates to the grid coordinates
        self.gx = (mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH
        self.gy = (mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT

    def move_up(self):
        if self.gy > 0:
            self.gy -= 1
            self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_MOVE)

    def move_down(self):
        if self.gy < self.get_manager(Manager.MAP).height - 1:
            self.gy += 1
            self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_MOVE)

    def move_left(self):
        if self.gx > 0:
            self.gx -= 1
            self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_MOVE)

    def move_right(self):
        if self.gx < self.get_manager(Manager.MAP).width - 1:
            self.gx += 1
            self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_MOVE)

    def confirm(self):
        if self.can_confirm_or_cancel():
            if not self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                if self.get_mode() in [Mode.BATTLE, Mode.NETWORK_BATTLE] and \
                        not self.get_manager(Manager.PIECE).get_piece_at(int(self.gx), int(self.gy), self.team) and \
                        not self.move_ui:
                    self.open_pause_menu()
                else:
                    publish_game_event(EventType.E_SELECT, {
                        'gx': int(self.gx),
                        'gy': int(self.gy),
                        'team': self.team,
                        'selecting_movement': self.move_ui is not None
                    })

                    self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_SELECT)

    def cancel(self):
        if self.can_confirm_or_cancel():
            if not self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                publish_game_event(EventType.E_CANCEL, {})

                self.get_manager(Manager.SOUND).play_sound(SoundType.CURSOR_SELECT)

    # Creates a generic menu popup from the provided event.
    def open_menu(self, event):
        if self.can_confirm_or_cancel():
            self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def close_menu(self, event):
        if self.can_confirm_or_cancel():
            if self.menu:
                self.menu.destroy()
            self.menu = None

    def open_pause_menu(self):
        if self.can_confirm_or_cancel():
            if self.get_mode() in [Mode.BATTLE, Mode.NETWORK_BATTLE]:
                if self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
                    menu_options = [Option.MENU_REVISE_TURN]
                else:
                    menu_options = [Option.MENU_SUBMIT_TURN]

                if self.get_manager(Manager.PLAYER).is_hotseat_mode():
                    menu_options.append(Option.MENU_SWAP_ACTIVE_PLAYER)

                menu_options.extend([Option.MENU_SAVE_GAME, Option.MENU_CONCEDE, Option.MENU_QUIT_BATTLE])
            elif self.get_mode() == Mode.EDIT:
                menu_options = [Option.MENU_FILL_WITH_CURRENT_TILE, Option.MENU_MIRROR_X, Option.MENU_MIRROR_Y,
                                Option.MENU_SAVE_MAP, Option.MENU_QUIT_BATTLE]
            else:
                # Don't open the menu in this mode
                return

            self.menu = MenuPopup(self, self.gx, self.gy, self.team, menu_options, centered=True)

    def open_move_ui(self, event):
        self.move_ui = TileSelection(event.gx, event.gy, event.min_range, event.max_range,
                                     event.movement_type, event.piece_type, event.team, event.option)

    def close_move_ui(self, event):
        if self.move_ui:
            self.move_ui.destroy()
            self.move_ui = None

    def open_build_ui(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def open_upgrade_ui(self, event):
        self.menu = MenuPopup(self, event.gx, event.gy, event.team, event.options)

    def step(self, event):
        super().step(event)

        if self.menu:
            self.menu.step(event)
        if self.move_ui:
            self.move_ui.step(event)

    # Clamp gx and gy, and scroll camera as appropriate
    def scroll_camera(self):
        map = self.get_manager(Manager.MAP)

        if not self.menu and pygame.mouse.get_focused():
            mousex, mousey = pygame.mouse.get_pos()
            # Convert the screen coordinates to the grid coordinates
            self.gx = clamp((mousex / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_x) // GRID_WIDTH, 0, map.width - 1)
            self.gy = clamp((mousey / SETTINGS.get(Setting.SCREEN_SCALE) + self.camera_y) // GRID_HEIGHT, 0, map.height - 1)

        camera_min_gx = self.camera_dest_x // GRID_WIDTH
        camera_min_gy = self.camera_dest_y // GRID_HEIGHT
        camera_max_gx = camera_min_gx + CAMERA_WIDTH // GRID_WIDTH
        camera_max_gy = camera_min_gy + CAMERA_HEIGHT // GRID_HEIGHT

        if self.gx >= camera_max_gx - camera_scroll_border:
            self.camera_dest_x += GRID_WIDTH
        if self.gx <= camera_min_gx + camera_scroll_border:
            self.camera_dest_x -= GRID_WIDTH
        if self.gy >= camera_max_gy - camera_scroll_border:
            self.camera_dest_y += GRID_HEIGHT
        if self.gy <= camera_min_gy + camera_scroll_border:
            self.camera_dest_y -= GRID_HEIGHT

        self.camera_dest_x = clamp(self.camera_dest_x, 0, map.width * GRID_WIDTH - CAMERA_WIDTH)
        self.camera_dest_y = clamp(self.camera_dest_y, 0, map.height * GRID_HEIGHT - CAMERA_HEIGHT)

        # Scroll the actual camera position to the destination coords
        if self.camera_x != self.camera_dest_x:
            self.camera_x += (self.camera_dest_x - self.camera_x) / camera_scroll_speed
            if abs(self.camera_x - self.camera_dest_x) <= camera_lock_distance:
                self.camera_x = self.camera_dest_x
        if self.camera_y != self.camera_dest_y:
            self.camera_y += (self.camera_dest_y - self.camera_y) / camera_scroll_speed
            if abs(self.camera_y - self.camera_dest_y) <= camera_lock_distance:
                self.camera_y = self.camera_dest_y

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        self.scroll_camera()

        if self.move_ui:
            self.move_ui.render(game_screen, ui_screen)

        game_screen.blit(spr_cursor[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.get_manager(Manager.TEAM).is_turn_submitted(self.team):
            game_screen.blit(spr_turn_submitted_indicator[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.get_manager(Manager.TURN).phase != BattlePhase.ORDERS:
            game_screen.blit(spr_wait_icon[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))

        if self.menu:
            self.menu.render(game_screen, ui_screen)
