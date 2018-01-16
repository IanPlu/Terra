

# Base game object class.
# Objects that should be part of the game loop cycle (step, render, etc.)
# should extend from this and implement its methods.
class GameObject:

    def __init__(self):
        pass

    # Invoked for every event on the queue.
    # Handle events and do state changes.
    def step(self, event):
        pass

    # Invoked every frame of rendering.
    # Draw to the provided screen.
    def render(self, screen):
        pass
