import socket
import select
import random
from terra.event import *
from terra.team import Team
from terra.settings import SERVER_PORT
from terra.engine.gameobject import GameObject
from terra.network.messagecode import MessageCode
from ast import literal_eval
from terra.managers.managers import Managers
from terra.piece.orders import deserialize_order


# Manager for synchronizing and messaging the game state back and forth in a network game.
class NetworkManager(GameObject):
    def __init__(self, address, is_host=True):
        super().__init__()

        if not address:
            # Don't do any networking.
            self.team = Team.RED
            self.networked_game = False
        else:
            self.networked_game = True
            self.is_host = is_host
            self.address = address
            self.server_port = SERVER_PORT

            self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.read_list = [self.connection]
            self.write_list = []

            if self.is_host:
                # Set ourselves up as the server / host
                self.connection.bind(("localhost", SERVER_PORT))
                self.team = Team.RED
                self.clients = []
            else:
                # Set ourselves up as a client, connecting to the host
                self.client_port = random.randrange(7008, 7999)
                self.connection.bind(("localhost", self.client_port))
                self.team = Team.BLUE
                self.connect_to_host()

    # Initialize a connection to the host
    def connect_to_host(self):
        self.send_message(MessageCode.NEW_CONNECTION, self.team, "")

    # Query the map name from the host and return it
    def get_map_name_from_host(self):
        # TODO
        return "cycle_island.map"

    # Handle incoming messages from either the client or the host
    def handle_message(self, message, address):
        print("Received message '{}' from '{}'".format(str(message.decode()), str(address)))

        command = message.decode()[:9]
        team = Team(message.decode()[9:14])
        body = message.decode()[14:]

        if command == MessageCode.NEW_CONNECTION.value:
            print("Connection request from: " + str(address))
            self.clients.append(address)
        elif command == MessageCode.DROP_CONNECTION.value:
            print("Connection dropped for: " + str(address))
            self.clients.remove(address)
        elif command == MessageCode.SET_ORDERS.value:
            print("Setting orders from net msg: " + str(literal_eval(body)))
            orders = literal_eval(body)

            parsed_orders = {}
            for coord, order in orders.items():
                parsed_orders[coord] = deserialize_order(order)

            Managers.piece_manager.set_orders(team, parsed_orders)
            publish_game_event(E_SUBMIT_TURN, {
                'team': team
            })

    # Send the provided message on to the other player
    def send_message(self, code, team, message):
        full_message = (code.value + team.value + message).encode()

        if self.is_host:
            for client in self.clients:
                self.connection.sendto(full_message, client)
        else:
            self.connection.sendto(full_message, (self.address, self.server_port))

    # Check for any new network messages
    # Maintain a buffer of messages to send and send them in the step func, but add to the buffer in the while 1 loop
    def network_step(self):
        if self.networked_game:
            readable, writable, exceptional = (
                select.select(self.read_list, self.write_list, [], 0)
            )

            for f in readable:
                if f is self.connection:
                    message, address = f.recvfrom(2048)
                    self.handle_message(message, address)

    def step(self, event):
        if self.networked_game:
            if is_event_type(event, E_TURN_SUBMITTED):
                self.send_message(MessageCode.SET_ORDERS, event.team, str(event.orders))
            elif is_event_type(event, E_CANCEL_TURN_SUBMITTED):
                pass
            elif is_event_type(event, E_ALL_TURNS_SUBMITTED):
                pass

    def render(self, map_screen, ui_screen):
        pass