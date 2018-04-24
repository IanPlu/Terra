import pygame

from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH, TICK_RATE
from terra.control.inputcontroller import INPUT_CONTROLLER
from terra.engine.animatedgameobject import AnimatedGameObject
from terra.engine.debug import DebugController
from terra.event.event import EventType
from terra.event.eventbus import EVENT_BUS
from terra.managers.session import SESSION, Manager
from terra.menu.titlescreen import TitleScreen
from terra.menu.option import Option
from terra.mode import Mode
from terra.resources.assetloading import AssetType
from terra.resources.assets import load_assets, clear_color, spr_game_icon
from terra.screens.battle import Battle
from terra.screens.leveleditor import LevelEditor
from terra.screens.lobby import Lobby
from terra.screens.results import ResultsScreen
from terra.settings import Setting, SETTINGS
from terra.team.team import Team

use_network_lobby = True


# Main entry point for the game.
# Instantiate this class and call 'run()' on it to fire up the game.
class Main:
    def __init__(self):
        self.screen_resolution = None
        self.screen_width = None
        self.screen_height = None
        self.screen = None

        self.current_screen = None
        self.set_screen_from_mode(Mode.MAIN_MENU)

        self.register_handlers()

        self.debug_handler = DebugController()
        self.should_quit = False

    def register_handlers(self):
        EVENT_BUS.register_handler(EventType.MENU_SELECT_OPTION, self.handle_menu_selections)
        EVENT_BUS.register_handler(EventType.E_START_NETWORK_BATTLE, self.handle_network_game_start)
        EVENT_BUS.register_handler(EventType.E_START_BATTLE, self.handle_local_game_start)
        EVENT_BUS.register_handler(EventType.E_BATTLE_OVER, self.handle_battle_end)
        EVENT_BUS.register_multiple_handlers(self.reset_to_menu, EventType.E_QUIT_BATTLE, EventType.E_EXIT_RESULTS,
                                             EventType.E_EXIT_LOBBY, EventType.E_NETWORKING_ERROR)

    def is_accepting_events(self):
        return True

    def set_screen_from_mode(self, new_mode, map_name=None, address=None, is_host=False, map_type=AssetType.MAP, results=None):
        SESSION.set_mode(new_mode)

        if new_mode == Mode.MAIN_MENU:
            new_screen = TitleScreen()
        elif new_mode == Mode.BATTLE:
            # Managers are already initialized by the lobby
            new_screen = Battle(create_session=False)
        elif new_mode == Mode.EDIT:
            new_screen = LevelEditor(map_name)
        elif new_mode == Mode.RESULTS:
            new_screen = ResultsScreen(results)
        elif new_mode == Mode.LOBBY:
            new_screen = Lobby(False, map_name, map_type)
        elif new_mode == Mode.NETWORK_LOBBY:
            new_screen = Lobby(is_host, map_name, map_type, address)
        elif new_mode == Mode.NETWORK_BATTLE:
            # Managers are already initialized by the lobby
            new_screen = Battle(create_session=False)
        else:
            new_screen = None

        # Clean up the old screen, if any
        if self.current_screen:
            self.current_screen.destroy()
        # Swap to the new screen
        self.current_screen = new_screen

    # Set the screen resolution from the screen scale in the settings
    def reset_resolution(self):
        self.screen_resolution = RESOLUTION_WIDTH * SETTINGS.get(Setting.SCREEN_SCALE), \
                                 RESOLUTION_HEIGHT * SETTINGS.get(Setting.SCREEN_SCALE)
        self.screen_width, self.screen_height = self.screen_resolution

        self.screen = pygame.display.set_mode(self.screen_resolution)
        self.screen.fill(clear_color[Team.RED])

    # Reset the screens and managers
    def reset_to_menu(self, event):
        SESSION.reset()
        self.set_screen_from_mode(Mode.MAIN_MENU)

    def handle_menu_selections(self, event):
        if event.option == Option.NEW_GAME:
            self.set_screen_from_mode(Mode.LOBBY, event.mapname)
        elif event.option == Option.LOAD_GAME:
            self.set_screen_from_mode(Mode.LOBBY, event.mapname, map_type=AssetType.SAVE)
        elif event.option == Option.NEW_NETWORK_GAME:
            mode = Mode.NETWORK_LOBBY if use_network_lobby else Mode.BATTLE
            self.set_screen_from_mode(mode, event.mapname, event.address, is_host=True)
        elif event.option == Option.LOAD_NETWORK_GAME:
            mode = Mode.NETWORK_LOBBY if use_network_lobby else Mode.BATTLE
            self.set_screen_from_mode(mode, event.mapname, event.address, is_host=True, map_type=AssetType.SAVE)
        elif event.option == Option.JOIN_GAME:
            mode = Mode.NETWORK_LOBBY if use_network_lobby else Mode.BATTLE
            self.set_screen_from_mode(mode, None, event.address, is_host=False)
        elif event.option == Option.NEW_MAP:
            self.set_screen_from_mode(Mode.EDIT, event.mapname)
        elif event.option == Option.LOAD_MAP:
            self.set_screen_from_mode(Mode.EDIT, event.mapname)
        elif event.option == Option.QUIT:
            self.quit()
        elif event.option == Option.SAVE_SETTINGS:
            SETTINGS.save_settings()
            self.reset_resolution()

    def handle_network_game_start(self, event):
        if SESSION.is_network_game:
            self.set_screen_from_mode(Mode.NETWORK_BATTLE)

    def handle_local_game_start(self, event):
        if not SESSION.is_network_game:
            self.set_screen_from_mode(Mode.BATTLE)

    def handle_battle_end(self, event):
        self.set_screen_from_mode(Mode.RESULTS, results=event.results)

    def quit(self):
        pygame.quit()
        self.should_quit = True

    # Step phase of game loop - handle events
    def step(self, event):
        # Allow the input controller to marshal events out
        INPUT_CONTROLLER.invoke_handlers(event)

        # Allow the event bus to marshal events out
        EVENT_BUS.invoke_handlers(event)

        self.current_screen.step(event)

    # Render phase of game loop - draw to the screen
    # noinspection PyArgumentList
    def render(self):
        # Update the global frame
        AnimatedGameObject.update_global_frame()

        base_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        base_screen.fill(clear_color[Team.BLUE], (0, 0, RESOLUTION_WIDTH, RESOLUTION_HEIGHT))

        ui_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
        ui_screen = ui_screen.convert_alpha()

        game_screen = self.current_screen.render(ui_screen)

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
            if SESSION.is_network_game:
                SESSION.get(Manager.NETWORK).network_step()

            # Run game logic
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    break

                self.step(event)

            if self.should_quit:
                break

            # Render to the screen
            self.render()
