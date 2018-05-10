from terra.event.eventbus import EVENT_BUS
# TODO: Game screens shouldn't need the input controller-- input should be handled by a delegate
from terra.control.inputcontroller import INPUT_CONTROLLER
from terra.managers.session import SESSION


# Base game screen class.
# Game screens manage, contain, and display multiple GameObjects.
# They are similar to GameObjects, but produce a game screen to show on render.
# New full screens, like different game modes or menus, should extend from this.
# TODO: Game screens should not make use of the input handler
class GameScreen:
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

    # Get a reference to a manager object in the Session.
    def get_manager(self, manager_type):
        return SESSION.get(manager_type)

    # Return the current game mode.
    def get_mode(self):
        return SESSION.current_mode

    # Return whether this is a network game or not
    def is_network_game(self):
        return SESSION.is_network_game

    def step(self, event):
        pass

    def render(self, ui_screen):
        return None
