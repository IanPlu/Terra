from enum import Enum

from terra.map.maputils import load_map_from_file, generate_map, parse_map_from_string, map_exists
from terra.mode import Mode
from terra.resources.assetloading import AssetType, get_asset


class Manager(Enum):
    COMBAT_LOGGER = "combat_logger"
    EFFECTS = "effects"
    MAP = "map"
    TEAM = "team"
    PIECE = "piece"
    TURN = "turn"
    PLAYER = "player"
    NETWORK = "network"
    SOUND = "sound"
    STAT = "stat"


# A single game session (a battle). An instance will contain multiple manager objects.
class Session:
    def __init__(self, is_network_game=False):
        super().__init__()

        self.managers = {}

        self.map_name = None
        self.current_mode = Mode.MAIN_MENU
        self.is_network_game = is_network_game

    def get(self, manager_type):
        return self.managers[manager_type]

    # Set up a local game, either a new game with a .map file, or loading a saved game from a .sav file.
    @staticmethod
    def set_up_local_game(map_name, map_type=AssetType.MAP):
        from terra.network.networkmanager import NetworkManager

        bitmap, pieces, teams, upgrades, meta = load_map_from_file(map_name, map_type)

        global SESSION
        SESSION.reset()
        SESSION.managers[Manager.NETWORK] = NetworkManager(None, teams)
        SESSION.__set_up__(map_name, bitmap, pieces, teams, upgrades, meta)

        return bitmap, pieces, teams, upgrades, meta

    # Set up a network game, where we're the host.
    @staticmethod
    def set_up_network_game_as_host(map_name, map_type=AssetType.MAP, address="localhost"):
        from terra.network.networkmanager import NetworkManager

        bitmap, pieces, teams, upgrades, meta = load_map_from_file(map_name, map_type)

        global SESSION
        SESSION.reset()
        SESSION.is_network_game = True
        SESSION.managers[Manager.NETWORK] = NetworkManager(address, teams, is_host=True)
        SESSION.__set_up__(map_name, bitmap, pieces, teams, upgrades, meta)

        return bitmap, pieces, teams, upgrades, meta

    # Set up a network game, where we're just a client. Ping the host to get the map data.
    @staticmethod
    def set_up_network_game_as_client(address):
        from terra.network.networkmanager import NetworkManager

        global SESSION
        SESSION.reset()
        SESSION.is_network_game = True
        SESSION.managers[Manager.NETWORK] = NetworkManager(address, None, is_host=False)
        bitmap, pieces, teams, upgrades, meta = parse_map_from_string(SESSION.get(Manager.NETWORK).map_data)
        SESSION.__set_up__("NetworkGame", bitmap, pieces, teams, upgrades, meta)

        return bitmap, pieces, teams, upgrades, meta

    # Set up a level editor sessions, creating a new map if needed.
    @staticmethod
    def set_up_level_editor(map_name):
        from terra.network.networkmanager import NetworkManager

        if map_exists(map_name):
            bitmap, pieces, teams, upgrades, meta = load_map_from_file(map_name, AssetType.MAP)
        else:
            bitmap, pieces, teams, upgrades, meta = generate_map()

        global SESSION
        SESSION.reset()
        SESSION.managers[Manager.NETWORK] = NetworkManager(None, teams)
        SESSION.__set_up__(map_name, bitmap, pieces, teams, upgrades, meta)

        return bitmap, pieces, teams, upgrades, meta

    # Remove and delete our managers, starting over.
    def reset(self):
        for key, manager in self.managers.items():
            manager.destroy()

        del self.managers
        self.managers = {}

    # Set up non-network managers, given a map, pieces, teams, etc.
    def __set_up__(self, map_name, bitmap, pieces, teams, upgrades, meta):
        # Dodging circular dependencies. It's usually OK for managers to rely on one another.
        # NOTE: Creation order for managers matters as a result!
        from terra.managers.combatlogger import CombatLogger
        from terra.effects.effectsmanager import EffectsManager
        from terra.map.mapmanager import MapManager
        from terra.piece.piecemanager import PieceManager
        from terra.team.playermanager import PlayerManager
        from terra.sound.soundmanager import SoundManager
        from terra.managers.statmanager import StatManager
        from terra.team.teammanager import TeamManager
        from terra.turn.turnmanager import TurnManager

        self.map_name = map_name
        self.managers[Manager.COMBAT_LOGGER] = CombatLogger(map_name)
        self.managers[Manager.EFFECTS] = EffectsManager()
        self.managers[Manager.TEAM] = TeamManager(teams, upgrades)
        self.managers[Manager.MAP] = MapManager(bitmap)
        self.managers[Manager.PIECE] = PieceManager(pieces)
        self.managers[Manager.TURN] = TurnManager(meta)
        self.managers[Manager.PLAYER] = PlayerManager()
        self.managers[Manager.SOUND] = SoundManager()
        self.managers[Manager.STAT] = StatManager(teams)

    def step(self, event):
        for key, manager in self.managers.items():
            manager.step(event)

    def render(self, game_screen, ui_screen):
        for key, manager in self.managers.items():
            manager.render(game_screen, ui_screen)

    # Set the current game mode
    def set_mode(self, new_mode):
        self.current_mode = new_mode

    # Ask each manager to serialize any metadata it needs to store
    def serialize_metadata(self):
        metadata = []

        metadata.extend(self.get(Manager.TURN).serialize_metadata())

        return metadata

    # Save the current game state to a string
    def save_game_to_string(self):
        # Ask each manager to serialize itself
        bitmap = self.get(Manager.MAP).convert_bitmap_from_grid()
        pieces = self.get(Manager.PIECE).serialize_pieces()
        teams = self.get(Manager.TEAM).serialize_teams()
        upgrades = self.get(Manager.TEAM).serialize_upgrades()
        meta = self.serialize_metadata()

        # Strip '.map' from the map name
        save_name = self.map_name[:-4]
        save_path = get_asset(AssetType.SAVE, save_name + ".sav")

        # Serialize to a string
        lines = ""
        # Append map
        for row in bitmap:
            line = ""
            for column in row:
                line += "{} ".format(column)
            line += "\n"
            lines += line

        # Append pieces
        lines += "# Pieces\n"
        for piece in pieces:
            lines += piece + "\n"

        # Append teams
        lines += "# Teams\n"
        for team in teams:
            lines += team + "\n"

        # Append upgrades
        lines += "# Upgrades\n"
        for upgrade in upgrades:
            lines += upgrade + "\n"

        # Append any meta information
        lines += "# Meta\n"
        for metadata in meta:
            lines += "{} {} \n".format(metadata[0], metadata[1])

        return lines, save_path

    # Save the current state to a save file
    def save_game_to_file(self):
        lines, save_path = self.save_game_to_string()

        with open(save_path, 'w') as save_file:
            save_file.write(lines)

    # Save the current state to a map file
    def save_map_to_file(self):
        lines, _ = self.save_game_to_string()

        with open(get_asset(AssetType.MAP, self.map_name), 'w') as map_file:
            map_file.write(lines)


SESSION = Session()
