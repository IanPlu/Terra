from terra.battlephase import BattlePhase
from terra.constants import GRID_WIDTH, GRID_HEIGHT
from terra.constants import RESOLUTION_HEIGHT, RESOLUTION_WIDTH
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.managers import Managers
from terra.resources.assets import clear_color, spr_cursor, spr_phase_indicator, spr_resource_icon, spr_digit_icons, \
    spr_turn_submitted_indicator, light_color
from terra.strings import get_text, get_formatted_text, notification_strings, phase_strings
from terra.ui.toastnotification import ToastNotification
from terra.util.drawingutil import draw_resource_count


# Renders a UI at the bottom of the screen
class PhaseBar(GameObject):
    def __init__(self, team):
        super().__init__()

        self.team = team
        self.toast = None

    def destroy(self):
        super().destroy()
        if self.toast:
            self.toast.destroy()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_INVALID_MOVE_ORDERS, self.create_toast_from_event)
        event_bus.register_handler(EventType.E_INVALID_BUILD_ORDERS, self.create_toast_from_event)
        event_bus.register_handler(EventType.E_INVALID_UPGRADE_ORDERS, self.create_toast_from_event)
        event_bus.register_handler(EventType.NETWORK_CONNECTED_TO_HOST, self.create_toast_from_event)
        event_bus.register_handler(EventType.NETWORK_DISCONNECTED_FROM_HOST, self.create_toast_from_event)

        event_bus.register_handler(EventType.NETWORK_CLIENT_CONNECTED, self.create_toast_from_network_event)
        event_bus.register_handler(EventType.NETWORK_CLIENT_DISCONNECTED, self.create_toast_from_network_event)

    def create_toast_from_event(self, event):
        if event.team == self.team:
            self.toast = ToastNotification(self, get_text(notification_strings, event.event_type, light=True), self.team)

    def create_toast_from_network_event(self, event):
        if event.team == self.team:
            self.toast = ToastNotification(self, get_formatted_text(notification_strings, event.event_type, True, event.nickname), self.team)

    def remove_toast_notification(self):
        self.toast = None

    def step(self, event):
        if self.toast:
            self.toast.step(event)

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
