from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.economy.resourcetypes import ResourceType
from terra.effects.effecttype import EffectType
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.managers.managers import Managers
from terra.resources.assets import clear_color, phase_text, spr_cursor, spr_phase_indicator, \
    spr_resource_icon_carbon, spr_resource_icon_minerals, spr_resource_icon_gas, spr_digit_icons, \
    text_notifications, spr_turn_submitted_indicator
from terra.team import Team
from terra.ui.toastnotification import ToastNotification
from terra.util.drawingutil import draw_resource_count


# Renders a UI at the bottom of the screen
class PhaseBar(GameObject):
    def __init__(self, team):
        super().__init__()

        self.team = team
        self.toast = None

    def remove_toast_notification(self):
        self.toast = None

    def step(self, event):
        if self.toast:
            self.toast.step(event)

        if is_event_type(event, E_INVALID_MOVE_ORDERS, E_INVALID_BUILD_ORDERS, E_INVALID_UPGRADE_ORDERS):
            if event.team == self.team:
                self.toast = ToastNotification(self, text_notifications[event.event_type], self.team)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.toast:
            self.toast.render(game_screen, ui_screen)

        # Render phase indicator bar
        ui_screen.fill(clear_color[self.team], (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))

        x = 0
        for x in range(len(spr_phase_indicator[self.team])):
            ui_screen.blit(spr_phase_indicator[self.team][x], (x * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
        ui_screen.blit(spr_cursor[self.team], (Managers.turn_manager.phase.value * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render phase indicator text
        x += 1
        ui_screen.blit(phase_text[self.team][Managers.turn_manager.phase],
                       (4 + GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT + 6))

        # Render resource counts
        x += 3
        resource_counts = draw_resource_count([spr_resource_icon_carbon, spr_resource_icon_minerals,
                                               spr_resource_icon_gas], spr_digit_icons, self.team,
                                              [Managers.team_manager.resources[self.team][ResourceType.CARBON],
                                               Managers.team_manager.resources[self.team][ResourceType.MINERALS],
                                               Managers.team_manager.resources[self.team][ResourceType.GAS]])
        ui_screen.blit(resource_counts, (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render turn submission status
        x += 3
        for team in Team:
            if Managers.team_manager.turn_submitted[team]:
                ui_screen.blit(spr_turn_submitted_indicator[team], (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))
            x += 1
