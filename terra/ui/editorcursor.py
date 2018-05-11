import pygame
from pygame.constants import KMOD_CTRL

from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.event.event import EventType, publish_game_event
from terra.managers.session import Manager
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.piece.piecetype import PieceType
from terra.team.team import Team
from terra.ui.cursor import Cursor
from terra.ui.menupopup import MenuPopup
from terra.util.mathutil import clamp


# Controllable cursor on the level editor.
# Allows the player to make changes to the map, either placing tile types or pieces.
class EditorCursor(Cursor):
    def __init__(self):
        self.menu = None

        super().__init__(Team.RED)
        self.placing_tiles = True

        self.tile_type = [TileType.GRASS, TileType.SEA]
        self.piece_type = PieceType.COLONIST

        self.placing_multiple = False
        self.placing_multiple_alt = False

        self.last_gx = self.gx
        self.last_gy = self.gy

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_CLOSE_MENU, self.close_menu)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.open_pause_menu)
        input_handler.register_handler(InputAction.PRESS, Key.MENU2, self.swap_placing_mode)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_UP, self.scroll_up)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_DOWN, self.scroll_down)

        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.start_multiplace)
        input_handler.register_handler(InputAction.RELEASE, Key.CONFIRM, self.end_multiplace)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.start_multiplace_alt)
        input_handler.register_handler(InputAction.RELEASE, Key.CANCEL, self.end_multiplace_alt)

    def is_accepting_input(self):
        return self.menu is None

    def is_active(self):
        return not self.menu and pygame.mouse.get_focused()

    # LClick action -- place tiles or pieces
    def confirm(self):
        if self.placing_tiles:
            self.place_tile(self.tile_type[0])
        else:
            self.place_piece(self.piece_type)

    # RClick action -- place alt tiles or remove pieces
    def cancel(self):
        if self.placing_tiles:
            self.place_tile(self.tile_type[1])
        else:
            self.remove_piece()

    # Swap between placing tiles and placing pieces
    def swap_placing_mode(self):
        self.placing_tiles = not self.placing_tiles

    def scroll_up(self):
        self.update_object_to_place(direction=1)

    def scroll_down(self):
        self.update_object_to_place(direction=-1)

    def start_multiplace(self):
        self.placing_multiple = True

    def end_multiplace(self):
        self.placing_multiple = False

    def start_multiplace_alt(self):
        self.placing_multiple_alt = True

    def end_multiplace_alt(self):
        self.placing_multiple_alt = False

    def open_pause_menu(self):
        self.menu = MenuPopup(self, Team.RED, self.gx, self.gy, [
            Option.MENU_SAVE_MAP,
            Option.MENU_FILL_WITH_CURRENT_TILE,
            Option.MENU_DESTROY_ALL_PIECES,
            Option.MENU_MIRROR_X,
            Option.MENU_MIRROR_Y,
            Option.MENU_QUIT_BATTLE
        ], centered=True)

    def close_menu(self, event):
        if self.menu:
            self.menu.destroy()
        self.menu = None

    # Scroll through placeable tiles / pieces
    def update_object_to_place(self, direction=1):
        alt_held = pygame.key.get_mods() & KMOD_CTRL
        if self.placing_tiles:
            # Update tile type
            index = 1 if alt_held else 0
            self.tile_type[index] = self.get_next_tile_type(self.tile_type[index], direction)
        else:
            if alt_held:
                # Update team
                self.team = self.get_next_team(self.team, direction)
            else:
                # Update piece type
                self.piece_type = self.get_next_piece_type(self.piece_type, direction)

    # Safely return the next tile type before or after the current tile type
    def get_next_tile_type(self, current_tile_type, direction=1):
        return TileType(clamp(current_tile_type.value + direction, 1, len(TileType)))

    def get_next_piece_type(self, current_piece_type, direction=1):
        return PieceType(clamp(current_piece_type.value + direction, 1, len(PieceType) - 1))

    def get_next_team(self, current_team, direction=1):
        available_teams = self.get_manager(Manager.TEAM).all_teams + [Team.NONE]
        return available_teams[clamp(available_teams.index(current_team) + direction, 0, len(available_teams) - 1)]

    # Replace the tile at the current cursor location with the specified tile type
    def place_tile(self, tile_type):
        self.get_manager(Manager.MAP).update_tile_type(self.gx, self.gy, tile_type)

    # Place the current piece type at the current cursor location. If a piece for this team already exists, remove it
    def place_piece(self, piece_type):
        piece = self.get_manager(Manager.PIECE).get_piece_at(self.gx, self.gy, self.team)
        if piece:
            # Delete existing pieces first
            self.remove_piece(piece)

        publish_game_event(EventType.E_PIECE_BUILT, {
            'tx': self.gx,
            'ty': self.gy,
            'team': self.team,
            'new_piece_type': piece_type,
        })

    # Remove any piece belonging to the current team at the current cursor location
    def remove_piece(self, piece=None):
        if not piece:
            piece = self.get_manager(Manager.PIECE).get_piece_at(self.gx, self.gy, self.team)

        if piece:
            publish_game_event(EventType.E_PIECE_DEAD, {
                'gx': self.gx,
                'gy': self.gy,
                'team': self.team,
                'piece': piece
            })

    def step(self, event):
        super().step(event)

        if self.menu:
            self.menu.step(event)
        elif self.last_gx != self.gx or self.last_gy != self.gy:
            self.last_gx = self.gx
            self.last_gy = self.gy

            if self.placing_multiple:
                self.confirm()
            elif self.placing_multiple_alt:
                self.cancel()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.menu:
            self.menu.render(game_screen, ui_screen)
