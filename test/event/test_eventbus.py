import unittest

from pygame.event import Event
from pygame import USEREVENT

from terra.event.event import EventType, EVENT_TYPE, FROM_NETWORK
from terra.event.eventbus import EventBus


class TestObject:
    def __init__(self):
        self.test_function_has_been_called = False
        self.test_value = 0
        self.accepts_events = True

    def test_function(self, event):
        self.test_function_has_been_called = True

    def test_function2(self, event):
        self.test_value += 1

    def is_accepting_events(self):
        return self.accepts_events


class EventBusTest(unittest.TestCase):
    def test_add_handler(self):
        bus = EventBus()

        def dummy_function(event): pass

        bus.register_handler(EventType.E_START_BATTLE, dummy_function)

        self.assertTrue(len(bus.__subscribers__[EventType.E_START_BATTLE]) > 0)

    def test_invoke_handler(self):
        bus = EventBus()
        test_object = TestObject()

        bus.register_handler(EventType.E_START_BATTLE, test_object.test_function)

        # Try to invoke the handler
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE
        })
        bus.invoke_handlers(test_event)

        self.assertTrue(test_object.test_function_has_been_called)

    def test_remove_handler(self):
        bus = EventBus()
        test_object = TestObject()

        bus.register_handler(EventType.E_START_BATTLE, test_object.test_function)

        self.assertTrue(len(bus.__subscribers__[EventType.E_START_BATTLE]) > 0)

        bus.unregister_handlers(test_object)

        self.assertTrue(len(bus.__subscribers__[EventType.E_START_BATTLE]) == 0)

        # Try (and fail) to invoke the handler
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE
        })
        bus.invoke_handlers(test_event)

        self.assertFalse(test_object.test_function_has_been_called)

    def test_invocation_state(self):
        bus = EventBus()
        test_object = TestObject()

        # The test value should start at 0
        self.assertTrue(test_object.test_value == 0)

        bus.register_handler(EventType.E_START_BATTLE, test_object.test_function2)

        # Modify the test value outside of the handler
        test_object.test_value = 2

        # Invoke the handler
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE
        })
        bus.invoke_handlers(test_event)

        # Assert that the callback method uses the current object and not a snapshot
        self.assertTrue(test_object.test_value == 3)

    def test_invoke_handler_accepting_input(self):
        bus = EventBus()
        test_object = TestObject()

        bus.register_handler(EventType.E_START_BATTLE, test_object.test_function2)

        # Try to invoke the handler with a local event
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE
        })
        bus.invoke_handlers(test_event)
        self.assertTrue(test_object.test_value == 1)

        # Try (and fail) to invoke the handler after disabling accepting events
        test_object.accepts_events = False
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE,
        })
        bus.invoke_handlers(test_event)
        self.assertTrue(test_object.test_value == 1)

    def test_local_only_handler(self):
        bus = EventBus()
        test_object = TestObject()

        bus.register_handler(EventType.E_START_BATTLE, test_object.test_function2, local_only=True)

        # Try to invoke the handler with a local event
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE
        })
        bus.invoke_handlers(test_event)
        self.assertTrue(test_object.test_value == 1)

        # Try (and fail) to invoke the handler with a network event
        test_event = Event(USEREVENT, {
            EVENT_TYPE: EventType.E_START_BATTLE,
            FROM_NETWORK: True
        })
        bus.invoke_handlers(test_event)
        self.assertTrue(test_object.test_value == 1)
