from terra.ai.aiplayer import AIPlayer
from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.mode import Mode
from terra.turn.battlephase import BattlePhase
from terra.ui.battlecursor import BattleCursor
from terra.ui.editorcursor import EditorCursor


# Manager for the current player. Helps handle input, networking, and information that should be hidden
# from the other player(s).
class PlayerManager(GameObject):
    def __init__(self):
        super().__init__()

        all_teams = self.get_manager(Manager.TEAM).get_teams()
        if self.is_network_game():
            self.human_teams = all_teams.copy()
            self.ai_teams = []
        else:
            self.human_teams = all_teams[:1]
            self.ai_teams = all_teams[1:]

        self.cursors = {}
        self.ais = {}
        for team in self.human_teams:
            self.cursors[team] = self.create_cursor(team)

        for team in self.ai_teams:
            self.ais[team] = AIPlayer(team)

        self.active_team = self.get_manager(Manager.NETWORK).team

    def destroy(self):
        super().destroy()
        for team, cursor in self.cursors.items():
            cursor.destroy()

        for team, ai in self.ais.items():
            ai.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.pass_control_to_next_team_from_event)
        event_bus.register_handler(EventType.E_SWAP_ACTIVE_PLAYER, self.pass_control_to_next_team_from_event)
        event_bus.register_handler(EventType.E_ADD_HUMAN, self.add_human)
        event_bus.register_handler(EventType.E_REMOVE_HUMAN, self.remove_human)

    def is_accepting_input(self):
        return self.get_mode() in [Mode.BATTLE, Mode.CAMPAIGN] and not self.get_manager(Manager.NETWORK).networked_game

    def is_hotseat_mode(self):
        return not self.get_manager(Manager.NETWORK).networked_game and len(self.ais.keys()) == 0

    def get_ai_player(self, team):
        return self.ais.get(team, None)

    def is_ai_thinking(self, team):
        ai = self.ais.get(team, None)
        if ai:
            return ai.is_thinking
        else:
            return False

    def create_cursor(self, team):
        if self.get_mode() in [Mode.EDIT]:
            return EditorCursor()
        else:
            return BattleCursor(team)

    # Swap a team from being human-controlled to ai-controlled, and vice-versa
    def swap_team(self, team):
        if team in self.ai_teams:
            ai = self.ais.pop(team)
            ai.destroy()
            self.cursors[team] = self.create_cursor(team)

            self.ai_teams.remove(team)
            self.human_teams.append(team)
        elif team in self.human_teams:
            self.ais[team] = AIPlayer(team)
            cursor = self.cursors.pop(team)
            cursor.destroy()

            self.ai_teams.append(team)
            self.human_teams.remove(team)

            # Prompt the new AI to plan its turn
            publish_game_event(EventType.AI_REPLAN_TURN, {})

    # Add a human player to the first open spot (AI-occupied slot)
    def add_human(self, event=None):
        if len(self.ai_teams) > 0:
            self.swap_team(self.ai_teams[0])

    # Remove a human player from the last occupied spot
    def remove_human(self, event=None):
        if len(self.human_teams) > 0:
            self.swap_team(self.human_teams[-1])

    # Once a player submits their turn, if we're in hotseat / sequential mode,
    # swap the active team to let the other player take a turn
    def pass_control_to_next_team_from_event(self, event):
        if self.is_hotseat_mode():
            self.pass_control_to_next_team()

    def pass_control_to_next_team(self):
        team_manager = self.get_manager(Manager.TEAM)

        current_index = team_manager.get_teams().index(self.active_team) + 1
        if current_index >= len(team_manager.get_teams()):
            current_index = 0

        self.active_team = team_manager.get_teams()[current_index]

    def handle_team_defeated(self, team):
        if self.cursors.get(team, None):
            self.cursors[team].destroy()
            del self.cursors[team]
        elif self.ais.get(team, None):
            self.ais[team].destroy()
            del self.ais[team]

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
