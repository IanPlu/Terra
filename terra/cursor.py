from terra.settings import *
from terra.constants import *
from terra.gameobject import GameObject
from terra.menupopup import MenuPopup
from terra.mathutil import clamp
from terra.event import *
from terra.tileselection import TileSelection

# TODO: Build palette swaps rather than hard-code
cursor_sprites = {
    Team.RED: pygame.image.load("resources/sprites/ui/Cursor.png"),
    Team.BLUE: pygame.image.load("resources/sprites/ui/Cursor-2.png")
}


# Controllable cursor on the map.
# Triggers selection events and allows the player to move around.
class Cursor(GameObject):
    def __init__(self, game_map, team=Team.RED, gx=0, gy=0):
        super().__init__()
        self.game_map = game_map
        self.gx = gx
        self.gy = gy
        self.team = team

        self.menu = None
        self.move_ui = None

    def confirm(self):
        publish_game_event(E_SELECT, {
            'gx': int(self.gx),
            'gy': int(self.gy),
            'team': self.team,
            'selecting_movement': self.move_ui is not None
        })

    def cancel(self):
        publish_game_event(E_CANCEL, {})

    def debug2(self):
        if self.team == Team.RED:
            self.team = Team.BLUE
        elif self.team == Team.BLUE:
            self.team = Team.RED

    # Creates a menu popup from the provided event.
    def open_menu(self, event):
        self.menu = MenuPopup(event.gx, event.gy, self.team, event.options)

    def close_menu(self):
        del self.menu
        self.menu = None

    def open_move_ui(self, event):
        self.move_ui = TileSelection(event.gx, event.gy, event.min_range, event.max_range,
                                     event.game_map, event.movement_type, event.team, event.army, event.option)

    def close_move_ui(self, event):
        del self.move_ui
        self.move_ui = None

    def step(self, event):
        super().step(event)

        if is_event_type(event, E_OPEN_MENU):
            self.open_menu(event)
        elif is_event_type(event, E_CLOSE_MENU):
            self.close_menu()
        elif is_event_type(event, E_OPEN_TILE_SELECTION):
            self.open_move_ui(event)
        elif is_event_type(event, E_SELECT_TILE, E_CANCEL_TILE_SELECTION):
            self.close_move_ui(event)

        # Only react to button inputs if we're not showing a sub menu
        if self.menu:
            self.menu.step(event)
        else:
            if self.move_ui:
                self.move_ui.step(event)

            if event.type == KEYDOWN:
                # Cursor movement
                if event.key in KB_UP and self.gy > 0:
                    self.gy -= 1
                elif event.key in KB_DOWN and self.gy < self.game_map.height - 1:
                    self.gy += 1
                if event.key in KB_LEFT and self.gx > 0:
                    self.gx -= 1
                elif event.key in KB_RIGHT and self.gx < self.game_map.width - 1:
                    self.gx += 1

                # Unit selection
                if event.key in KB_CONFIRM:
                    self.confirm()
                elif event.key in KB_CANCEL:
                    self.cancel()
                elif event.key in KB_DEBUG2:
                    self.debug2()

            # Mouse control of the cursor
            elif event.type == MOUSEMOTION:
                mousex, mousey = pygame.mouse.get_pos()
                # Convert the screen coordinates to the grid coordinates
                self.gx = (mousex / SCREEN_SCALE) // GRID_WIDTH
                self.gy = (mousey / SCREEN_SCALE) // GRID_HEIGHT
                self.gx = clamp(self.gx, 0, self.game_map.width - 1)
                self.gy = clamp(self.gy, 0, self.game_map.height - 1)

            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CONFIRM:
                    self.confirm()
                elif event.button in KB_CANCEL:
                    self.cancel()

    def render(self, screen):
        super().render(screen)
        if self.menu:
            self.menu.render(screen)
        if self.move_ui:
            self.move_ui.render(screen)
        screen.blit(cursor_sprites[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))