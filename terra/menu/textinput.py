import pygame
from pygame.constants import KEYDOWN, K_BACKSPACE, KMOD_CTRL

from terra.constants import RESOLUTION_WIDTH, RESOLUTION_HEIGHT
from terra.control.inputcontroller import InputAction
from terra.control.keybindings import Key
from terra.engine.gameobject import GameObject
from terra.event.event import EventType, publish_game_event
from terra.resources.assets import shadow_color, light_color
from terra.strings import get_text, label_strings
from terra.team import Team
from terra.util.drawingutil import draw_text

# Common input filter strings
FILTER_NUMBERS = "0123456789"
FILTER_LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
FILTER_UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
FILTER_ALPHANUMERIC = FILTER_NUMBERS + FILTER_LOWERCASE + FILTER_UPPERCASE
FILTER_FILENAME = FILTER_ALPHANUMERIC + "_- s"
FILTER_IP = FILTER_ALPHANUMERIC + ".:"


# A text input field for use in the main menu.
# Allows the player to input a name for a map file, ip address, etc.
# - label: label string displayed above the input box, from the 'label_strings' group.
# - option: tag for the event fired when the text input completes.
# - default_text: default placeholder text initially in the input box.
# - input_filter: string containing the only valid characters for this text input.
class TextInput(GameObject):
    def __init__(self, label, tag, default_text="", input_filter=FILTER_ALPHANUMERIC):
        super().__init__()

        self.label = label
        self.input_filter = input_filter
        self.tag = tag

        self.width = 24 * 8
        self.height = 16
        self.x = (RESOLUTION_WIDTH - self.width) // 2
        self.y = (RESOLUTION_HEIGHT - self.height) // 2

        self.current_text = default_text

    def register_input_handlers(self, input_handler):
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.submit_text)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.cancel_text)

    # Add the specified character to the current text, obeying any input filter we may have.
    def append_char(self, char):
        if char in self.input_filter:
            self.current_text += char

    # Delete the last character from the current text.
    def delete_char(self):
        self.current_text = self.current_text[:-1]

    # Delete all characters from the current text.
    def delete_all(self):
        self.current_text = ""

    # Submit the current text, firing an event.
    def submit_text(self):
        if len(self.current_text) > 0:
            publish_game_event(EventType.TEXT_SUBMIT_INPUT, {
                "tag": self.tag,
                "input": self.current_text,
            })

    # Cancel text input and return.
    def cancel_text(self):
        publish_game_event(EventType.TEXT_CANCEL_INPUT, {
            "tag": self.tag,
            "input": None,
        })

    def step(self, event):
        super().step(event)

        # Note: this class directly looks for input events rather than using the input controller,
        # since it needs to get individual keystrokes and letters.
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE and len(self.current_text) > 0:
                if pygame.key.get_mods() & KMOD_CTRL:
                    self.delete_all()
                else:
                    self.delete_char()
            elif event.unicode and len(self.current_text) < 32:
                self.append_char(event.unicode)

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        label_text = get_text(label_strings, self.label)
        ui_screen.blit(label_text, (self.x, self.y - 24))

        # Draw the text box
        ui_screen.fill(light_color, (self.x - 1, self.y - 1, self.width + 3, self.height + 3))
        ui_screen.fill(shadow_color[Team.RED], (self.x, self.y, self.width, self.height))

        # Draw the current text
        rendered_text = self.current_text + "|" if len(self.current_text) >= 32 else self.current_text + "_"
        text = draw_text(rendered_text, light_color)
        ui_screen.blit(text, (self.x + 4, self.y + 2))

