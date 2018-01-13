import sys
from terra.battle import Battle
from terra.units.unit import *

# Initialize pygame and some UI settings
pygame.init()
screen_resolution = screen_width, screen_height = RESOLUTION_WIDTH * SCREEN_SCALE, RESOLUTION_HEIGHT * SCREEN_SCALE


screen = pygame.display.set_mode(screen_resolution)

battle = Battle()
game_objects = [battle]


# Step phase of game loop - handle events
def step(event):
    for obj in game_objects:
        obj.step(event)


# Render phase of game loop - draw to the screen
def render():
    canvas = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT))
    canvas.fill(CLEAR_COLOR)

    for obj in game_objects:
        obj.render(canvas)

    pygame.transform.scale(canvas, (screen_width, screen_height), screen)
    pygame.display.flip()


clock = pygame.time.Clock()

# Game loop
while True:
    # Update game tick TICK_RATE times per second
    clock.tick(TICK_RATE)

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()

        step(event)

    # TODO: Separate out rendering loop from logic loop
    render()
