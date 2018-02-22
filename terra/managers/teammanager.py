from copy import deepcopy

from pygame.constants import KEYDOWN

from terra.economy.resourcetypes import ResourceType
from terra.economy.upgrades import base_upgrades
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.keybindings import KB_DEBUG1, KB_DEBUG2
from terra.managers.managers import Managers
from terra.piece.pieceattributes import Attribute
from terra.piece.pieceattributes import base_piece_attributes
from terra.piece.piecetype import PieceType
from terra.team import Team
from terra.ui.phasebar import PhaseBar
from terra.util.mathutil import clamp, add_tuples

# Max number of any given resource a player can hold.
MAX_RESOURCES = 1000


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, teams):
        super().__init__()

        self.teams = []

        self.resources = {}
        self.owned_upgrades = {}
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
            self.phase_bars[team] = PhaseBar(team)
            self.resources[team] = {}
            self.resources[team][ResourceType.CARBON] = int(data[1])
            self.resources[team][ResourceType.MINERALS] = int(data[2])
            self.resources[team][ResourceType.GAS] = int(data[3])

            # Set the base values for piece attributes
            self.piece_attributes[team] = deepcopy(base_piece_attributes)

            # Set the base upgrade tree for each piece type
            self.owned_upgrades[team] = []
            for piece_type in PieceType:
                for upgrade_type, upgrade in base_upgrades.items():
                    if upgrade["bought_by"] == piece_type and upgrade["tier"] == 1:
                        self.piece_attributes[team][piece_type][Attribute.PURCHASEABLE_UPGRADES].append(upgrade_type)

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

    # Add an upgrade to a team, triggering any changes to the units + upgrade tree as necessary.
    def purchase_upgrade(self, team, upgrade_type):
        print("Purchased upgrade: " + upgrade_type.name)

        # 1. Add the chosen upgrade to the team
        self.owned_upgrades[team].append(upgrade_type)

        # 2. Trigger the 'on-purchase' effect
        self.on_upgrade_purchase(team, upgrade_type)

        # 3. Add any upgrades to the purchasable list that are now available (prereqs met)
        bought_by_piece_type = base_upgrades[upgrade_type]["bought_by"]
        new_unlocks = base_upgrades[upgrade_type]["unlocks"]
        if len(new_unlocks):
            self.piece_attributes[team][bought_by_piece_type][Attribute.PURCHASEABLE_UPGRADES] += new_unlocks

        # 4. Remove the chosen upgrade from the purchaseable list
        self.piece_attributes[team][bought_by_piece_type][Attribute.PURCHASEABLE_UPGRADES].remove(upgrade_type)

    def on_upgrade_purchase(self, team, upgrade_type):
        upgrade = base_upgrades[upgrade_type]

        if upgrade.get("new_stat"):
            for piece_type, attributes in upgrade["new_stat"].items():
                for attribute in attributes:
                    Managers.team_manager.piece_attributes[team][piece_type][attribute] += \
                        upgrade["new_stat"][piece_type][attribute]

        if upgrade.get("new_type"):
            for piece_type, attributes in upgrade["new_type"].items():
                for attribute in attributes:
                    Managers.team_manager.piece_attributes[team][piece_type][attribute] = \
                        upgrade["new_type"][piece_type][attribute]

        if upgrade.get("new_costs"):
            for piece_type, attributes in upgrade["new_costs"].items():
                for attribute in attributes:
                    existing_price = Managers.team_manager.piece_attributes[team][piece_type][attribute]
                    new_price = upgrade["new_costs"][piece_type][attribute]
                    Managers.team_manager.piece_attributes[team][piece_type][attribute] = \
                        add_tuples(new_price, existing_price)

        if upgrade.get("new_attack_multiplier"):
            for piece_type, enemy_piece_types in upgrade["new_attack_multiplier"].items():
                for enemy_piece_type in enemy_piece_types:
                    Managers.team_manager.piece_attributes[team][piece_type][Attribute.ATTACK_MULTIPLIER][enemy_piece_type] = \
                        upgrade["new_attack_multiplier"][piece_type][enemy_piece_type]

    def get_owned_upgrades(self, team):
        return self.owned_upgrades[team]

    # Return true if all teams have submitted their turn.
    def check_if_ready_to_submit_turns(self):
        for team in Team:
            if not self.turn_submitted[team]:
                return False
        return True

    # Attempt to submit the turn for the specified team. Orders are validated before submission is allowed.
    def try_submitting_turn(self, team):
        if not self.turn_submitted[team] and Managers.piece_manager.validate_orders(team):
            self.turn_submitted[team] = True
            publish_game_event(E_TURN_SUBMITTED, {
                'team': team,
                'orders': Managers.piece_manager.serialize_orders(team)
            })

            if self.check_if_ready_to_submit_turns():
                publish_game_event(E_ALL_TURNS_SUBMITTED, {})
                for team in Team:
                    self.turn_submitted[team] = False
        else:
            self.turn_submitted[team] = False
            publish_game_event(E_CANCEL_TURN_SUBMITTED, {
                'team': team
            })

    # Mark a turn received from the network as submitted.
    def set_turn_submitted(self, team):
        self.turn_submitted[team] = True

        if self.check_if_ready_to_submit_turns():
            publish_game_event(E_ALL_TURNS_SUBMITTED, {})
            for team in Team:
                self.turn_submitted[team] = False

    def step(self, event):
        super().step(event)

        for team in Team:
            self.phase_bars[team].step(event)

        if is_event_type(event, E_CLEANUP):
            for team in Team:
                self.turn_submitted[team] = False
        elif is_event_type(event, E_SUBMIT_TURN):
            self.set_turn_submitted(event.team)
        elif is_event_type(event, E_CLOSE_MENU) and event.option:
            if event.option == MENU_SUBMIT_TURN:
                self.try_submitting_turn(event.team)
            elif event.option == MENU_SAVE_GAME:
                publish_game_event(E_SAVE_GAME, {})
            elif event.option == MENU_QUIT_BATTLE:
                publish_game_event(E_QUIT_BATTLE, {})
        elif is_event_type(event, E_UPGRADE_BUILT):
            self.purchase_upgrade(event.team, event.new_upgrade_type)
        elif event.type == KEYDOWN:
            if event.key in KB_DEBUG1:
                self.try_submitting_turn(Team.RED)
            elif event.key in KB_DEBUG2:
                self.try_submitting_turn(Team.BLUE)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        self.phase_bars[Managers.player_manager.active_team].render(game_screen, ui_screen)
