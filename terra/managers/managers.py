from terra.constants import MAP_PATH


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

    @staticmethod
    def initialize_managers(map_name, address, is_host):
        from terra.managers.effectsmanager import EffectsManager
        from terra.managers.mapmanager import MapManager, load_map_from_file
        from terra.managers.piecemanager import PieceManager
        from terra.managers.playermanager import PlayerManager
        from terra.managers.teammanager import TeamManager
        from terra.managers.turnmanager import TurnManager
        from terra.managers.combatlogger import CombatLogger
        from terra.managers.networkmanager import NetworkManager

        Managers.network_manager = NetworkManager(address, is_host)

        # Client games won't have a map name until they connect, so fetch it now
        if not map_name:
            map_name = Managers.network_manager.get_map_name_from_host()

        bitmap, pieces, teams, upgrades = load_map_from_file(map_name)

        Managers.combat_logger = CombatLogger(map_name)
        Managers.effects_manager = EffectsManager()
        Managers.map_name = map_name
        Managers.team_manager = TeamManager(teams, upgrades)
        Managers.battle_map = MapManager(bitmap)
        Managers.piece_manager = PieceManager(pieces)
        Managers.turn_manager = TurnManager()
        Managers.player_manager = PlayerManager()

    @staticmethod
    def save_game():
        # Ask the map to serialize itself
        bitmap = Managers.battle_map.convert_bitmap_from_grid()

        # Ask the piece manager to serialize itself
        pieces = Managers.piece_manager.serialize_pieces()

        # Ask the team manager to serialize itself
        teams = Managers.team_manager.serialize_teams()

        # Ask the team manager to serialize its upgrades
        upgrades = Managers.team_manager.serialize_upgrades()

        # Strip '.map' from the map name
        savename = Managers.map_name[:-4]

        with open("{}{}.sav".format(MAP_PATH, savename), 'w') as savefile:
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

            savefile.write(lines)

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
