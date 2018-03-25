from pygame import Surface, SRCALPHA

from terra.constants import GRID_WIDTH, GRID_HEIGHT, CAMERA_WIDTH, CAMERA_HEIGHT
from terra.engine.gamescreen import GameScreen
from terra.event import is_event_type, publish_game_event, E_BASE_DESTROYED, E_SAVE_GAME, END_PHASE_SPECIAL, \
    E_BATTLE_OVER, E_PLAYER_CONCEDED
from terra.managers.managers import Managers
from terra.resources.assetloading import AssetType


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class Battle(GameScreen):
    def __init__(self, map_name="key_range.map", address=None, is_host=False, map_type=AssetType.MAP):
        super().__init__()

        # Store bases as they're destroyed.
        self.bases_destroyed = set()

        Managers.initialize_managers(map_name, address, is_host, map_type)

    def end_battle(self):
        results = {
            'bases_destroyed': self.bases_destroyed,
            'team_stats': Managers.stat_manager.get_results(),
            'teams': Managers.team_manager.get_teams(),
        }

        publish_game_event(E_BATTLE_OVER, results)

    def step(self, event):
        super().step(event)

        Managers.step(event)

        if is_event_type(event, E_BASE_DESTROYED):
            self.bases_destroyed.add(event.team)
        elif is_event_type(event, E_SAVE_GAME):
            Managers.save_game_to_file()
        elif is_event_type(event, END_PHASE_SPECIAL):
            if len(self.bases_destroyed) > 0:
                self.end_battle()
        elif is_event_type(event, E_PLAYER_CONCEDED):
            self.bases_destroyed.add(event.team)
            self.end_battle()

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
