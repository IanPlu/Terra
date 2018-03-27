from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.engine.gameobject import GameObject
from terra.event import *
from terra.managers.managers import Managers
from terra.resources.assets import clear_color, spr_cursor, spr_phase_indicator, spr_resource_icon, spr_digit_icons, \
    spr_turn_submitted_indicator, light_color
from terra.strings import get_text, get_formatted_text, notification_strings, phase_strings
from terra.ui.toastnotification import ToastNotification
from terra.util.drawingutil import draw_resource_count
from terra.battlephase import BattlePhase


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

        if is_event_type(event, E_INVALID_MOVE_ORDERS, E_INVALID_BUILD_ORDERS, E_INVALID_UPGRADE_ORDERS,
                         NETWORK_CONNECTED_TO_HOST, NETWORK_DISCONNECTED_FROM_HOST):
            if event.team == self.team:
                self.toast = ToastNotification(self, get_text(notification_strings, event.event_type, light=True), self.team)
        elif is_event_type(event, NETWORK_CLIENT_CONNECTED, NETWORK_CLIENT_DISCONNECTED):
            if event.team == self.team:
                self.toast = ToastNotification(self, get_formatted_text(notification_strings, event.event_type, True, event.nickname), self.team)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        if self.toast:
            self.toast.render(game_screen, ui_screen)

        # Render phase indicator bar
        ui_screen.fill(light_color, (0, RESOLUTION_HEIGHT - GRID_HEIGHT, RESOLUTION_WIDTH, GRID_HEIGHT))
        ui_screen.fill(clear_color[self.team], (1, RESOLUTION_HEIGHT - GRID_HEIGHT + 1, RESOLUTION_WIDTH - 2, GRID_HEIGHT - 3))

        x = 0
        for phase in BattlePhase:
            ui_screen.blit(spr_phase_indicator[self.team][phase.value], (x * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))
            x += 1
        ui_screen.blit(spr_cursor[self.team], (Managers.turn_manager.phase.value * GRID_WIDTH, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render phase indicator text
        ui_screen.blit(get_text(phase_strings, Managers.turn_manager.phase),
                       (4 + GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT + 6))

        # Render resource count
        x += 3
        ui_screen.blit(draw_resource_count(spr_resource_icon, spr_digit_icons, self.team,
                                           Managers.team_manager.resources[self.team]),
                       (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))

        # Render turn submission status
        x += 1
        for team in Managers.team_manager.get_teams():
            if Managers.team_manager.turn_submitted[team]:
                ui_screen.blit(spr_turn_submitted_indicator[team], (GRID_WIDTH * x, RESOLUTION_HEIGHT - GRID_HEIGHT))
                x += 1
