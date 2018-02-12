from pygame.constants import KEYDOWN

from terra.battlephase import BattlePhase
from terra.engine.gameobject import GameObject
from terra.event import is_event_type, publish_game_event, E_NEXT_PHASE, E_CLEANUP, START_PHASE_START_TURN, \
    START_PHASE_ORDERS, START_PHASE_EXECUTE_BUILD, START_PHASE_EXECUTE_MOVE, START_PHASE_EXECUTE_COMBAT, \
    START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL, E_ALL_TURNS_SUBMITTED
from terra.managers.managers import Managers
from terra.team import Team
from terra.keybindings import KB_DEBUG1


# Manager for the current phase of the game and marshalling progression through phases.
class TurnManager(GameObject):
    def __init__(self):
        super().__init__()

        self.phase = BattlePhase.ORDERS

    # Validate that it's OK to progress the current phase.
    # Check movement orders, primarily
    def validate_phase(self):
        if self.phase == BattlePhase.ORDERS:
            # Validate that all orders for all teams are correct before moving on
            for team in Team:
                if not Managers.piece_manager.validate_orders(team):
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

    def step(self, event):
        super().step(event)

        if is_event_type(event, START_PHASE_START_TURN, START_PHASE_EXECUTE_BUILD,
                         START_PHASE_EXECUTE_MOVE, START_PHASE_EXECUTE_COMBAT,
                         START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL):
            self.progress_phase()
        elif is_event_type(event, E_ALL_TURNS_SUBMITTED):
            self.progress_phase()
        elif event.type == KEYDOWN:
            if event.key in KB_DEBUG1:
                self.progress_phase()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
