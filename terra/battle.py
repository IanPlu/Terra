from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event import *
from terra.managers.managers import Managers


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class Battle(GameScreen):
    def __init__(self, map_name="key_range.map", address=None, is_host=False):
        super().__init__()

        Managers.initialize_managers(map_name, address, is_host)

    def check_for_victory(self, event):
        print("A base has been destroyed. The game is over!: " + str(event))

    def step(self, event):
        super().step(event)

        Managers.step(event)

        if is_event_type(event, E_BASE_DESTROYED):
            self.check_for_victory(event)
        elif is_event_type(event, E_SAVE_GAME):
            Managers.save_game_to_file()

    # Generate a screen with the entire map, subsurfaced to the camera area
    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map_screen = pygame.Surface((Managers.battle_map.width * GRID_WIDTH, Managers.battle_map.height * GRID_HEIGHT),
                                    pygame.SRCALPHA, 32)

        Managers.render(map_screen, ui_screen)

        # Trim the screen to just the camera area
        camera_x, camera_y = Managers.player_manager.get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
