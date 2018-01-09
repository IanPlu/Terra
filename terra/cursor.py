from terra.settings import *
from terra.constants import *
from terra.gameobject import GameObject
from terra.menupopup import MenuPopup

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

    def confirm(self):
        pygame.event.post(pygame.event.Event(E_SELECT, {'gx': self.gx, 'gy': self.gy, 'team': self.team}))

    def cancel(self):
        pygame.event.post(pygame.event.Event(E_CANCEL, {}))

    # TODO: Remove debug key
    def debug1(self):
        pygame.event.post(pygame.event.Event(E_EXECUTE_ORDERS, {}))

    def debug2(self):
        if self.team == Team.RED:
            self.team = Team.BLUE
        elif self.team == Team.BLUE:
            self.team = Team.RED

    # Creates a menu popup from the provided event.
    def open_menu(self, event):
        self.menu = MenuPopup(event.gx, event.gy, self.team, event.options)

    def close_menu(self):
        # TODO: Check that menus are actually being deleted once dereferenced
        self.menu = None

    def step(self, event):
        super().step(event)

        if event.type == E_OPEN_MENU:
            self.open_menu(event)
        elif event.type == E_CLOSE_MENU:
            self.close_menu()

        # Only react to button inputs if we're not showing a sub menu
        if self.menu:
            self.menu.step(event)
        else:
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
                elif event.key in KB_DEBUG1:
                    self.debug1()
                elif event.key in KB_DEBUG2:
                    self.debug2()

            # Mouse control of the cursor
            elif event.type == MOUSEMOTION:
                mousex, mousey = pygame.mouse.get_pos()
                # Convert the screen coordinates to the grid coordinates
                self.gx = (mousex / SCREEN_SCALE) // GRID_WIDTH
                self.gy = (mousey / SCREEN_SCALE) // GRID_HEIGHT
            elif event.type == MOUSEBUTTONDOWN:
                if event.button in KB_CONFIRM:
                    self.confirm()
                elif event.button in KB_CANCEL:
                    self.cancel()

    def render(self, screen):
        super().render(screen)
        if self.menu:
            self.menu.render(screen)
        screen.blit(cursor_sprites[self.team], (self.gx * GRID_WIDTH, self.gy * GRID_HEIGHT))