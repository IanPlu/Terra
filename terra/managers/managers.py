from terra.resources.assets import AssetType, get_asset
from terra.mode import Mode


# Container for the various -manager objects.
# The initialize method must be called first when a battle is being set up.
class Managers:
    combat_logger = None
    effects_manager = None
    map_name = None
    team_manager = None
    battle_map = None
    piece_manager = None
    turn_manager = None
    player_manager = None
    network_manager = None

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

        Managers.network_manager = NetworkManager(address, is_host)

        if map_name:
            # Load the map from a file for a local game (or network game where we're the host)
            bitmap, pieces, teams, upgrades = load_map_from_file(map_name)
        elif not map_name and Managers.network_manager.networked_game:
            # Client games won't have a map name until they connect, so fetch it now
            map_data = Managers.network_manager.map_data
            map_name = "NetworkGame"
            # Load the map from the string representation given to us by the host
            bitmap, pieces, teams, upgrades = parse_map_from_string(map_data)
        else:
            # No map name for a local game, so assume we're generating a new map
            map_name = None
            bitmap, pieces, teams, upgrades = generate_map()

        Managers.combat_logger = CombatLogger(map_name)
        Managers.effects_manager = EffectsManager()
        Managers.map_name = map_name
        Managers.team_manager = TeamManager(teams, upgrades)
        Managers.battle_map = MapManager(bitmap)
        Managers.piece_manager = PieceManager(pieces)
        Managers.turn_manager = TurnManager()
        Managers.player_manager = PlayerManager()

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

        # Strip '.map' from the map name
        save_name = Managers.map_name[:-4]
        save_path = get_asset(AssetType.MAP, save_name + ".sav")

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

        return lines, save_path

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

    @staticmethod
    def render(map_screen, ui_screen):
        Managers.battle_map.render(map_screen, ui_screen)
        Managers.piece_manager.render(map_screen, ui_screen)
        Managers.effects_manager.render(map_screen, ui_screen)
        Managers.team_manager.render(map_screen, ui_screen)
        Managers.turn_manager.render(map_screen, ui_screen)
        Managers.player_manager.render(map_screen, ui_screen)
        Managers.network_manager.render(map_screen, ui_screen)
