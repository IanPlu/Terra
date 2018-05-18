from sys import exc_info

from pygame import USEREVENT

from terra.event.event import FROM_NETWORK


# Handles and stores event subscribers, and marshals events to them as needed.
# Do not instantiate a new EventBus-- just import and use the static methods.
class EventBus:
    def __init__(self):
        # Format: subscribers[EventType] = [callback1, callback2...]
        self.__subscribers__ = {}

    # Add a new handler for the provided event type. When that event is caught, it'll invoke the callback method.
    # If local_only=True, the handler will only fire for events originating from this machine
    # Callback signature: (event) -> None
    def register_handler(self, event_type, callback, local_only=False):
        existing_handlers = self.__subscribers__.get(event_type)
        new_handler = (callback, local_only)

        if existing_handlers:
            existing_handlers.insert(0, new_handler)
        else:
            self.__subscribers__[event_type] = [new_handler]

    def register_multiple_handlers(self, callback, *event_types):
        for event_type in event_types:
            self.register_handler(event_type, callback)

    # Find all handlers associated with the passed in instance object and remove them
    def unregister_handlers(self, owner):
        for event_type, handlers in self.__subscribers__.items():
            for handler, _ in handlers:
                if handler.__self__ == owner:
                    self.__subscribers__[event_type].remove((handler, _))

    # For the provided event, invoke any handlers we have
    def invoke_handlers(self, event):
        # For each event, find any subscribers we may have for this event type
        if event.type == USEREVENT:
            is_local_event = not hasattr(event, FROM_NETWORK)

            event_handlers = self.__subscribers__.get(event.event_type)
            if event_handlers:
                for handler, local_only in event_handlers:
                    if ((local_only and is_local_event) or (not local_only)) and \
                            handler.__self__.is_accepting_events():
                        try:
                            handler(event)
                        except:
                            exc = exc_info()
                            raise exc[0].with_traceback(exc[1], exc[2])


EVENT_BUS = EventBus()
