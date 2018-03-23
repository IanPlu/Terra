from pygame.constants import KEYDOWN, KEYUP, KMOD_CTRL, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT, RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.engine.gamescreen import GameScreen
from terra.event import *
from terra.keybindings import KB_MENU2, KB_SCROLL_UP, KB_SCROLL_DOWN, KB_CONFIRM, KB_CANCEL
from terra.managers.managers import Managers
from terra.map.tiletype import TileType
from terra.piece.piecetype import PieceType
from terra.resources.assets import clear_color, spr_tiles, spr_cursor, spr_pieces
from terra.team import Team
from terra.util.mathutil import clamp
from terra.piece.piece import Piece


# A map editor for Terra maps.
# Allows placing tiles of different types and saving / loading maps.
class LevelEditor(GameScreen):
    def __init__(self, map_name="edited_map.map"):
        super().__init__()

        Managers.initialize_managers(map_name, None, False)

        self.current_tile_type = TileType.GRASS
        self.secondary_tile_type = TileType.SEA

        self.placing_tiles = True
        self.piece_team = Team.RED
        self.piece_type = PieceType.COLONIST

        self.placing_multiple = False
        self.placing_multiple_alt = False

    def step(self, event):
        super().step(event)

        Managers.step(event)

        if is_event_type(event, E_SELECT):
            self.confirm()
        elif is_event_type(event, E_CANCEL):
            self.confirm2()
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.option == MENU_SAVE_MAP:
                Managers.save_map_to_file()
            elif event.option == MENU_QUIT_BATTLE:
                publish_game_event(E_QUIT_BATTLE, {})
            elif event.option == MENU_FILL_WITH_CURRENT_TILE:
                self.fill_with_current_tile()
        elif event.type == KEYDOWN:
            if event.key in KB_SCROLL_UP:
                self.scroll(1)
            elif event.key in KB_SCROLL_DOWN:
                self.scroll(-1)
            elif event.key in KB_MENU2:
                self.swap_placing_mode()
            elif event.key in KB_CONFIRM:
                self.placing_multiple = True
            elif event.key in KB_CANCEL:
                self.placing_multiple_alt = True
        elif event.type == MOUSEBUTTONDOWN:
            if event.button in KB_SCROLL_UP:
                self.scroll(1)
            elif event.button in KB_SCROLL_DOWN:
                self.scroll(-1)
            elif event.button in KB_CONFIRM:
                self.placing_multiple = True
            elif event.button in KB_CANCEL:
                self.placing_multiple_alt = True
        elif event.type == KEYUP:
            self.placing_multiple = False
            self.placing_multiple_alt = False
        elif event.type == MOUSEBUTTONUP:
            self.placing_multiple = False
            self.placing_multiple_alt = False

        if self.placing_multiple:
            self.confirm()
        elif self.placing_multiple_alt:
            self.confirm2()

    def confirm(self):
        if self.placing_tiles:
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            Managers.battle_map.update_tile_type(cursor_x, cursor_y, self.current_tile_type)
        else:
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            if Managers.piece_manager.get_piece_at(cursor_x, cursor_y, self.piece_team):
                # Delete the existing piece first
                Managers.piece_manager.remove_piece(cursor_x, cursor_y, self.piece_team)

            Managers.piece_manager.register_piece(Piece(self.piece_type, self.piece_team, cursor_x, cursor_y))

    def confirm2(self):
        if self.placing_tiles:
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            Managers.battle_map.update_tile_type(cursor_x, cursor_y, self.secondary_tile_type)
        else:
            cursor_x, cursor_y = Managers.player_manager.get_cursor_coords()
            Managers.piece_manager.remove_piece(cursor_x, cursor_y, self.piece_team)

    def scroll(self, direction):
        if self.placing_tiles:
            if pygame.key.get_mods() & KMOD_CTRL:
                self.secondary_tile_type = self.update_tile_type(self.secondary_tile_type, direction)
            else:
                self.current_tile_type = self.update_tile_type(self.current_tile_type, direction)
        else:
            if pygame.key.get_mods() & KMOD_CTRL:
                self.piece_team = self.update_team(self.piece_team, direction)
            else:
                self.piece_type = self.update_piece_type(self.piece_type, direction)

    def swap_placing_mode(self):
        self.placing_tiles = not self.placing_tiles

    def update_tile_type(self, tiletype, amount):
        new_tile_type = clamp(tiletype.value + amount, 1, len(TileType))

        if not new_tile_type == tiletype:
            return TileType(new_tile_type)

    def update_piece_type(self, piecetype, amount):
        new_piece_type = clamp(piecetype.value + amount, 1, len(PieceType) - 1)

        if not new_piece_type == piecetype:
            return PieceType(new_piece_type)

    def update_team(self, team, amount):
        if team == Team.RED:
            new_team = Team.BLUE
        elif team == Team.BLUE:
            new_team = Team.RED
        else:
            new_team = Team.RED

        if not new_team == team:
            return Team(new_team)

    def get_tile_sprite_for_tiletype(self, tiletype):
        if tiletype in [TileType.COAST]:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)
        else:
            return spr_tiles[tiletype].subsurface(0, 0, 24, 24)

    def get_piece_sprite_for_piecetype(self, piecetype):
        return spr_pieces[self.piece_team][piecetype]

    def fill_with_current_tile(self):
        Managers.battle_map.fill_map_with_tile(self.current_tile_type)

    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map_screen = pygame.Surface((Managers.battle_map.width * GRID_WIDTH, Managers.battle_map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)
        Managers.render(map_screen, ui_screen)

        # Render the current tile at the bottom of the screen
        ui_screen.fill(clear_color[Team.RED], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        # Render tiles
        tile_display = pygame.Surface((GRID_WIDTH * 2, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        tile_display.set_alpha(255 if self.placing_tiles else 64)

        tile_display.blit(self.get_tile_sprite_for_tiletype(self.current_tile_type), (0, 0))
        tile_display.blit(spr_cursor[Team.RED], (0, 0))
        tile_display.blit(self.get_tile_sprite_for_tiletype(self.secondary_tile_type), (GRID_WIDTH, 0))
        tile_display.blit(spr_cursor[Team.BLUE], (GRID_WIDTH, 0))

        ui_screen.blit(tile_display, (0, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render pieces
        piece_display = pygame.Surface((GRID_WIDTH, GRID_HEIGHT), pygame.SRCALPHA, 32).convert()
        piece_display.set_alpha(255 if not self.placing_tiles else 64)

        piece_display.fill(clear_color[self.piece_team], (0, 0, GRID_WIDTH, GRID_HEIGHT))
        piece_display.blit(self.get_piece_sprite_for_piecetype(self.piece_type), (0, 0))
        piece_display.blit(spr_cursor[self.piece_team], (0, 0))

        ui_screen.blit(piece_display, (GRID_WIDTH * 3, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Trim the screen to just the camera area
        camera_x, camera_y = Managers.player_manager.get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
