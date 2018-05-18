from terra.engine.gameobject import GameObject
from terra.control.keybindings import Key
from terra.control.inputcontroller import InputAction
from terra.menu.menu import Menu
from terra.constants import RESOLUTION_WIDTH, HALF_RES_HEIGHT
from terra.strings import tutorial_strings, label_strings, get_text, get_multiline_text
from terra.event.event import publish_game_event, EventType
from terra.sound.soundtype import SoundType


scroll_amount = 12
max_page = 5


# Scrolling tutorial text display
class Tutorial(GameObject):
    def __init__(self):
        super().__init__()

        self.width = RESOLUTION_WIDTH - 48
        self.height = HALF_RES_HEIGHT

        self.current_page = 0
        self.scroll_pos = 0
        self.text = None
        self.scroll_height = 0

        # Set the initial values for the above page / scroll vars
        self.change_page(0)

    def register_input_handlers(self, input_handler):
        super().register_input_handlers(input_handler)

        input_handler.register_handler(InputAction.PRESS, Key.UP, self.scroll_up)
        input_handler.register_handler(InputAction.PRESS, Key.DOWN, self.scroll_down)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_UP, self.scroll_up)
        input_handler.register_handler(InputAction.PRESS, Key.SCROLL_DOWN, self.scroll_down)
        input_handler.register_handler(InputAction.PRESS, Key.CONFIRM, self.confirm)
        input_handler.register_handler(InputAction.PRESS, Key.CANCEL, self.cancel)
        input_handler.register_handler(InputAction.PRESS, Key.MENU, self.cancel)

    def debug_print_scroll(self):
        print(self.scroll_height / self.text.get_height())
        print("{} / {}".format(self.scroll_pos, self.text.get_height()))
        print(self.scroll_pos / self.text.get_height())

    def scroll_up(self):
        if self.scroll_pos > scroll_amount:
            self.scroll_pos -= scroll_amount
        else:
            self.scroll_pos = 0

        # self.debug_print_scroll()

    def scroll_down(self):
        if self.scroll_pos < self.text.get_height() - self.scroll_height - scroll_amount:
            self.scroll_pos += scroll_amount
        else:
            self.scroll_pos = self.text.get_height() - self.scroll_height

        # self.debug_print_scroll()

    def confirm(self):
        if self.current_page < max_page:
            self.change_page(1)
        else:
            self.play_sound(SoundType.CURSOR_CANCEL)
            publish_game_event(EventType.TUTORIAL_EXIT, {})

    def cancel(self):
        if self.current_page > 0:
            self.change_page(-1)
        else:
            self.play_sound(SoundType.CURSOR_CANCEL)
            publish_game_event(EventType.TUTORIAL_EXIT, {})

    def change_page(self, amount):
        self.play_sound(SoundType.CURSOR_SELECT)

        self.current_page += amount
        self.scroll_pos = 0
        self.text = get_multiline_text(tutorial_strings, self.current_page, width=self.width - 24, height=self.height * 2)
        self.scroll_height = min(HALF_RES_HEIGHT - 24, self.text.get_height())

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)

        pos_x = 24
        pos_y = HALF_RES_HEIGHT - 24
        text_height = min(HALF_RES_HEIGHT - 24, self.text.get_height())

        # Draw the menu box + scrollbar
        game_screen.blit(Menu.draw_menu_box(self.width, self.height), (pos_x, pos_y))
        game_screen.blit(Menu.draw_scroll_bar(8, self.height, self.scroll_height, self.scroll_pos, self.text.get_height()),
                         (pos_x + self.width, pos_y))

        # Draw the text subscroll
        scrolled_text = self.text.subsurface((0, self.scroll_pos,
                                              self.text.get_width(), text_height))
        game_screen.blit(scrolled_text, (pos_x + 12, pos_y + 12))

        # Draw the prompt text
        prompt_text = get_text(label_strings, "TUTORIAL_PROMPT")
        game_screen.blit(prompt_text, (pos_x + self.width - prompt_text.get_width(), pos_y + self.height + 8))
