from terra.engine.gameobject import GameObject
from terra.ui.phasebar import PhaseBar
from terra.constants import Team
from terra.economy.resourcetypes import ResourceType


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, battle, teams):
        super().__init__()

        self.battle = battle
        self.teams = teams

        self.resources = {}
        self.upgrades = {}
        self.phase_bars = {}

        # Initialize resources and upgrades for each team provided
        for team in self.teams:
            self.upgrades[team] = []
            self.phase_bars[team] = PhaseBar(team, self, self.battle)
            self.resources[team] = {}
            for resource in ResourceType:
                self.resources[team][resource] = 10

    def __str__(self):
        return_string = ""
        for team in self.teams:
            return_string = return_string + "{} team with {} carbon, {} minerals, and {} gas.\n"\
                .format(team, self.resources[team][ResourceType.CARBON],
                        self.resources[team][ResourceType.MINERALS],
                        self.resources[team][ResourceType.GAS])
        return return_string

    def add_resources(self, team, new_resources):
        self.resources[team][ResourceType.CARBON] = self.resources[team][ResourceType.CARBON] + new_resources[0]
        self.resources[team][ResourceType.MINERALS] = self.resources[team][ResourceType.MINERALS] + new_resources[1]
        self.resources[team][ResourceType.GAS] = self.resources[team][ResourceType.GAS] + new_resources[2]

    def deduct_resources(self, team, resource_deduction):
        self.resources[team][ResourceType.CARBON] = self.resources[team][ResourceType.CARBON] - resource_deduction[0]
        self.resources[team][ResourceType.MINERALS] = self.resources[team][ResourceType.MINERALS] - resource_deduction[1]
        self.resources[team][ResourceType.GAS] = self.resources[team][ResourceType.GAS] - resource_deduction[2]

    def can_spend_resources(self, team, amounts):
        total_carbon = 0
        total_minerals = 0
        total_gas = 0
        for amount in amounts:
            total_carbon = total_carbon + amount[0]
            total_minerals = total_minerals + amount[0]
            total_gas = total_gas + amount[0]
        return total_carbon < self.resources[team][ResourceType.CARBON] and \
               total_minerals < self.resources[team][ResourceType.MINERALS] and \
               total_gas < self.resources[team][ResourceType.GAS]

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        # for team in Team:
        self.phase_bars[Team.RED].render(game_screen, ui_screen)
