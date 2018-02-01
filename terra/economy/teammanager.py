from terra.engine.gameobject import GameObject
from terra.ui.phasebar import PhaseBar
from terra.constants import Team
from terra.economy.resourcetypes import ResourceType
from terra.util.mathutil import clamp
from terra.event import *

MAX_RESOURCES = 1000


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, battle, effects_manager, teams):
        super().__init__()

        self.battle = battle
        self.teams = teams
        self.effects_manager = effects_manager

        self.resources = {}
        self.upgrades = {}
        self.phase_bars = {}
        self.turn_submitted = {}

        # Initialize resources and upgrades for each team provided
        for team in self.teams:
            self.turn_submitted[team] = False
            self.upgrades[team] = []
            self.phase_bars[team] = PhaseBar(team, self, self.battle, self.effects_manager)
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
        self.resources[team][ResourceType.CARBON] = clamp(self.resources[team][ResourceType.CARBON] + new_resources[0], 0, MAX_RESOURCES)
        self.resources[team][ResourceType.MINERALS] = clamp(self.resources[team][ResourceType.MINERALS] + new_resources[1], 0, MAX_RESOURCES)
        self.resources[team][ResourceType.GAS] = clamp(self.resources[team][ResourceType.GAS] + new_resources[2], 0, MAX_RESOURCES)

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
        return total_carbon <= self.resources[team][ResourceType.CARBON] and \
               total_minerals <= self.resources[team][ResourceType.MINERALS] and \
               total_gas <= self.resources[team][ResourceType.GAS]

    def check_if_ready_to_submit_turns(self):
        for team in Team:
            if not self.turn_submitted[team]:
                return False
        return True

    def try_submitting_turn(self, team):
        # TODO: Validate orders here

        if not self.turn_submitted[team]:
            self.turn_submitted[team] = True
            if self.check_if_ready_to_submit_turns():
                publish_game_event(E_ALL_TURNS_SUBMITTED, {})
                for team in Team:
                    self.turn_submitted[team] = False
        else:
            self.turn_submitted[team] = False

    def step(self, event):
        super().step(event)

        for team in Team:
            self.phase_bars[team].step(event)

        if is_event_type(event, E_SUBMIT_TURN):
            self.try_submitting_turn(event.team)
        elif is_event_type(event, E_CLEANUP):
            for team in Team:
                self.turn_submitted[team] = False

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        self.phase_bars[self.battle.active_team].render(game_screen, ui_screen)
