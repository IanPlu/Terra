import sys
from terra.battle import Battle
from terra.leveleditor import LevelEditor
from terra.piece.unit.unit import *
from terra.resources.assets import load_assets, clear_color
from terra.settings import *
from enum import Enum


class Mode(Enum):
    BATTLE = 0
    EDIT = 1


# Initialize pygame and some UI settings
pygame.init()
screen_resolution = screen_width, screen_height = RESOLUTION_WIDTH * SCREEN_SCALE, RESOLUTION_HEIGHT * SCREEN_SCALE


screen = pygame.display.set_mode(screen_resolution)
screen.fill(clear_color[Team.RED])

load_assets()
mode = Mode.BATTLE
if mode == Mode.EDIT:
    level_editor = LevelEditor()
else:
    battle = Battle()


# Step phase of game loop - handle events
def step(event):
    if mode == Mode.BATTLE:
        battle.step(event)
    elif mode == Mode.EDIT:
        level_editor.step(event)


# Render phase of game loop - draw to the screen
def render():
    ui_screen = pygame.Surface((RESOLUTION_WIDTH, RESOLUTION_HEIGHT), pygame.SRCALPHA, 32)
    ui_screen = ui_screen.convert_alpha()

    if mode == Mode.BATTLE:
        # Render the battle
        game_screen = battle.render(ui_screen)
        # Combine the game screen and UI
        game_screen.blit(ui_screen, (0, 0))
    else:
        # Render the map editor
        game_screen = level_editor.render(ui_screen)
        # Combine the game screen and UI
        game_screen.blit(ui_screen, (0, 0))
    pygame.transform.scale(game_screen, (screen_width, screen_height), screen)
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
