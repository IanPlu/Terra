from pygame import Surface, SRCALPHA

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event.event import publish_game_event, EventType
from terra.managers.managers import Managers


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class Battle(GameScreen):
    def __init__(self):
        super().__init__()

    def destroy(self):
        super().destroy()
        Managers.tear_down_managers()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_SAVE_GAME, self.trigger_save_game)

    def trigger_save_game(self, event):
        Managers.save_game_to_file()

    def step(self, event):
        super().step(event)

        Managers.step(event)

    # Generate a screen with the entire map, subsurfaced to the camera area
    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map_screen = Surface((Managers.battle_map.width * GRID_WIDTH, Managers.battle_map.height * GRID_HEIGHT),
                                    SRCALPHA, 32)

        Managers.render(map_screen, ui_screen)

        # Trim the screen to just the camera area
        camera_x, camera_y = Managers.player_manager.get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
