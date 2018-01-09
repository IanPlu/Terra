import sys
from terra.map import Map
from terra.cursor import Cursor
from terra.unit import *

# Initialize pygame and some UI settings
pygame.init()
resolution = width, height = 240, 240
screen_resolution = screen_width, screen_height = width * SCREEN_SCALE, height * SCREEN_SCALE
clear_color = 80, 126, 163

screen = pygame.display.set_mode(screen_resolution)

# Set up some game objects
game_objects = []
mapname = "map1.txt"
game_map = Map(mapname)
cursor = Cursor(game_map)

# Create some units and place them on the map
unitr1 = Unit(game_map, UnitType.COLONIST, Team.RED, 1, 1)
unitr2 = Unit(game_map, UnitType.TROOPER, Team.RED, 2, 1)
unitb1 = Unit(game_map, UnitType.COLONIST, Team.BLUE, 8, 8)
unitb2 = Unit(game_map, UnitType.TROOPER, Team.BLUE, 7, 8)

# TODO: Make a rendering depth system
game_objects.append(game_map)
game_objects.extend([unitr1, unitr2, unitb1, unitb2])
game_objects.append(cursor)


# Step phase of game loop - handle events
def step(event):
    for obj in game_objects:
        obj.step(event)


# Render phase of game loop - draw to the screen
def render():
    canvas = pygame.Surface(resolution)
    canvas.fill(clear_color)

    for obj in game_objects:
        obj.render(canvas)

    pygame.transform.scale(canvas, (screen_width, screen_height), screen)
    pygame.display.flip()


# Game loop
while 1:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        step(event)
    render()


