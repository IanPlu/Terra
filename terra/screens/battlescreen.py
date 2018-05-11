from threading import Timer

from pygame import Surface, SRCALPHA

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event.event import EventType
from terra.managers.session import SESSION, Session, Manager
from terra.settings import Setting, SETTINGS


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class BattleScreen(GameScreen):
    def __init__(self, map_name=None, map_type=None, create_session=True):
        super().__init__()
        # Only create the session if nothing else has (e.g. the network lobby)
        if create_session:
            Session.set_up_local_game(map_name, map_type)

        # Begin scheduling autosaves
        if SETTINGS.get(Setting.AUTOSAVE_INTERVAL) > 0:
            self.autosave()

    def destroy(self):
        super().destroy()
        if SESSION:
            SESSION.reset()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_SAVE_GAME, self.trigger_save_game)

    def trigger_save_game(self, event):
        SESSION.save_game_to_file()

    def autosave(self):
        if SESSION.is_active():
            timer = Timer(SETTINGS.get(Setting.AUTOSAVE_INTERVAL), self.autosave)
            timer.daemon = True
            timer.start()

            SESSION.save_game_to_file(autosave=True)

    def step(self, event):
        super().step(event)

        SESSION.step(event)

    # Generate a screen with the entire map, subsurfaced to the camera area
    def render(self, ui_screen):
        super().render(ui_screen)

        # Generate a screen of the size of the map
        map = self.get_manager(Manager.MAP)
        map_screen = Surface((map.width * GRID_WIDTH, map.height * GRID_HEIGHT), SRCALPHA, 32)

        SESSION.render(map_screen, ui_screen)

        # Trim the screen to just the camera area
        camera_x, camera_y = self.get_manager(Manager.PLAYER).get_camera_coords()
        return map_screen.subsurface((camera_x, camera_y,
                                      min(CAMERA_WIDTH, map_screen.get_size()[0]),
                                      min(CAMERA_HEIGHT, map_screen.get_size()[1])))
