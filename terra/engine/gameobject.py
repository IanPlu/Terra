from terra.event.eventbus import EVENT_BUS
from terra.control.inputcontroller import INPUT_CONTROLLER


# Base game object class.
# Objects that should be part of the game loop cycle (step, render, etc.)
# should extend from this and implement its methods. Provides hooks to the event bus and input handler.
class GameObject:
    def __init__(self):
        self.register_handlers(EVENT_BUS)
        self.register_input_handlers(INPUT_CONTROLLER)

    def __del__(self):
        self.destroy()

    # Called when the screen is no longer being used.
    # Screens should ensure that their child objects also call destroy()!
    def destroy(self):
        EVENT_BUS.unregister_handlers(self)
        INPUT_CONTROLLER.unregister_handlers(self)

    # Invoked on creation.
    # Set up any event listeners here.
    def register_handlers(self, event_bus):
        pass

    # Invoked on creation.
    # Set up any control input listeners here.
    def register_input_handlers(self, input_handler):
        pass

    # Return true if this game object should react to input events.
    # Objects that only want to react to controller inputs while they're 'active' should override this method.
    def is_accepting_input(self):
        return True

    # Return true if this game object should react to its watched events.
    # Objects that only want to react to events while they're 'active' should override this method
    def is_accepting_events(self):
        return True

    # Invoked for every event on the queue.
    # Do state changes and any logic that should run for every event and logic loop tick
    def step(self, event):
        pass

    # Invoked every frame of rendering.
    # Draw to the provided screen.
    def render(self, game_screen, ui_screen):
        pass
