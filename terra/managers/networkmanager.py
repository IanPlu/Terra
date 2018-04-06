import random
import select
import socket
from ast import literal_eval

from terra.constants import SERVER_PORT
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType, publish_game_event_from_network
from terra.managers.managers import Managers
from terra.network.messagecode import MessageCode
from terra.piece.orders import deserialize_order
from terra.settings import SETTINGS, Setting
from terra.team import Team


# Manager for synchronizing and messaging the game state back and forth in a network game.
class NetworkManager(GameObject):
    def __init__(self, address, open_teams, is_host=True):
        super().__init__()

        self.team = Team.NONE
        if open_teams:
            self.open_teams = open_teams
        else:
            self.open_teams = []
        self.filled_teams = {}

        if not address:
            # Don't do any networking.
            self.networked_game = False
            self.team = self.get_next_open_team()
        else:
            self.networked_game = True

            self.is_host = is_host
            self.address = address
            self.server_port = SERVER_PORT

            self.nickname = SETTINGS.get(Setting.NICKNAME)

            self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.read_list = [self.connection]
            self.write_list = []

            self.map_data = None

            if self.is_host:
                # Set ourselves up as the server / host
                self.connection.bind(("localhost", SERVER_PORT))
                self.clients = []

                # Automatically take the first team available
                self.team = self.get_next_open_team(self.nickname)
            else:
                # Set ourselves up as a client, connecting to the host
                self.client_port = random.randrange(7008, 7999)
                self.connection.bind(("localhost", self.client_port))

                # We don't know our team or what map we're on yet!
                # Wait for a message to come back telling us who and where we are
                self.connect_to_host()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)
        event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.submit_turn)
        event_bus.register_handler(EventType.E_CANCEL_TURN_SUBMITTED, self.cancel_turn_submission)
        event_bus.register_handler(EventType.E_CONCEDE, self.concede)
        event_bus.register_handler(EventType.E_START_BATTLE, self.start_battle)
        event_bus.register_handler(EventType.E_QUIT_BATTLE, self.quit_battle)
        event_bus.register_handler(EventType.E_EXIT_RESULTS, self.quit_results)

    def is_accepting_events(self):
        return self.networked_game

    def get_next_open_team(self, nickname=None, notify=True):
        team = self.open_teams[0]
        self.fill_team(team, nickname)
        if notify:
            self.send_message(MessageCode.TEAM_FILLED, team, str(nickname))

        return team

    def fill_team(self, team, nickname):
        if team in self.open_teams:
            self.open_teams.remove(team)
        self.filled_teams[team] = nickname

        if len(self.open_teams) == 0:
            publish_game_event(EventType.E_ALL_TEAMS_FILLED, {})

    def remove_team(self, team, notify=True):
        self.open_teams.append(team)
        del self.filled_teams[team]

        publish_game_event(EventType.E_TEAM_LEFT, {
            'team': team
        })

        if notify:
            self.send_message(MessageCode.TEAM_EMPTIED, team, "")

    # Initialize a connection to the host
    def connect_to_host(self):
        self.send_message(MessageCode.NEW_CONNECTION, Team.NONE, str(self.nickname))

        # Block until we receive the map information back from the host.
        while not self.map_data:
            try:
                self.network_step(blocking=True)
            except Exception as err:
                print("Failed to connect to host. Aborting.")
                Managers.error_logger.exception("Failed to connect to host", err)
                Managers.tear_down_managers()
                publish_game_event(EventType.E_QUIT_BATTLE, {})
                break

    def disconnect_from_host(self, notify_host=True):
        if notify_host:
            self.send_message(MessageCode.DROP_CONNECTION, self.team, self.nickname)

        self.connection.close()
        self.networked_game = False
        publish_game_event(EventType.NETWORK_DISCONNECTED_FROM_HOST, {
            'team': self.team
        })

    # Send the entire game state to clients. Same format as loading it from a file.
    # Also, assign that client a team from the currently open teams
    def send_game_state_to_client(self, game_state, team):
        self.send_message(MessageCode.SET_TEAM, self.team, str(team))
        self.send_message(MessageCode.SET_GAME_STATE, self.team, game_state)
        self.send_message(MessageCode.TEAM_FILLED, self.team, self.nickname)

    # Handle incoming messages from either the client or the host
    def handle_message(self, message, address):
        print("Received message '{}' from '{}'".format(str(message.decode()), str(address)))

        command = message.decode()[:9]
        team = Team(message.decode()[9:14])
        body = message.decode()[14:]

        if command == MessageCode.NEW_CONNECTION.value:
            print("Connection request from: " + str(address))
            self.clients.append(address)
            client_team = self.get_next_open_team(body)

            # TODO: What if Managers aren't initialized?
            self.send_game_state_to_client(Managers.save_game_to_string()[0], client_team.value)

            publish_game_event(EventType.NETWORK_CLIENT_CONNECTED, {
                'team': self.team,
                'nickname': str(body)
            })
        elif command == MessageCode.DROP_CONNECTION.value:
            print("Connection dropped for: " + str(address))
            self.clients.remove(address)
            self.remove_team(team)
            publish_game_event(EventType.NETWORK_CLIENT_DISCONNECTED, {
                'team': self.team,
                'nickname': str(body)
            })
        elif command == MessageCode.END_CONNECTION.value:
            print("Connection ended from: " + str(address))
            self.connection.close()
            self.quit_network_game(notify_host=False)
            publish_game_event_from_network(EventType.E_QUIT_BATTLE, {})
        elif command == MessageCode.SET_ORDERS.value:
            print("Setting orders from net msg: " + str(body))
            orders = literal_eval(body)

            parsed_orders = {}
            for coord, order in orders.items():
                if order:
                    parsed_orders[coord] = deserialize_order(order)
                else:
                    parsed_orders[coord] = None

            Managers.piece_manager.set_orders(team, parsed_orders)
            publish_game_event_from_network(EventType.E_SUBMIT_TURN, {
                'team': team
            })
        elif command == MessageCode.SET_TEAM.value:
            print("Receiving our assigned team from host: " + str(body))
            self.team = Team(body)
        elif command == MessageCode.CANCEL_ORDERS.value:
            print("Canceling orders from net msg:" + str(body))
            publish_game_event_from_network(EventType.E_CANCEL_TURN, {
                'team': team
            })
        elif command == MessageCode.PLAYER_CONCEDED.value:
            print("Player has conceded from net msg: " + str(body))
            publish_game_event_from_network(EventType.E_CONCEDE, {
                'team': team
            })
        elif command == MessageCode.SET_GAME_STATE.value:
            print("Setting game state from net msg: " + str(body))
            self.map_data = body
        elif command == MessageCode.START_BATTLE.value:
            print("Network has started the battle")
            publish_game_event_from_network(EventType.E_START_NETWORK_BATTLE, {})
        elif command == MessageCode.TEAM_FILLED.value:
            print("Got filled team from network")
            self.fill_team(team, body)
        elif command == MessageCode.TEAM_EMPTIED.value:
            print("Emptied team from network")
            self.remove_team(team, notify=False)

    # Send the provided message on to the other player
    def send_message(self, code, team, message):
        full_message = (code.value + team.value + message).encode()

        attempt = 1
        attempt_limit = 3

        while attempt < attempt_limit:
            try:
                if self.is_host:
                    for client in self.clients:
                        self.connection.sendto(full_message, client)
                else:
                    self.connection.sendto(full_message, (self.address, self.server_port))

                break
            except Exception as err:
                attempt += 1
                Managers.error_logger.warn("Caught exception while sending message '{}'. Retry {} of {}.".format(full_message, attempt, attempt_limit))

                if attempt > attempt_limit:
                    Managers.error_logger.exception("Too many attempts failed. Aborting sending message '{}'".format(full_message), err)
                    # For now, just abort the game
                    self.quit_network_game()

    # Cleanly exit out of a networked game
    def quit_network_game(self, notify_host=True):
        print("Exiting network game")
        if self.is_host:
            # Close down the game, notify clients
            self.send_message(MessageCode.END_CONNECTION, self.team, "")
        else:
            # Disconnect from the host
            self.disconnect_from_host(notify_host)

        self.networked_game = False
        publish_game_event(EventType.E_NETWORKING_ERROR, {})

    # Check for any new network messages
    # Maintain a buffer of messages to send and send them in the step func, but add to the buffer in the while 1 loop
    def network_step(self, blocking=False):
        if self.networked_game:
            try:
                readable, writable, exceptional = (
                    select.select(self.read_list, self.write_list, [], 0)
                )

                for f in readable:
                    if f is self.connection:
                        message, address = f.recvfrom(2048)
                        self.handle_message(message, address)
            except Exception as err:
                print("Caught exception during networking step. ")
                Managers.error_logger.exception("Caught exception during network step.", err)
                self.quit_network_game()

                # If an error occurs when we're blocking for this message, need to bubble it upward
                if blocking:
                    raise err

    def submit_turn(self, event):
        self.send_message(MessageCode.SET_ORDERS, event.team, str(event.orders))

    def cancel_turn_submission(self, event):
        self.send_message(MessageCode.CANCEL_ORDERS, event.team, "")

    def concede(self, event):
        self.send_message(MessageCode.PLAYER_CONCEDED, event.team, "")

    def start_battle(self, event):
        self.send_message(MessageCode.START_BATTLE, event.team, "")
        publish_game_event(EventType.E_START_NETWORK_BATTLE, {})

    def quit_battle(self, event):
        self.quit_network_game(notify_host=True)

    def quit_results(self, event):
        self.quit_network_game(notify_host=False)

    def render(self, map_screen, ui_screen):
        pass
