from terra.turn.battlephase import BattlePhase
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.session import Manager
from terra.mode import Mode
from terra.ui.cursor import Cursor
from terra.ai.aiplayer import AIPlayer


# Manager for the current player. Helps handle input, networking, and information that should be hidden
# from the other player(s).
class PlayerManager(GameObject):
    def __init__(self):
        super().__init__()

        self.cursors = {}
        self.ais = {}
        for team in self.get_manager(Manager.TEAM).get_human_teams():
            self.cursors[team] = Cursor(team)

        for team in self.get_manager(Manager.TEAM).get_ai_teams():
            self.ais[team] = AIPlayer(team)

        self.active_team = self.get_manager(Manager.NETWORK).team
        self.hotseat_mode = not self.get_manager(Manager.NETWORK).networked_game and len(self.ais.keys()) == 0

    def destroy(self):
        super().destroy()
        for team, cursor in self.cursors.items():
            cursor.destroy()

        for team, ai in self.ais.items():
            ai.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.pass_control_to_next_team)
        event_bus.register_handler(EventType.E_SWAP_ACTIVE_PLAYER, self.pass_control_to_next_team)

    def is_accepting_input(self):
        return self.get_mode() in [Mode.BATTLE] and not self.get_manager(Manager.NETWORK).networked_game

    # Once a player submits their turn, if we're in hotseat / sequential mode,
    # swap the active team to let the other player take a turn
    def pass_control_to_next_team(self, event):
        if self.hotseat_mode:
            team_manager = self.get_manager(Manager.TEAM)

            current_index = team_manager.get_teams().index(self.active_team) + 1
            if current_index >= len(team_manager.get_teams()):
                current_index = 0

            self.active_team = team_manager.get_teams()[current_index]

    def handle_team_defeated(self, team):
        pass
        self.cursors[team].destroy()
        del self.cursors[team]

    def step(self, event):
        super().step(event)

        if self.get_manager(Manager.TURN).phase == BattlePhase.ORDERS:
            cursor = self.cursors.get(self.active_team)
            if cursor:
                cursor.step(event)

        for _, ai_player in self.ais.items():
            ai_player.step(event)

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

        cursor = self.cursors.get(self.active_team)
        if cursor:
            cursor.render(game_screen, ui_screen)

        for _, ai_player in self.ais.items():
            ai_player.render(game_screen, ui_screen)
