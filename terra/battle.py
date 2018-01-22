from terra.map.map import Map, load_map_from_file
from terra.ui.cursor import Cursor
from terra.constants import *
from terra.settings import *
from terra.piece.piecemanager import PieceManager
from terra.event import *
from terra.economy.teammanager import TeamManager
from terra.effects.effectsmanager import EffectsManager
from terra.effects.effecttype import EffectType
from terra.piece.building.buildingtype import BuildingType


# A battle containing a map, players, their resources + input methods, etc.
# Handles the turn / phase loop.
class Battle:
    def __init__(self, mapname="map4.txt"):
        super().__init__()

        bitmap, roster, buildings, teams = load_map_from_file(mapname)

        self.map = Map(bitmap)
        self.effects_manager = EffectsManager()
        self.team_manager = TeamManager(self, self.effects_manager, teams)
        self.piece_manager = PieceManager(self, self.map, self.team_manager, roster, buildings)

        self.cursors = {}
        for team in Team:
            self.cursors[team] = Cursor(self.map, team)

        self.active_team = Team.RED

        self.phase = BattlePhase.EXECUTE_SPECIAL
        self.progress_phase()

    # Validate that it's OK to progress the current phase.
    # Check movement orders, primarily
    def validate_phase(self):
        if self.phase == BattlePhase.ORDERS:
            # Validate that all orders for all teams are correct before moving on
            for team in Team:
                if not self.piece_manager.validate_orders(team):
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
        self.map.step(event)
        self.piece_manager.step(event)
        self.effects_manager.step(event)
        self.team_manager.step(event)

        if self.phase == BattlePhase.ORDERS:
            self.cursors[self.active_team].step(event)

        if is_event_type(event, START_PHASE_START_TURN, START_PHASE_EXECUTE_BUILD,
                         START_PHASE_EXECUTE_MOVE, START_PHASE_EXECUTE_COMBAT,
                         START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL):
            self.progress_phase()
        elif is_event_type(event, E_ALL_TURNS_SUBMITTED):
            self.progress_phase()
        elif is_event_type(event, E_BASE_DESTROYED):
            self.check_for_victory(event)
        elif is_event_type(event, E_PIECE_DEAD):
            self.effects_manager.create_effect(event.gx, event.gy, EffectType.PIECE_DESTROYED)
        elif is_event_type(event, E_INVALID_MOVE_ORDERS):
            for coordinate in event.invalid_coordinates:
                self.effects_manager.create_effect(coordinate[0], coordinate[1], EffectType.ALERT)
        elif is_event_type(event, E_INVALID_BUILD_ORDERS):
            base = self.piece_manager.get_all_pieces_for_team(event.team, BuildingType.BASE)[0]
            self.effects_manager.create_effect(base.gx, base.gy, EffectType.NO_MONEY)
        elif event.type == KEYDOWN:
            if event.key in KB_DEBUG2:
                if self.active_team == Team.RED:
                    self.active_team = Team.BLUE
                elif self.active_team == Team.BLUE:
                    self.active_team = Team.RED

    # Generate a screen with the entire map, subsurfaced to the camera area
    def render(self, ui_screen):
        # Generate a screen of the size of the map
        map_screen = pygame.Surface((self.map.width * GRID_WIDTH, self.map.height * GRID_HEIGHT), pygame.SRCALPHA, 32)

        self.map.render(map_screen, ui_screen)
        self.piece_manager.render(map_screen, ui_screen)
        self.team_manager.render(map_screen, ui_screen)
        self.effects_manager.render(map_screen, ui_screen)

        if self.phase == BattlePhase.ORDERS:
            self.cursors[self.active_team].render(map_screen, ui_screen)

        # Trim the screen to just the camera area
        return map_screen.subsurface((self.cursors[self.active_team].camera_x, self.cursors[self.active_team].camera_y,
                                      min(RESOLUTION_WIDTH, map_screen.get_size()[0]),
                                      min(RESOLUTION_HEIGHT, map_screen.get_size()[1])))
