from terra.engine.gameobject import GameObject
from terra.constants import *
from terra.settings import *
from terra.util.drawingutil import draw_three_digit_number
from terra.resources.assets import clear_color, phase_text, spr_cursor, spr_phase_indicator, \
    spr_resource_icon_carbon, spr_resource_icon_minerals, spr_resource_icon_gas, spr_digit_icons


# Renders a UI at the bottom of the screen
class PhaseBar(GameObject):
    def __init__(self, team, team_manager, battle):
        super().__init__()

        self.team = team
        self.team_manager = team_manager
        self.battle = battle

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        # Render phase indicator bar
        ui_screen.fill(clear_color[self.team], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        for x in range(len(spr_phase_indicator[self.team])):
            ui_screen.blit(spr_phase_indicator[self.team][x], (x * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[self.team], (self.battle.phase.value * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render phase indicator text
        x = x + 1
        ui_screen.blit(phase_text[self.battle.phase],
                       (4 + GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT + 6))

        # Render resource counts
        x = x + 3
        ui_screen.blit(spr_resource_icon_carbon[self.team], (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(draw_three_digit_number(spr_digit_icons, self.team_manager.carbon[self.team], self.team),
                       (GRID_WIDTH * x, RESOLUTION_HEIGHT - 8))
        x = x + 1
        ui_screen.blit(spr_resource_icon_minerals[self.team], (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(draw_three_digit_number(spr_digit_icons, self.team_manager.minerals[self.team], self.team),
                       (GRID_WIDTH * x, RESOLUTION_HEIGHT - 8))
        x = x + 1
        ui_screen.blit(spr_resource_icon_gas[self.team], (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(draw_three_digit_number(spr_digit_icons, self.team_manager.gas[self.team], self.team),
                       (GRID_WIDTH * x, RESOLUTION_HEIGHT - 8))

