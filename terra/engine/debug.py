from terra.engine.gameobject import GameObject
from terra.control.keybindings import Key
from terra.control.inputcontroller import InputAction
from terra.managers.session import Manager


# Controller for initiating debug actions.
class DebugController(GameObject):
    def __init__(self):
        super().__init__()

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG0, self.pass_control)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG1, self.submit_turn_team_1)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG2, self.submit_turn_team_2)

    def pass_control(self):
        self.get_manager(Manager.PLAYER).pass_control_to_next_team(None)

    def submit_turn_team_1(self):
        team_manager = self.get_manager(Manager.TEAM)
        team_manager.try_submitting_turn(team_manager.teams[0])

    def submit_turn_team_2(self):
        team_manager = self.get_manager(Manager.TEAM)
        team_manager.try_submitting_turn(team_manager.teams[1])
