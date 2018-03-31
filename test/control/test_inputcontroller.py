import unittest

from pygame import KEYDOWN, MOUSEBUTTONDOWN, MOUSEMOTION, K_RETURN
from pygame.event import Event

from terra.control.inputcontroller import InputController, InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject


class TestObject(GameObject):
    def __init__(self):
        super().__init__()
        self.test_function_has_been_called = False
        self.test_value = 0
        self.accepting_input = True

    def is_accepting_input(self):
        return self.accepting_input

    def test_function(self):
        self.test_function_has_been_called = True

    def test_function2(self):
        self.test_value += 1


class InputControllerTest(unittest.TestCase):
    def test_add_handler(self):
        controller = InputController()

        def dummy_function(): pass

        controller.register_handler(InputAction.PRESS, Key.CONFIRM, dummy_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) > 0)

    def test_invoke_handler_keydown(self):
        controller = InputController()
        test_object = TestObject()

        controller.register_handler(InputAction.PRESS, Key.CONFIRM, test_object.test_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) > 0)

        # Try to invoke the handler
        test_event = Event(KEYDOWN, {
            'key': K_RETURN
        })

        controller.invoke_handlers(test_event)
        self.assertTrue(test_object.test_function_has_been_called)

    def test_invoke_handler_mousedown(self):
        controller = InputController()
        test_object = TestObject()

        controller.register_handler(InputAction.PRESS, Key.CONFIRM, test_object.test_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) > 0)

        # Try to invoke the handler
        test_event = Event(MOUSEBUTTONDOWN, {
            'button': 1
        })

        controller.invoke_handlers(test_event)
        self.assertTrue(test_object.test_function_has_been_called)

    def test_invoke_handler_mousemotion(self):
        controller = InputController()
        test_object = TestObject()

        controller.register_handler(InputAction.MOTION, None, test_object.test_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.MOTION, None)]) > 0)

        # Try to invoke the handler
        test_event = Event(MOUSEMOTION, {})

        controller.invoke_handlers(test_event)
        self.assertTrue(test_object.test_function_has_been_called)

    def test_invoke_handler_accepting_input(self):
        controller = InputController()
        test_object = TestObject()

        controller.register_handler(InputAction.PRESS, Key.CONFIRM, test_object.test_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) > 0)

        # Try to invoke the handler
        test_event = Event(KEYDOWN, {
            'key': K_RETURN
        })

        controller.invoke_handlers(test_event)
        self.assertTrue(test_object.test_function_has_been_called)

        # Disable accepting input and try to invoke the handler
        test_object.test_function_has_been_called = False
        test_object.accepting_input = False

        # Try to invoke the handler again
        test_event = Event(KEYDOWN, {
            'key': K_RETURN
        })

        controller.invoke_handlers(test_event)
        self.assertFalse(test_object.test_function_has_been_called)

    def test_remove_handler(self):
        controller = InputController()
        test_object = TestObject()

        controller.register_handler(InputAction.PRESS, Key.CONFIRM, test_object.test_function)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) > 0)

        controller.unregister_handlers(test_object)
        self.assertTrue(len(controller.__subscribers__[(InputAction.PRESS, Key.CONFIRM)]) == 0)

        # Try (and fail) to invoke the handler
        test_event = Event(KEYDOWN, {
            'key': K_RETURN
        })

        controller.invoke_handlers(test_event)
        self.assertFalse(test_object.test_function_has_been_called)
