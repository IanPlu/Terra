import sys
from enum import Enum

from pygame.constants import QUIT

from terra.battle import Battle
from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.event import *
from terra.leveleditor import LevelEditor
from terra.mainmenu.mainmenu import MainMenu
from terra.mainmenu.option import Option
from terra.resources.assets import load_assets, clear_color
from terra.settings import SCREEN_SCALE, TICK_RATE
from terra.team import Team
from terra.managers.managers import Managers


class Mode(Enum):
    MAIN_MENU = 0
    BATTLE = 1
    EDIT = 2
    NETWORK_BATTLE = 3


# Main entry point for the game.
# Instantiate this class and call 'run()' on it to fire up the game.
class Main:
    def __init__(self):
        self.mode = None
        self.current_screen = None

        self.screen_resolution = None
        self.screen_width = None
        self.screen_height = None
        self.screen = None

        self.set_screen_from_mode(Mode.MAIN_MENU)

    def set_screen_from_mode(self, new_mode, mapname=None, address=None, is_host=False):
        self.mode = new_mode
        if new_mode == Mode.MAIN_MENU:
            self.current_screen = MainMenu()
        elif new_mode == Mode.BATTLE:
            self.current_screen = Battle(mapname, address, is_host)
        elif new_mode == Mode.EDIT:
            self.current_screen = LevelEditor(mapname)

    def quit(self):
        pygame.quit()
        sys.exit()

    # Step phase of game loop - handle events
    def step(self, event):
        self.current_screen.step(event)

        if is_event_type(event, MENU_SELECT_OPTION):
            if event.option == Option.NEW_GAME:
                self.set_screen_from_mode(Mode.BATTLE, event.mapname)
            elif event.option == Option.LOAD_GAME:
                self.set_screen_from_mode(Mode.BATTLE, event.mapname)
            elif event.option in [Option.NEW_NETWORK_GAME, Option.LOAD_NETWORK_GAME]:
                self.set_screen_from_mode(Mode.BATTLE, event.mapname, event.address, is_host=True)
            elif event.option == Option.JOIN_GAME:
                self.set_screen_from_mode(Mode.BATTLE, None, event.address, is_host=False)
            elif event.option == Option.NEW_MAP:
                self.set_screen_from_mode(Mode.EDIT, None)
            elif event.option == Option.LOAD_MAP:
                self.set_screen_from_mode(Mode.EDIT, event.mapname)
            elif event.option == Option.QUIT:
                self.quit()
        elif is_event_type(event, E_QUIT_BATTLE):
            self.set_screen_from_mode(Mode.MAIN_MENU, None)

    # Render phase of game loop - draw to the screen
    # noinspection PyArgumentList
    def render(self):
        ui_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        ui_screen = ui_screen.convert_alpha()

        game_screen = self.current_screen.render(ui_screen)
        game_screen.blit(ui_screen, (0, 0))

        pygame.transform.scale(game_screen, (self.screen_width, self.screen_height), self.screen)
        pygame.display.flip()

    # Run the entire game + loop. Initialize stuff like pygame and the window the game will render in.
    def run(self):
        # Initialize pygame and some UI settings
        pygame.init()
        self.screen_resolution = self.screen_width, self.screen_height = RESOLUTION_WIDTH * SCREEN_SCALE, RESOLUTION_HEIGHT * SCREEN_SCALE

        self.screen = pygame.display.set_mode(self.screen_resolution)
        self.screen.fill(clear_color[Team.RED])

        load_assets()

        clock = pygame.time.Clock()

        # Game loop
        while True:
            # Update game tick TICK_RATE times per second
            clock.tick(TICK_RATE)

            # Plumb for network messages if necessary
            if Managers.network_manager:
                Managers.network_manager.network_step()

            # Run game logic
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit()

                self.step(event)

            # Render to the screen
            self.render()
