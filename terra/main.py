import sys

from pygame.constants import QUIT

from terra.battle import Battle
from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH, TICK_RATE
from terra.event import *
from terra.leveleditor import LevelEditor
from terra.mainmenu.mainmenu import MainMenu
from terra.mainmenu.option import Option
from terra.managers.managers import Managers
from terra.mode import Mode
from terra.resources.assets import load_assets, clear_color, spr_game_icon
from terra.settings import Setting, SETTINGS
from terra.team import Team


# Main entry point for the game.
# Instantiate this class and call 'run()' on it to fire up the game.
class Main:
    def __init__(self):
        self.screen_resolution = None
        self.screen_width = None
        self.screen_height = None
        self.screen = None

        self.screens = {}
        self.set_screen_from_mode(Mode.MAIN_MENU)

    def set_screen_from_mode(self, new_mode, mapname=None, address=None, is_host=False):
        Managers.set_mode(new_mode)

        if new_mode == Mode.MAIN_MENU:
            new_screen = MainMenu()
        elif new_mode == Mode.BATTLE:
            new_screen = Battle(mapname, address, is_host)
        elif new_mode == Mode.EDIT:
            new_screen = LevelEditor(mapname)
        else:
            new_screen = None

        self.screens[new_mode] = new_screen

    # Set the screen resolution from the screen scale in the settings
    def reset_resolution(self):
        self.screen_resolution = RESOLUTION_WIDTH * SETTINGS.get(Setting.SCREEN_SCALE), \
                                 RESOLUTION_HEIGHT * SETTINGS.get(Setting.SCREEN_SCALE)
        self.screen_width, self.screen_height = self.screen_resolution

        self.screen = pygame.display.set_mode(self.screen_resolution)
        self.screen.fill(clear_color[Team.RED])

    def quit(self):
        pygame.quit()
        sys.exit()

    # Step phase of game loop - handle events
    def step(self, event):
        self.screens[Managers.current_mode].step(event)

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
                self.set_screen_from_mode(Mode.EDIT, event.mapname)
            elif event.option == Option.LOAD_MAP:
                self.set_screen_from_mode(Mode.EDIT, event.mapname)
            elif event.option == Option.QUIT:
                self.quit()
            elif event.option == Option.SAVE_SETTINGS:
                SETTINGS.save_settings()
                self.reset_resolution()
        elif is_event_type(event, E_QUIT_BATTLE):
            # Reset the screens and managers
            Managers.tear_down_managers()
            self.screens = {}
            self.set_screen_from_mode(Mode.MAIN_MENU, None)

    # Render phase of game loop - draw to the screen
    # noinspection PyArgumentList
    def render(self):
        base_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        base_screen.fill(clear_color[Team.BLUE], (0, 0, RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

        ui_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        ui_screen = ui_screen.convert_alpha()

        game_screen = self.screens[Managers.current_mode].render(ui_screen)

        base_screen.blit(game_screen, (0, 0))
        base_screen.blit(ui_screen, (0, 0))

        pygame.transform.scale(base_screen, (self.screen_width, self.screen_height), self.screen)
        pygame.display.update()

    # Run the entire game + loop. Initialize stuff like pygame and the window the game will render in.
    def run(self):
        # Initialize pygame and some UI settings
        pygame.init()
        self.reset_resolution()

        load_assets()

        # Set the window icon and caption
        pygame.display.set_icon(spr_game_icon)
        pygame.display.set_caption("Terra")

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
