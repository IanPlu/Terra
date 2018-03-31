from copy import deepcopy

from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.managers import Managers
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.attribute import Attribute
from terra.piece.pieceattributes import base_piece_attributes
from terra.piece.piecetype import PieceType
from terra.team import Team
from terra.ui.phasebar import PhaseBar
from terra.util.mathutil import clamp

# Max number of any given resource a player can hold.
MAX_RESOURCES = 1000


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, teams, upgrades):
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
            self.resources[team] = int(data[1])

            # Set the base values for piece attributes
            self.piece_attributes[team] = deepcopy(base_piece_attributes)

        # Initialize upgrades
        for team_upgrades in upgrades:
            # Parse the upgrades. Looks like: 'RED|UPGRADE1 UPGRADE2', with team color and then upgrade names.
            upgrade_data = team_upgrades.split('|')
            team = Team[upgrade_data[0]]

            upgrade_list = upgrade_data[1].split(' ')

            # Set the base upgrade tree for each piece type
            self.owned_upgrades[team] = []
            for piece_type in PieceType:
                for upgrade_type, upgrade in base_upgrades.items():
                    if piece_type in upgrade[UpgradeAttribute.BOUGHT_BY] and upgrade[UpgradeAttribute.TIER] == 1:
                        self.piece_attributes[team][piece_type][Attribute.PURCHASEABLE_UPGRADES].append(upgrade_type)

            # Apply any already owned upgrades
            for upgrade in upgrade_list:
                if upgrade:
                    self.purchase_upgrade(team, UpgradeType[upgrade])

    def destroy(self):
        super().destroy()
        for _, bar in self.phase_bars.items():
            bar.destroy()

    def __str__(self):
        return_string = ""
        for team in self.teams:
            return_string = return_string + "{} team with {} resources.\n"\
                .format(team, self.resources[team])
        return return_string

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_CLEANUP, self.cleanup_turn_submission)
        event_bus.register_handler(EventType.E_SUBMIT_TURN, self.set_turn_submitted)
        event_bus.register_handler(EventType.E_CANCEL_TURN, self.unset_turn_submitted)
        event_bus.register_handler(EventType.E_CLOSE_MENU, self.handle_menu_option)
        event_bus.register_handler(EventType.E_UPGRADE_BUILT, self.purchase_upgrade_from_event)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG1, self.__debug_submit_turn_t1__)
        input_handler.register_handler(InputAction.PRESS, Key.DEBUG2, self.__debug_submit_turn_t2__)

    def is_accepting_input(self):
        return Managers.current_mode in [Mode.BATTLE] and not Managers.network_manager.networked_game

    def __debug_submit_turn_t1__(self):
        self.try_submitting_turn(self.teams[0])

    def __debug_submit_turn_t2__(self):
        self.try_submitting_turn(self.teams[1])

    # Get the list of teams present in the battle
    def get_teams(self):
        return self.teams

    # Query the piece attributes table for an up to date value for an attribute on a piece
    def attr(self, team, piece_type, attribute):
        return self.piece_attributes[team][piece_type].get(attribute,
                                                           self.piece_attributes[team][PieceType.DEFAULT][attribute])

    # Serialize team, resource counts, and upgrades for saving
    def serialize_teams(self):
        team_strings = []
        for team in self.teams:
            team_strings.append("{} {}".format(team.name, self.resources[team]))
        return team_strings

    def serialize_upgrades(self):
        team_upgrade_strings = []
        for team in self.teams:
            team_upgrades = str(team.name) + "|"
            for upgrade in self.owned_upgrades[team]:
                team_upgrades += upgrade.name + " "
            team_upgrade_strings.append(team_upgrades)

        return team_upgrade_strings

    # Add new resources to the specified team. new_resources should be formatted as a tuple: (1, 2, 3)
    def add_resources(self, team, new_resources):
        self.resources[team] = clamp(self.resources[team] + new_resources, 0, MAX_RESOURCES)
        Managers.combat_logger.log_resource_acquisition(new_resources, team)

    # Deduct resources from the specified team. resource_deduction should be formatted as a tuple: (1, 2, 3)
    def deduct_resources(self, team, resource_deduction):
        self.resources[team] = max(self.resources[team] - resource_deduction, 0)
        Managers.combat_logger.log_resource_acquisition(-resource_deduction, team)

    # Return true if the specified team is able to spend the provided list of amounts.
    # Each amount in amounts should be formatted as a tuple: (1, 2, 3)
    def can_spend_resources(self, team, amounts):
        total_spent = 0
        for amount in amounts:
            total_spent += amount

        return total_spent <= self.resources[team]

    # Add an upgrade to a team, triggering any changes to the units + upgrade tree as necessary.
    def purchase_upgrade(self, team, upgrade_type):
        # 1. Add the chosen upgrade to the team
        self.owned_upgrades[team].append(upgrade_type)

        # 2. Trigger the 'on-purchase' effect
        self.on_upgrade_purchase(team, upgrade_type)

        # 3. Add any upgrades to the purchasable list that are now available (prereqs met)
        new_unlocks = base_upgrades[upgrade_type][UpgradeAttribute.UNLOCKS]
        if len(new_unlocks):
            for new_unlock in new_unlocks:
                for bought_by_piece in base_upgrades[new_unlock][UpgradeAttribute.BOUGHT_BY]:
                    self.piece_attributes[team][bought_by_piece][Attribute.PURCHASEABLE_UPGRADES].append(new_unlock)

        # 4. Remove the chosen upgrade from the purchaseable list
        for bought_by_piece in base_upgrades[upgrade_type][UpgradeAttribute.BOUGHT_BY]:
            self.piece_attributes[team][bought_by_piece][Attribute.PURCHASEABLE_UPGRADES].remove(upgrade_type)

        Managers.combat_logger.log_upgrade(upgrade_type, team)

    def on_upgrade_purchase(self, team, upgrade_type):
        upgrade = base_upgrades[upgrade_type]

        if upgrade.get(UpgradeAttribute.NEW_STAT):
            for piece_type, attributes in upgrade[UpgradeAttribute.NEW_STAT].items():
                for attribute in attributes:
                    self.piece_attributes[team][piece_type][attribute] += \
                        upgrade[UpgradeAttribute.NEW_STAT][piece_type][attribute]

        if upgrade.get(UpgradeAttribute.NEW_TYPE):
            for piece_type, attributes in upgrade[UpgradeAttribute.NEW_TYPE].items():
                for attribute in attributes:
                    self.piece_attributes[team][piece_type][attribute] = \
                        upgrade[UpgradeAttribute.NEW_TYPE][piece_type][attribute]

        if upgrade.get(UpgradeAttribute.NEW_ATTACK_MULTIPLIER):
            for piece_type, enemy_piece_archetypes in upgrade[UpgradeAttribute.NEW_ATTACK_MULTIPLIER].items():
                for enemy_piece_archetype in enemy_piece_archetypes:
                    self.piece_attributes[team][piece_type][Attribute.ATTACK_MULTIPLIER][enemy_piece_archetype] = \
                        upgrade[UpgradeAttribute.NEW_ATTACK_MULTIPLIER][piece_type][enemy_piece_archetype]

        if upgrade.get(UpgradeAttribute.NEW_BUILDABLE):
            for piece_type, new_pieces in upgrade[UpgradeAttribute.NEW_BUILDABLE].items():
                self.piece_attributes[team][piece_type][Attribute.BUILDABLE_PIECES].extend(new_pieces)

    def get_owned_upgrades(self, team):
        return self.owned_upgrades[team]

    def purchase_upgrade_from_event(self, event):
        self.purchase_upgrade(event.team, event.new_upgrade_type)

    # Return true if all teams have submitted their turn.
    def check_if_ready_to_submit_turns(self):
        for team in self.teams:
            if not self.turn_submitted[team]:
                return False
        return True

    def is_turn_submitted(self, team):
        return self.turn_submitted[team]

    # Attempt to submit the turn for the specified team. Orders are validated before submission is allowed.
    def try_submitting_turn(self, team):
        if not self.is_turn_submitted(team) and Managers.piece_manager.validate_orders(team):
            self.turn_submitted[team] = True
            publish_game_event(EventType.E_TURN_SUBMITTED, {
                'team': team,
                'orders': Managers.piece_manager.serialize_orders(team)
            })

            if self.check_if_ready_to_submit_turns():
                publish_game_event(EventType.E_ALL_TURNS_SUBMITTED, {})
                for team in self.teams:
                    self.turn_submitted[team] = False

    # Cancel turn submission for the specified team
    def cancel_turn_submission(self, team):
        if self.is_turn_submitted(team):
            self.turn_submitted[team] = False
            publish_game_event(EventType.E_CANCEL_TURN_SUBMITTED, {
                'team': team
            })

    # Mark a turn received from the network as submitted.
    def set_turn_submitted(self, event):
        self.turn_submitted[event.team] = True

        if self.check_if_ready_to_submit_turns():
            publish_game_event(EventType.E_ALL_TURNS_SUBMITTED, {})
            for team in self.teams:
                self.turn_submitted[team] = False

    # Mark a turn received from the network as NOT submitted
    def unset_turn_submitted(self, event):
        self.turn_submitted[event.team] = False

    def cleanup_turn_submission(self, event):
        for team in self.teams:
            self.turn_submitted[team] = False

    def handle_menu_option(self, event):
        if event.option:
            if event.option == Option.MENU_SUBMIT_TURN:
                self.try_submitting_turn(event.team)
            elif event.option == Option.MENU_REVISE_TURN:
                self.cancel_turn_submission(event.team)
            elif event.option == Option.MENU_SAVE_GAME:
                publish_game_event(EventType.E_SAVE_GAME, {})
            elif event.option == Option.MENU_QUIT_BATTLE:
                publish_game_event(EventType.E_QUIT_BATTLE, {})
            elif event.option == Option.MENU_CONCEDE:
                publish_game_event(EventType.E_CONCEDE, {
                    'team': event.team
                })

    def step(self, event):
        super().step(event)

        for team in self.teams:
            self.phase_bars[team].step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        self.phase_bars[Managers.player_manager.active_team].render(game_screen, ui_screen)
