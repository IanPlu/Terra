from copy import deepcopy

from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.attribute import Attribute
from terra.piece.pieceattributes import base_piece_attributes
from terra.piece.piecetype import PieceType
from terra.team.team import Team
from terra.ui.phasebar import PhaseBar
from terra.util.mathutil import clamp

# Max number of any given resource a player can hold.
MAX_RESOURCES = 999


# Manager for resources, upgrades, and piece stats for all teams.
# Handles moving resources around, and handles purchasing + triggering upgrades.
# Is the source of truth for what attributes the pieces from a particular team have.
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

        # Initialize neutral attributes
        self.piece_attributes[Team.NONE] = deepcopy(base_piece_attributes)
        self.resources[Team.NONE] = 100

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

        # Create an archive of all teams at the start of battle.
        # When players lose or are removed, they'll stay in this list.
        self.all_teams = self.teams.copy()

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
        event_bus.register_handler(EventType.E_SUBMIT_TURN, self.set_turn_submitted_from_event)
        event_bus.register_handler(EventType.E_CANCEL_TURN, self.unset_turn_submitted)
        event_bus.register_handler(EventType.E_CLOSE_MENU, self.handle_menu_option)
        event_bus.register_handler(EventType.E_UPGRADE_BUILT, self.purchase_upgrade_from_event)

        event_bus.register_handler(EventType.E_BASE_DESTROYED, self.handle_base_destroyed)
        event_bus.register_handler(EventType.E_CONCEDE, self.handle_concession)
        event_bus.register_handler(EventType.END_PHASE_SPECIAL, self.check_for_remaining_teams)

    def is_accepting_input(self):
        return self.get_mode() in [Mode.BATTLE] and not self.get_manager(Manager.NETWORK).networked_game

    # Get the list of teams currently present in the battle
    def get_teams(self):
        return self.teams

    # Get a list of all teams that have ever been in the battle
    def get_all_teams(self):
        return self.all_teams

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
        publish_game_event(EventType.E_RESOURCES_GAINED, {
            'team': team,
            'new_resources': new_resources
        })

    # Deduct resources from the specified team. resource_deduction should be formatted as a tuple: (1, 2, 3)
    def deduct_resources(self, team, resource_deduction):
        self.resources[team] = max(self.resources[team] - resource_deduction, 0)
        publish_game_event(EventType.E_RESOURCES_LOST, {
            'team': team,
            'resources_lost': resource_deduction
        })

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

    # When an upgrade is purchased, trigger any effects it may have. Modify piece stats, add new abilities, etc.
    def on_upgrade_purchase(self, team, upgrade_type):
        upgrade = base_upgrades[upgrade_type]

        if upgrade.get(UpgradeAttribute.NEW_STAT):
            for piece_type, attributes in upgrade[UpgradeAttribute.NEW_STAT].items():
                for attribute in attributes:
                    self.piece_attributes[team][piece_type][attribute] += \
                        upgrade[UpgradeAttribute.NEW_STAT][piece_type][attribute]

                    # Corner case: heal units when their max HP increases
                    if attribute == Attribute.MAX_HP:
                        for piece in self.get_manager(Manager.PIECE).get_all_pieces_for_team(team, piece_type=piece_type):
                            piece.heal_hp(upgrade[UpgradeAttribute.NEW_STAT][piece_type][attribute])

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

    def has_upgrade(self, team, upgrade):
        return upgrade in self.get_owned_upgrades(team)

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
        if not self.is_turn_submitted(team) and self.get_manager(Manager.PIECE).validate_orders(team):
            self.turn_submitted[team] = True
            publish_game_event(EventType.E_TURN_SUBMITTED, {
                'team': team,
                'orders': self.get_manager(Manager.PIECE).serialize_orders(team)
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
    def set_turn_submitted(self, team):
        self.turn_submitted[team] = True

        if self.check_if_ready_to_submit_turns():
            publish_game_event(EventType.E_ALL_TURNS_SUBMITTED, {})
            for team in self.teams:
                self.turn_submitted[team] = False

    # Mark a turn received from the network as NOT submitted
    def unset_turn_submitted(self, event):
        self.turn_submitted[event.team] = False

    def set_turn_submitted_from_event(self, event):
        self.set_turn_submitted(event.team)

    def cleanup_turn_submission(self, event):
        for team in self.teams:
            self.turn_submitted[team] = False

    # Remove all trace of a team
    def remove_team(self, team):
        del self.resources[team]
        del self.owned_upgrades[team]
        del self.piece_attributes[team]

        self.phase_bars[team].destroy()
        del self.phase_bars[team]
        del self.turn_submitted[team]

        self.teams.remove(team)

        self.get_manager(Manager.PIECE).destroy_all_pieces_for_team(team)
        self.get_manager(Manager.PLAYER).handle_team_defeated(team)

        publish_game_event(EventType.E_TEAM_DEFEATED, {
            'team': team
        })

        self.check_for_remaining_teams()

    def handle_base_destroyed(self, event):
        if event.team is not Team.NONE:
            self.remove_team(event.team)

    def handle_concession(self, event):
        publish_game_event(EventType.E_BASE_DESTROYED, {
            'team': event.team
        })

    def check_for_remaining_teams(self, event=None):
        if len(self.teams) <= 1:
            winning_team = self.get_teams()[0]

            results = {
                'winning_team': winning_team,
                'all_teams': self.get_all_teams(),
                'team_stats': self.get_manager(Manager.STAT).get_results(),
                'winning_pieces': self.get_manager(Manager.PIECE).get_all_pieces_for_team(winning_team),
                'turn': self.get_manager(Manager.TURN).turn,
            }

            publish_game_event(EventType.E_BATTLE_OVER, {
                'results': results
            })

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
            elif event.option == Option.MENU_SWAP_ACTIVE_PLAYER:
                publish_game_event(EventType.E_SWAP_ACTIVE_PLAYER, {})

    def step(self, event):
        super().step(event)

        for team in self.teams:
            self.phase_bars[team].step(event)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        phase_bar = self.phase_bars.get(self.get_manager(Manager.PLAYER).active_team)
        if phase_bar:
            phase_bar.render(game_screen, ui_screen)
