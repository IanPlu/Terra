

# Container for the various -manager objects.
# The initialize method must be called first when a battle is being set up.
class Managers:
    team_manager = None
    piece_manager = None
    effects_manager = None
    turn_manager = None
    player_manager = None
    battle_map = None
    map_name = ""

    @staticmethod
    def initialize_managers(bitmap, pieces, teams, map_name):
        from terra.managers.effectsmanager import EffectsManager
        from terra.managers.mapmanager import MapManager
        from terra.managers.piecemanager import PieceManager
        from terra.managers.playermanager import PlayerManager
        from terra.managers.teammanager import TeamManager
        from terra.managers.turnmanager import TurnManager

        Managers.effects_manager = EffectsManager()
        Managers.map_name = map_name
        Managers.team_manager = TeamManager(teams)
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

        # Strip '.map' from the map name
        savename = Managers.map_name[:-4]

        with open("resources/maps/{}.sav".format(savename), 'w') as savefile:
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

            savefile.write(lines)

    @staticmethod
    def step(event):
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
