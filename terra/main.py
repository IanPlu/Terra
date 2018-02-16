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


class Mode(Enum):
    MAIN_MENU = 0
    BATTLE = 1
    EDIT = 2
    NETWORK_BATTLE = 3


# Main entry point for the game.
class Main:
    def __init__(self):
        self.mode = None
        self.current_screen = None

        self.set_screen_from_mode(Mode.MAIN_MENU)

    def set_screen_from_mode(self, new_mode, mapname=None, address=None, is_host=False):
        self.mode = new_mode
        if new_mode == Mode.MAIN_MENU:
            self.current_screen = MainMenu()
        elif new_mode == Mode.BATTLE:
            self.current_screen = Battle(mapname, address, is_host)
        elif new_mode == Mode.EDIT:
            self.current_screen = LevelEditor(mapname)

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
            elif event.option == Option.LEVEL_EDITOR:
                self.set_screen_from_mode(Mode.EDIT, event.mapname)
            elif event.option == Option.QUIT:
                quit()
        elif is_event_type(event, E_QUIT_BATTLE):
            self.set_screen_from_mode(Mode.MAIN_MENU, None)

    # Render phase of game loop - draw to the screen
    # noinspection PyArgumentList
    def render(self):
        ui_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        ui_screen = ui_screen.convert_alpha()

        game_screen = self.current_screen.render(ui_screen)
        game_screen.blit(ui_screen, (0, 0))

        pygame.transform.scale(game_screen, (screen_width, screen_height), screen)
        pygame.display.flip()


# Initialize pygame and some UI settings
pygame.init()
screen_resolution = screen_width, screen_height = RESOLUTION_WIDTH * SCREEN_SCALE, RESOLUTION_HEIGHT * SCREEN_SCALE

screen = pygame.display.set_mode(screen_resolution)
screen.fill(clear_color[Team.RED])

load_assets()

clock = pygame.time.Clock()
main = Main()

# Game loop
while True:
    # Update game tick TICK_RATE times per second
    clock.tick(TICK_RATE)

    # Run game logic
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

        main.step(event)

    # Render to the screen
    main.render()
