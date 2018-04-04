from terra.managers.errorlogger import ErrorLogger
from terra.mode import Mode
from terra.resources.assetloading import AssetType, get_asset
from terra.team import Team


# Container for the various -manager objects.
# The initialize method must be called first when a battle is being set up.
class Managers:
    error_logger = ErrorLogger()
    combat_logger = None
    effects_manager = None
    map_name = None
    team_manager = None
    battle_map = None
    piece_manager = None
    turn_manager = None
    player_manager = None
    network_manager = None
    sound_manager = None
    stat_manager = None

    current_mode = Mode.MAIN_MENU

    @staticmethod
    def load_map_setup_network(map_name, address, is_host, map_type=AssetType.MAP):
        from terra.managers.networkmanager import NetworkManager
        from terra.managers.mapmanager import load_map_from_file, parse_map_from_string, generate_map

        if map_name:
            # Load the map from a file for a local game (or network game where we're the host)
            bitmap, pieces, teams, upgrades, meta = load_map_from_file(map_name, map_type)
            open_teams = [Team[team.split(' ')[0]] for team in teams]

            Managers.network_manager = NetworkManager(address, open_teams, is_host)
        elif not map_name and not is_host:
            # Client games won't have a map name until they connect, so fetch it now
            Managers.network_manager = NetworkManager(address, None, is_host)
            map_data = Managers.network_manager.map_data

            # If we still have no map data, generate a random one, assuming we'll throw it out
            # TODO: Investigate a cleaner approach to this
            if not map_data:
                bitmap, pieces, teams, upgrades, meta = generate_map()
            else:
                # Load the map from the string representation given to us by the host
                map_name = "NetworkGame"
                bitmap, pieces, teams, upgrades, meta = parse_map_from_string(map_data)
        else:
            # No map name for a local game, so assume something has gone wrong and abort
            Managers.tear_down_managers()
            return

        return map_name, bitmap, pieces, teams, upgrades, meta

    @staticmethod
    def initialize_managers(map_name, bitmap, pieces, teams, upgrades, meta):
        from terra.managers.effectsmanager import EffectsManager
        from terra.managers.mapmanager import MapManager
        from terra.managers.piecemanager import PieceManager
        from terra.managers.playermanager import PlayerManager
        from terra.managers.teammanager import TeamManager
        from terra.managers.turnmanager import TurnManager
        from terra.managers.combatlogger import CombatLogger
        from terra.managers.soundmanager import SoundManager
        from terra.managers.statmanager import StatManager

        Managers.combat_logger = CombatLogger(map_name)
        Managers.effects_manager = EffectsManager()
        Managers.map_name = map_name
        Managers.team_manager = TeamManager(teams, upgrades)
        Managers.battle_map = MapManager(bitmap)
        Managers.piece_manager = PieceManager(pieces)
        Managers.turn_manager = TurnManager(meta)
        Managers.player_manager = PlayerManager()
        Managers.sound_manager = SoundManager()
        Managers.stat_manager = StatManager(teams)

    @staticmethod
    def tear_down_managers():
        def safe_destroy(manager):
            if manager:
                manager.destroy()

        safe_destroy(Managers.network_manager)
        safe_destroy(Managers.effects_manager)
        safe_destroy(Managers.team_manager)
        safe_destroy(Managers.battle_map)
        safe_destroy(Managers.piece_manager)
        safe_destroy(Managers.turn_manager)
        safe_destroy(Managers.player_manager)
        safe_destroy(Managers.sound_manager)
        safe_destroy(Managers.stat_manager)

        del Managers.map_name
        del Managers.combat_logger

        Managers.network_manager = None
        Managers.combat_logger = None
        Managers.effects_manager = None
        Managers.map_name = None
        Managers.team_manager = None
        Managers.battle_map = None
        Managers.piece_manager = None
        Managers.turn_manager = None
        Managers.player_manager = None
        Managers.sound_manager = None
        Managers.stat_manager = None

        Managers.set_mode(Mode.MAIN_MENU)

    @staticmethod
    def save_game_to_string():
        # Ask the map to serialize itself
        bitmap = Managers.battle_map.convert_bitmap_from_grid()

        # Ask the piece manager to serialize itself
        pieces = Managers.piece_manager.serialize_pieces()

        # Ask the team manager to serialize itself
        teams = Managers.team_manager.serialize_teams()

        # Ask the team manager to serialize its upgrades
        upgrades = Managers.team_manager.serialize_upgrades()

        # Ask the turn manager to serialize the current turn
        meta = Managers.serialize_metadata()

        # Strip '.map' from the map name
        save_name = Managers.map_name[:-4]
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

    @staticmethod
    def serialize_metadata():
        metadata = []

        metadata.extend(Managers.turn_manager.serialize_metadata())

        return metadata

    @staticmethod
    # Save the current state to a save file
    def save_game_to_file():
        lines, save_path = Managers.save_game_to_string()

        with open(save_path, 'w') as save_file:
            save_file.write(lines)

    @staticmethod
    # Save the current state to a map file
    def save_map_to_file():
        lines, _ = Managers.save_game_to_string()

        with open(get_asset(AssetType.MAP, Managers.map_name), 'w') as map_file:
            map_file.write(lines)

    @staticmethod
    def set_mode(new_mode):
        Managers.current_mode = new_mode

    @staticmethod
    def step(event):
        Managers.network_manager.step(event)
        Managers.battle_map.step(event)
        Managers.piece_manager.step(event)
        Managers.effects_manager.step(event)
        Managers.team_manager.step(event)
        Managers.turn_manager.step(event)
        Managers.player_manager.step(event)
        Managers.sound_manager.step(event)
        Managers.stat_manager.step(event)

    @staticmethod
    def render(map_screen, ui_screen):
        Managers.battle_map.render(map_screen, ui_screen)
        Managers.piece_manager.render(map_screen, ui_screen)
        Managers.effects_manager.render(map_screen, ui_screen)
        Managers.team_manager.render(map_screen, ui_screen)
        Managers.turn_manager.render(map_screen, ui_screen)
        Managers.player_manager.render(map_screen, ui_screen)
        Managers.network_manager.render(map_screen, ui_screen)
        Managers.sound_manager.render(map_screen, ui_screen)
        Managers.stat_manager.render(map_screen, ui_screen)
