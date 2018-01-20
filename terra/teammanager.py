from terra.engine.gameobject import GameObject
from terra.ui.phasebar import PhaseBar
from terra.constants import Team


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, battle, teams):
        super().__init__()

        self.battle = battle
        self.teams = teams

        self.carbon = {}
        self.minerals = {}
        self.gas = {}
        self.upgrades = {}

        self.phase_bars = {}

        # Initialize resources and upgrades for each team provided
        for team in self.teams:
            self.carbon[team] = 100
            self.minerals[team] = 100
            self.gas[team] = 100
            self.upgrades[team] = []
            self.phase_bars[team] = PhaseBar(team, self, self.battle)

    def __str__(self):
        return_string = ""
        for team in self.teams:
            return_string = return_string + "{} team with {} carbon, {} minerals, and {} gas.\n"\
                .format(team, self.carbon[team], self.minerals[team], self.gas[team])
        return return_string

    def add_resources(self, team, new_resources):
        self.carbon[team] = self.carbon[team] + new_resources[0]
        self.minerals[team] = self.minerals[team] + new_resources[1]
        self.gas[team] = self.gas[team] + new_resources[2]

    def deduct_resources(self, team, resource_deduction):
        self.carbon[team] = self.carbon[team] - resource_deduction[0]
        self.minerals[team] = self.minerals[team] - resource_deduction[1]
        self.gas[team] = self.gas[team] - resource_deduction[2]

    def can_spend_resources(self, team, amounts):
        total_carbon = 0
        total_minerals = 0
        total_gas = 0
        for amount in amounts:
            total_carbon = total_carbon + amount[0]
            total_minerals = total_minerals + amount[0]
            total_gas = total_gas + amount[0]
        return total_carbon < self.carbon[team] and total_minerals < self.minerals[team] and total_gas < self.gas[team]

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        # for team in Team:
        self.phase_bars[Team.RED].render(game_screen, ui_screen)
