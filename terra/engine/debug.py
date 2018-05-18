from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradetype import UpgradeType
from terra.engine.gameobject import GameObject
from terra.managers.session import Manager
from terra.mode import Mode
from terra.constants import DEBUG_COMMANDS


# Controller for initiating debug actions.
class DebugController(GameObject):
    def __init__(self):
        super().__init__()

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG0, self.pass_control)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG1, self.submit_turn_team_1)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG2, self.submit_turn_team_2)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG5, self.research_and_money)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG4, self.win_battle)

    def is_accepting_input(self):
        return self.get_mode() in [Mode.BATTLE, Mode.CAMPAIGN] and DEBUG_COMMANDS

    # Manually swap control to the next player
    def pass_control(self):
        self.get_manager(Manager.PLAYER).pass_control_to_next_team()

    # Manually submit team 1's turn (respecting order validation)
    def submit_turn_team_1(self):
        team_manager = self.get_manager(Manager.TEAM)
        team_manager.try_submitting_turn(team_manager.teams[0])

    # Manually submit team 2's turn (respecting order validation)
    def submit_turn_team_2(self):
        team_manager = self.get_manager(Manager.TEAM)
        team_manager.try_submitting_turn(team_manager.teams[1])

    # Win the game for the current active team
    def win_battle(self):
        team_manager = self.get_manager(Manager.TEAM)
        for team in team_manager.teams:
            if team != self.get_manager(Manager.PLAYER).active_team:
                team_manager.remove_team(team)

    # Give each team lots of money, research all units
    def research_and_money(self):
        team_manager = self.get_manager(Manager.TEAM)
        unit_research = [
            UpgradeType.RESEARCH_GUARDIAN,
            UpgradeType.RESEARCH_BOLTCASTER,
            UpgradeType.RESEARCH_BANSHEE,
            UpgradeType.RESEARCH_TITAN,
            UpgradeType.RESEARCH_EARTHRENDER,
            UpgradeType.RESEARCH_DEMON,
        ]

        for team in team_manager.teams:
            team_manager.add_resources(team, 500)

            for upgrade in unit_research:
                if not team_manager.has_upgrade(team, upgrade):
                    team_manager.purchase_upgrade(team, upgrade)
