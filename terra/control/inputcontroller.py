from enum import Enum

from pygame import KEYDOWN, KEYUP, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP

from terra.control.keybindings import translate_input, translate_mouse_button


class InputAction(Enum):
    PRESS = [KEYDOWN, MOUSEBUTTONDOWN]
    RELEASE = [KEYUP, MOUSEBUTTONUP]
    MOTION = MOUSEMOTION


# Similar to the EventBus, handles and stores subscribers to input events like keydown, mousedown, etc.
# When a handler is invoked, it'll call the 'is_accepting_input' method on the owning object before invoking.
class InputController:
    def __init__(self):
        # Format: subscribers[(input_action, key)] = [callback1, callback2...]
        self.__subscribers__ = {}

    # Add a new handler for the provided input action and key. When that input is caught, invoke the callback.
    # Callback signature: () -> None
    def register_handler(self, input_action, key, callback):
        existing_handlers = self.__subscribers__.get((input_action, key))
        if existing_handlers:
            # Insert to the front, in case an object was created + registered input handlers as a result of an input.
            existing_handlers.insert(0, callback)
        else:
            self.__subscribers__[(input_action, key)] = [callback]

    # Find all handlers associated with the passed in instance object and remove them
    def unregister_handlers(self, owner):
        for (input_action, key), handlers in self.__subscribers__.items():
            for handler in handlers:
                if handler.__self__ == owner:
                    self.__subscribers__[(input_action, key)].remove(handler)

    # For the provided event, determine if it's an input action and translate the key.
    # If we have any handlers matching that input + key, invoke 'em
    def invoke_handlers(self, event):
        if event.type == KEYDOWN:
            event_handlers = self.__subscribers__.get((InputAction.PRESS, translate_input(event.key)))
        elif event.type == KEYUP:
            event_handlers = self.__subscribers__.get((InputAction.RELEASE, translate_input(event.key)))
        elif event.type == MOUSEBUTTONDOWN:
            event_handlers = self.__subscribers__.get((InputAction.PRESS, translate_mouse_button(event.button)))
        elif event.type == MOUSEBUTTONUP:
            event_handlers = self.__subscribers__.get((InputAction.RELEASE, translate_mouse_button(event.button)))
        elif event.type == MOUSEMOTION:
            event_handlers = self.__subscribers__.get((InputAction.MOTION, None))
        else:
            event_handlers = None

        if event_handlers:
            for handler in event_handlers:
                if handler.__self__.is_accepting_input():
                    handler()


INPUT_CONTROLLER = InputController()
