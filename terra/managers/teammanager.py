from copy import deepcopy

from terra.economy.resourcetypes import ResourceType
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.piece.pieceattributes import base_piece_attributes
from terra.team import Team
from terra.ui.phasebar import PhaseBar
from terra.util.mathutil import clamp
from terra.managers.managers import Managers

# Max number of any given resource a player can hold.
MAX_RESOURCES = 1000


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, teams):
        super().__init__()

        self.teams = []

        self.resources = {}
        self.upgrades = {}
        self.piece_attributes = {}

        self.phase_bars = {}
        self.turn_submitted = {}

        # Initialize resources and upgrades for each team provided
        for team in teams:
            # Parse the team line. Looks like: 'RED 1 2 3', with team color and then resource counts.
            data = team.split(' ')
            team = Team[data[0]]
            self.teams.append(team)

            self.turn_submitted[team] = False
            self.upgrades[team] = []
            self.phase_bars[team] = PhaseBar(team)
            self.resources[team] = {}
            self.resources[team][ResourceType.CARBON] = int(data[1])
            self.resources[team][ResourceType.MINERALS] = int(data[2])
            self.resources[team][ResourceType.GAS] = int(data[3])

            # Set the base values for piece attributes
            self.piece_attributes[team] = deepcopy(base_piece_attributes)

    def __str__(self):
        return_string = ""
        for team in self.teams:
            return_string = return_string + "{} team with {} carbon, {} minerals, and {} gas.\n"\
                .format(team, self.resources[team][ResourceType.CARBON],
                        self.resources[team][ResourceType.MINERALS],
                        self.resources[team][ResourceType.GAS])
        return return_string

    # Query the piece attributes table for an up to date value for an attribute on a piece
    def attr(self, team, piece_type, attribute):
        return self.piece_attributes[team][piece_type][attribute]

    # Serialize team and resource counts for saving
    def serialize_teams(self):
        team_strings = []
        for team in self.teams:
            team_strings.append("{} {} {} {}".format(team.name,
                                                     self.resources[team][ResourceType.CARBON],
                                                     self.resources[team][ResourceType.MINERALS],
                                                     self.resources[team][ResourceType.GAS]))
        return team_strings

    # Add new resources to the specified team. new_resources should be formatted as a tuple: (1, 2, 3)
    def add_resources(self, team, new_resources):
        self.resources[team][ResourceType.CARBON] = clamp(
            self.resources[team][ResourceType.CARBON] + new_resources[0], 0, MAX_RESOURCES)
        self.resources[team][ResourceType.MINERALS] = clamp(
            self.resources[team][ResourceType.MINERALS] + new_resources[1], 0, MAX_RESOURCES)
        self.resources[team][ResourceType.GAS] = clamp(
            self.resources[team][ResourceType.GAS] + new_resources[2], 0, MAX_RESOURCES)

    # Deduct resources from the specified team. resource_deduction should be formatted as a tuple: (1, 2, 3)
    def deduct_resources(self, team, resource_deduction):
        self.resources[team][ResourceType.CARBON] = self.resources[team][ResourceType.CARBON] - resource_deduction[0]
        self.resources[team][ResourceType.MINERALS] = self.resources[team][ResourceType.MINERALS] - resource_deduction[1]
        self.resources[team][ResourceType.GAS] = self.resources[team][ResourceType.GAS] - resource_deduction[2]

    # Return true if the specified team is able to spend the provided list of amounts.
    # Each amount in amounts should be formatted as a tuple: (1, 2, 3)
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

    # Return true if all teams have submitted their turn.
    def check_if_ready_to_submit_turns(self):
        for team in Team:
            if not self.turn_submitted[team]:
                return False
        return True

    # Attempt to submit the turn for the specified team.
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

        if is_event_type(event, E_CLEANUP):
            for team in Team:
                self.turn_submitted[team] = False
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.option == MENU_SUBMIT_TURN:
                self.try_submitting_turn(event.team)
            elif event.option == MENU_SAVE_GAME:
                publish_game_event(E_SAVE_GAME, {})
            elif event.option == MENU_QUIT_BATTLE:
                publish_game_event(E_QUIT_BATTLE, {})

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        self.phase_bars[Managers.player_manager.active_team].render(game_screen, ui_screen)
