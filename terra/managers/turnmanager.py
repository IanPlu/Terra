from terra.battlephase import BattlePhase
from terra.engine.gameobject import GameObject
from terra.event.event import publish_game_event, EventType
from terra.managers.session import Manager
from terra.map.metadatakey import MetadataKey
from terra.constants import TICK_RATE
from terra.settings import SETTINGS, Setting


# Manager for the current phase of the game and marshalling progression through phases.
class TurnManager(GameObject):
    def __init__(self, meta):
        super().__init__()
        self.turn = 1
        self.phase = BattlePhase.ORDERS
        self.timer = 0

        # How long each phase's animation should take (in seconds)
        self.phase_animation_length = 1/4
        self.framerate = 1

        # Initialize any data from metadata we care about
        for key, value in meta.items():
            if key == MetadataKey.TURN.value:
                self.turn = int(value)
            elif key == MetadataKey.PHASE.value:
                self.phase = BattlePhase[value]

        if self.phase == BattlePhase.START_TURN:
            self.progress_phase(None)

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.END_PHASE_START_TURN, self.progress_phase)
        event_bus.register_handler(EventType.END_PHASE_MOVE, self.progress_phase)
        event_bus.register_handler(EventType.END_PHASE_BUILD, self.progress_phase)
        event_bus.register_handler(EventType.END_PHASE_COMBAT, self.progress_phase)
        event_bus.register_handler(EventType.END_PHASE_RANGED, self.progress_phase)
        event_bus.register_handler(EventType.END_PHASE_SPECIAL, self.progress_phase)

        event_bus.register_handler(EventType.E_ALL_TURNS_SUBMITTED, self.progress_phase)

    # Validate that it's OK to progress the current phase.
    def validate_phase(self):
        if self.phase == BattlePhase.ORDERS:
            # Validate that all orders for all teams are correct before moving on
            for team in self.get_manager(Manager.TEAM).get_teams():
                if not self.get_manager(Manager.PIECE).validate_orders(team):
                    return False
            return True
        else:
            # Other phases have no validation at the moment
            return True

    # Move the phase forward if possible
    def progress_phase(self, event):
        if not self.validate_phase():
            return

        # Clean up units every phase
        publish_game_event(EventType.E_CLEANUP, {})

        # Publish an event for the end of the orders phase, if necessary
        if self.phase == BattlePhase.ORDERS:
            publish_game_event(EventType.END_PHASE_ORDERS, {})

        # Progress the phase
        new_phase = self.phase.value + 1
        if new_phase >= len(BattlePhase):
            new_phase = 0
        self.phase = BattlePhase(new_phase)

        # Log the start of a new round, if necessary
        if self.phase == BattlePhase.START_TURN:
            self.turn += 1

        # Publish events for the new phase
        publish_game_event(EventType.E_NEXT_PHASE, {
            'new_phase': self.phase
        })
        publish_game_event(self.phase_events[self.phase], {
            "turn_number": self.turn
        })

    def end_phase(self):
        publish_game_event(self.end_events[self.phase], {})
        self.timer = 0

    phase_events = {
        BattlePhase.START_TURN: EventType.START_PHASE_START_TURN,
        BattlePhase.ORDERS: EventType.START_PHASE_ORDERS,
        BattlePhase.EXECUTE_MOVE: EventType.START_PHASE_EXECUTE_MOVE,
        BattlePhase.EXECUTE_BUILD: EventType.START_PHASE_EXECUTE_BUILD,
        BattlePhase.EXECUTE_COMBAT: EventType.START_PHASE_EXECUTE_COMBAT,
        BattlePhase.EXECUTE_RANGED: EventType.START_PHASE_EXECUTE_RANGED,
        BattlePhase.EXECUTE_SPECIAL: EventType.START_PHASE_EXECUTE_SPECIAL,
    }

    end_events = {
        BattlePhase.START_TURN: EventType.END_PHASE_START_TURN,
        BattlePhase.ORDERS: EventType.END_PHASE_ORDERS,
        BattlePhase.EXECUTE_MOVE: EventType.END_PHASE_MOVE,
        BattlePhase.EXECUTE_BUILD: EventType.END_PHASE_BUILD,
        BattlePhase.EXECUTE_COMBAT: EventType.END_PHASE_COMBAT,
        BattlePhase.EXECUTE_RANGED: EventType.END_PHASE_RANGED,
        BattlePhase.EXECUTE_SPECIAL: EventType.END_PHASE_SPECIAL,
    }

    def serialize_metadata(self):
        return [
            (MetadataKey.TURN.value, self.turn),
            (MetadataKey.PHASE.value, self.phase.name),
        ]

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.phase != BattlePhase.ORDERS:
            self.timer += (self.framerate * SETTINGS.get(Setting.ANIMATION_SPEED)) / TICK_RATE
            # Progress the phase
            if self.timer >= self.phase_animation_length:
                self.end_phase()
