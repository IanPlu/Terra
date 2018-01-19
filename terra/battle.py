from terra.map.map import Map
from terra.ui.cursor import Cursor
from terra.constants import *
from terra.settings import *
from terra.util.drawingutil import draw_text
from terra.strings import phase_strings
from terra.piece.piecemanager import PieceManager
from terra.event import *
from terra.resources.assets import spr_cursor, spr_phase_indicator
from terra.teammanager import TeamManager


phase_text = {}
for _, phase in BattlePhase.__members__.items():
    phase_text[phase] = draw_text(phase_strings[LANGUAGE][phase], (248, 240, 211))


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class Battle:
    def __init__(self, mapname="map3.txt"):
        super().__init__()

        bitmap, roster, buildings, teams = self.load_map_from_file(mapname)

        self.map = Map(bitmap)
        self.team_manager = TeamManager(self, teams)
        self.piece_manager = PieceManager(self, self.map, self.team_manager, roster, buildings)
        self.cursor = Cursor(self.map)

        self.phase = BattlePhase.ORDERS

        # TODO IP
        self.toast = None # ToastNotification(self, "")

    # Load a map from the provided filename
    # Generate a bitmap for the Map to use, and generate a unit list for the PieceManager to use.
    def load_map_from_file(self, mapname):
        reading_units = False
        reading_buildings = False
        reading_teams = False

        with open("resources/maps/" + mapname) as mapfile:
            bitmap = []
            roster = []
            buildings = []
            teams = []
            for line in mapfile:
                if line.rstrip() == "# Units":
                    reading_units = True
                elif line.rstrip() == "# Buildings":
                    reading_buildings = True
                elif line.rstrip() == "# Teams":
                    reading_teams = True
                elif reading_teams:
                    if line.rstrip():
                        # Add each line to teams
                        teams.append(line.rstrip())
                elif reading_buildings:
                    if line.rstrip():
                        # Add each line to the buildings
                        buildings.append(line.rstrip())
                elif reading_units:
                    if line.rstrip():
                        # Add each line to the roster
                        roster.append(line.rstrip())
                else:
                    # Grab all non-newline chars, convert them to ints, and add them to the line list
                    bitmap.append(list(map(int, line.rstrip().split(' '))))

            # Filter teams to just the Team enum objects
            teams = list(set([Team[team] for team in teams if Team[team]]))

        return bitmap, roster, buildings, teams

    # Validate that it's OK to progress the current phase.
    # Check movement orders, primarily
    def validate_phase(self):
        if self.phase == BattlePhase.ORDERS:
            # Validate that all orders for all teams are correct before moving on
            for team in Team:
                if not self.piece_manager.validate_movement_orders(team):
                    publish_game_event(E_INVALID_ORDER, {
                        'team': team
                    })
                    return False
        else:
            # Other phases have no validation at the moment
            return True

        return True

    # Move the phase forward if possible
    def progress_phase(self):
        if not self.validate_phase():
            return

        new_phase = self.phase.value + 1
        if new_phase >= len(BattlePhase):
            new_phase = 0

        self.phase = BattlePhase(new_phase)

        publish_game_event(E_NEXT_PHASE, {
            'new_phase': self.phase
        })

        # Clean up units every phase
        publish_game_event(E_CLEANUP, {})

        # Execute the handler for the phase
        self.phase_handlers[self.phase](self)

    def resolve_phase_start_turn(self):
        publish_game_event(START_PHASE_START_TURN, {})

    def resolve_phase_orders(self):
        publish_game_event(START_PHASE_ORDERS, {})
        pass

    def resolve_phase_execute_build(self):
        publish_game_event(START_PHASE_EXECUTE_BUILD, {})

    def resolve_phase_execute_move(self):
        publish_game_event(START_PHASE_EXECUTE_MOVE, {})

    def resolve_phase_execute_combat(self):
        publish_game_event(START_PHASE_EXECUTE_COMBAT, {})

    def resolve_phase_execute_ranged(self):
        publish_game_event(START_PHASE_EXECUTE_RANGED, {})

    def resolve_phase_execute_special(self):
        publish_game_event(START_PHASE_EXECUTE_SPECIAL, {})

    phase_handlers = {
        BattlePhase.START_TURN: resolve_phase_start_turn,
        BattlePhase.ORDERS: resolve_phase_orders,
        BattlePhase.EXECUTE_BUILD: resolve_phase_execute_build,
        BattlePhase.EXECUTE_MOVE: resolve_phase_execute_move,
        BattlePhase.EXECUTE_COMBAT: resolve_phase_execute_combat,
        BattlePhase.EXECUTE_RANGED: resolve_phase_execute_ranged,
        BattlePhase.EXECUTE_SPECIAL: resolve_phase_execute_special
    }

    def check_for_victory(self, event):
        print("A base has been destroyed. The game is over!")

    def step(self, event):
        if self.toast:
            self.toast.step(event)

        if event.type == KEYDOWN and event.key in KB_DEBUG1:
            self.progress_phase()

        self.map.step(event)
        self.piece_manager.step(event)

        if self.phase == BattlePhase.ORDERS:
            self.cursor.step(event)

        if is_event_type(event, START_PHASE_START_TURN, START_PHASE_EXECUTE_BUILD,
                         START_PHASE_EXECUTE_MOVE, START_PHASE_EXECUTE_COMBAT,
                         START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL):
            self.progress_phase()
        elif is_event_type(event, E_BASE_DESTROYED):
            self.check_for_victory(event)

    # Generate a screen with the entire map, subsurfaced to the camera area
    def render(self, ui_screen):
        # Generate a screen of the size of the map
        map_screen = pygame.Surface((self.map.width * GRID_WIDTH, self.map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)

        self.map.render(map_screen, ui_screen)
        self.piece_manager.render(map_screen, ui_screen)

        if self.phase == BattlePhase.ORDERS:
            self.cursor.render(map_screen, ui_screen)

        # Render phase indicator bar
        ui_screen.fill(CLEAR_COLOR, (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        for x in range(len(spr_phase_indicator)):
            ui_screen.blit(spr_phase_indicator[x], (x * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[Team.RED], (self.phase.value * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render phase indicator text
        ui_screen.blit(phase_text[self.phase],
                    (4 + GRID_WIDTH * len(spr_phase_indicator), RESOLUTION_HEIGHT - GRID_HEIGHT + 6))

        # Render any toast notifications we have
        if self.toast:
            self.toast.render(map_screen, ui_screen)

        # Trim the screen to just the camera area
        return map_screen.subsurface((self.cursor.camera_x, self.cursor.camera_y, RESOLUTION_WIDTH, RESOLUTION_HEIGHT))
