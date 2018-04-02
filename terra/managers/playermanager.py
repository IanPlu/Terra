from terra.battlephase import BattlePhase
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject
from terra.managers.managers import Managers
from terra.mode import Mode
from terra.ui.cursor import Cursor


# Manager for the current player. Helps handle input, networking, and information that should be hidden
# from the other player(s).
class PlayerManager(GameObject):
    def __init__(self):
        super().__init__()

        self.cursors = {}
        for team in Managers.team_manager.get_teams():
            self.cursors[team] = Cursor(team)

        self.active_team = Managers.network_manager.team

    def destroy(self):
        super().destroy()
        for team, cursor in self.cursors.items():
            cursor.destroy()

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG0, self.__debug_swap_active_team__)

    def is_accepting_input(self):
        return Managers.current_mode in [Mode.BATTLE] and not Managers.network_manager.networked_game

    def __debug_swap_active_team__(self):
        current_index = Managers.team_manager.get_teams().index(self.active_team) + 1
        if current_index >= len(Managers.team_manager.get_teams()):
            current_index = 0

        self.active_team = Managers.team_manager.get_teams()[current_index]

    def handle_team_defeated(self, team):
        pass
        self.cursors[team].destroy()
        del self.cursors[team]

        # TODO: What to do when the removed team is the active player?

    def step(self, event):
        super().step(event)

        if Managers.turn_manager.phase == BattlePhase.ORDERS:
            cursor = self.cursors.get(self.active_team)
            if cursor:
                cursor.step(event)

    def get_camera_coords(self):
        cursor = self.cursors.get(self.active_team)
        if cursor:
            return int(cursor.camera_x), int(cursor.camera_y)
        else:
            return 0, 0

    # Return true if the provided rect is within the camera coords
    def is_within_camera_view(self, rect, border_fuzz=48):
        x, y, width, height = rect
        camera_x, camera_y = self.get_camera_coords()
        in_view_x = camera_x - border_fuzz - width <= x <= camera_x + border_fuzz + width + RESOLUTION_WIDTH
        in_view_y = camera_y - border_fuzz - height <= y <= camera_y + border_fuzz + height + RESOLUTION_HEIGHT

        return in_view_x and in_view_y

    def get_cursor_coords(self):
        return int(self.cursors[self.active_team].gx), int(self.cursors[self.active_team].gy)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if Managers.turn_manager.phase == BattlePhase.ORDERS:
            cursor = self.cursors.get(self.active_team)
            if cursor:
                cursor.render(game_screen, ui_screen)
