from pygame.constants import KEYDOWN

from terra.battlephase import BattlePhase
from terra.engine.gameobject import GameObject
from terra.keybindings import KB_DEBUG0
from terra.managers.managers import Managers
from terra.mode import Mode
from terra.team import Team
from terra.ui.cursor import Cursor


# Manager for the current player. Helps handle input, networking, and information that should be hidden
# from the other player(s).
class PlayerManager(GameObject):
    def __init__(self):
        super().__init__()

        self.cursors = {}
        for team in Managers.team_manager.teams:
            self.cursors[team] = Cursor(team)

        self.active_team = Managers.network_manager.team

    def step(self, event):
        super().step(event)

        if Managers.turn_manager.phase == BattlePhase.ORDERS:
            self.cursors[self.active_team].step(event)

        if event.type == KEYDOWN and Managers.current_mode in [Mode.BATTLE]:
            if event.key in KB_DEBUG0:
                if self.active_team == Team.RED:
                    self.active_team = Team.BLUE
                elif self.active_team == Team.BLUE:
                    self.active_team = Team.RED

    def get_camera_coords(self):
        return int(self.cursors[self.active_team].camera_x), int(self.cursors[self.active_team].camera_y)

    def get_cursor_coords(self):
        return int(self.cursors[self.active_team].gx), int(self.cursors[self.active_team].gy)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if Managers.turn_manager.phase == BattlePhase.ORDERS:
            self.cursors[self.active_team].render(game_screen, ui_screen)
