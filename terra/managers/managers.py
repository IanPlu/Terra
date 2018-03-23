from terra.managers.errorlogger import ErrorLogger
from terra.mode import Mode
from terra.resources.assetloading import AssetType, get_asset


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

    current_mode = Mode.MAIN_MENU

    @staticmethod
    def initialize_managers(map_name, address, is_host):
        from terra.managers.effectsmanager import EffectsManager
        from terra.managers.mapmanager import MapManager, load_map_from_file, generate_map, parse_map_from_string
        from terra.managers.piecemanager import PieceManager
        from terra.managers.playermanager import PlayerManager
        from terra.managers.teammanager import TeamManager
        from terra.managers.turnmanager import TurnManager
        from terra.managers.combatlogger import CombatLogger
        from terra.managers.networkmanager import NetworkManager
        from terra.managers.soundmanager import SoundManager

        Managers.network_manager = NetworkManager(address, is_host)

        if map_name:
            # Load the map from a file for a local game (or network game where we're the host)
            bitmap, pieces, teams, upgrades, meta = load_map_from_file(map_name)
        elif not map_name and Managers.network_manager.networked_game:
            # Client games won't have a map name until they connect, so fetch it now
            map_data = Managers.network_manager.map_data

            # If we still have no map data, just abort and return to the title screen
            if not map_data:
                Managers.tear_down_managers()
                return
            else:
                # Load the map from the string representation given to us by the host
                map_name = "NetworkGame"
                bitmap, pieces, teams, upgrades, meta = parse_map_from_string(map_data)
        else:
            # No map name for a local game, so assume something has gone wrong and abort
            Managers.tear_down_managers()
            return

        Managers.combat_logger = CombatLogger(map_name)
        Managers.effects_manager = EffectsManager()
        Managers.map_name = map_name
        Managers.team_manager = TeamManager(teams, upgrades)
        Managers.battle_map = MapManager(bitmap)
        Managers.piece_manager = PieceManager(pieces)
        Managers.turn_manager = TurnManager(meta)
        Managers.player_manager = PlayerManager()
        Managers.sound_manager = SoundManager()

    @staticmethod
    def tear_down_managers():
        del Managers.network_manager
        del Managers.combat_logger
        del Managers.effects_manager
        del Managers.map_name
        del Managers.team_manager
        del Managers.battle_map
        del Managers.piece_manager
        del Managers.turn_manager
        del Managers.player_manager
        del Managers.sound_manager

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

        # TODO: Expand to allow all managers to register k/v pairs to this
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
            lines += "{} {}\n".format(metadata[0], metadata[1])

        return lines, save_path

    @staticmethod
    def serialize_metadata():
        return Managers.turn_manager.serialize_metadata()

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
