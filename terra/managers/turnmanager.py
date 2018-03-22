
from terra.battlephase import BattlePhase
from terra.engine.gameobject import GameObject
from terra.event import is_event_type, publish_game_event, E_NEXT_PHASE, E_CLEANUP, START_PHASE_START_TURN, \
    START_PHASE_ORDERS, START_PHASE_EXECUTE_BUILD, START_PHASE_EXECUTE_MOVE, START_PHASE_EXECUTE_COMBAT, \
    START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL, E_ALL_TURNS_SUBMITTED, END_PHASE_START_TURN, \
    END_PHASE_ORDERS, END_PHASE_MOVE, END_PHASE_BUILD, END_PHASE_COMBAT, END_PHASE_RANGED, END_PHASE_SPECIAL
from terra.managers.managers import Managers
from terra.team import Team


# Manager for the current phase of the game and marshalling progression through phases.
class TurnManager(GameObject):
    def __init__(self):
        super().__init__()

        self.phase = BattlePhase.ORDERS
        self.round = 1
        Managers.combat_logger.log_new_round(self.round)

    # Validate that it's OK to progress the current phase.
    # Check movement orders, primarily
    def validate_phase(self):
        if self.phase == BattlePhase.ORDERS:
            # Validate that all orders for all teams are correct before moving on
            for team in Team:
                if not Managers.piece_manager.validate_orders(team):
                    return False

            Managers.piece_manager.log_orders()
            return True
        else:
            # Other phases have no validation at the moment
            return True

    # Move the phase forward if possible
    def progress_phase(self):
        if not self.validate_phase():
            return

        # Clean up units every phase
        publish_game_event(E_CLEANUP, {})

        # Publish an event for the end of the old phase
        publish_game_event(self.end_events[self.phase], {})

        new_phase = self.phase.value + 1
        if new_phase >= len(BattlePhase):
            new_phase = 0

        self.phase = BattlePhase(new_phase)

        if self.phase == BattlePhase.START_TURN:
            self.round += 1
            Managers.combat_logger.log_new_round(self.round)

        Managers.combat_logger.log_new_phase(self.phase)

        publish_game_event(E_NEXT_PHASE, {
            'new_phase': self.phase
        })

        # Publish an event for the new phase
        publish_game_event(self.phase_events[self.phase], {
            "turn_number": self.round
        })

    phase_events = {
        BattlePhase.START_TURN: START_PHASE_START_TURN,
        BattlePhase.ORDERS: START_PHASE_ORDERS,
        BattlePhase.EXECUTE_MOVE: START_PHASE_EXECUTE_MOVE,
        BattlePhase.EXECUTE_BUILD: START_PHASE_EXECUTE_BUILD,
        BattlePhase.EXECUTE_COMBAT: START_PHASE_EXECUTE_COMBAT,
        BattlePhase.EXECUTE_RANGED: START_PHASE_EXECUTE_RANGED,
        BattlePhase.EXECUTE_SPECIAL: START_PHASE_EXECUTE_SPECIAL,
    }

    end_events = {
        BattlePhase.START_TURN: END_PHASE_START_TURN,
        BattlePhase.ORDERS: END_PHASE_ORDERS,
        BattlePhase.EXECUTE_MOVE: END_PHASE_MOVE,
        BattlePhase.EXECUTE_BUILD: END_PHASE_BUILD,
        BattlePhase.EXECUTE_COMBAT: END_PHASE_COMBAT,
        BattlePhase.EXECUTE_RANGED: END_PHASE_RANGED,
        BattlePhase.EXECUTE_SPECIAL: END_PHASE_SPECIAL,
    }

    def step(self, event):
        super().step(event)

        if is_event_type(event, START_PHASE_START_TURN, START_PHASE_EXECUTE_MOVE,
                         START_PHASE_EXECUTE_BUILD, START_PHASE_EXECUTE_COMBAT,
                         START_PHASE_EXECUTE_RANGED, START_PHASE_EXECUTE_SPECIAL):
            self.progress_phase()
        elif is_event_type(event, E_ALL_TURNS_SUBMITTED):
            self.progress_phase()

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
