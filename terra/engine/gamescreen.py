

# Base game screen class.
# Game screens manage, contain, and display multiple GameObjects.
# They are similar to GameObjects, but produce a game screen to show on render.
# New full screens, like different game modes or menus, should extend from this.
class GameScreen:
    def __init__(self):
        pass

    def step(self, event):
        pass

    def render(self, ui_screen):
        return None
