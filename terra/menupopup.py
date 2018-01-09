from terra.settings import *
from terra.constants import *
from terra.strings import menu_option_strings
from terra.gameobject import GameObject
from terra.drawingutil import draw_text, draw_nine_slice_sprite

textbox_base = pygame.image.load("resources/sprites/ui/Textbox_9slice.png")
menu_option_cursor = pygame.image.load("resources/sprites/ui/Cursor.png")

# Slice into 9 pieces, with a width of 8. In order from left to right, top to bottom
textbox_sprites = [
    textbox_base.subsurface((0, 0, 8, 8)),
    textbox_base.subsurface((8, 0, 8, 8)),
    textbox_base.subsurface((16, 0, 8, 8)),
    textbox_base.subsurface((0, 8, 8, 8)),
    textbox_base.subsurface((8, 8, 8, 8)),
    textbox_base.subsurface((16, 8, 8, 8)),
    textbox_base.subsurface((0, 16, 8, 8)),
    textbox_base.subsurface((8, 16, 8, 8)),
    textbox_base.subsurface((16, 16, 8, 8))
]

# menu_option_sprites = {
#     MenuOptions.MOVE_N: pygame.image.load("resources/sprites/ui/MenuOption_N.png"),
#     MenuOptions.MOVE_E: pygame.image.load("resources/sprites/ui/MenuOption_E.png"),
#     MenuOptions.MOVE_S: pygame.image.load("resources/sprites/ui/MenuOption_S.png"),
#     MenuOptions.MOVE_W: pygame.image.load("resources/sprites/ui/MenuOption_W.png")
# }

menu_option_text = {
    MENU_MOVE_N: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE_N], (0, 0, 0)),
    MENU_MOVE_E: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE_E], (0, 0, 0)),
    MENU_MOVE_S: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE_S], (0, 0, 0)),
    MENU_MOVE_W: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE_W], (0, 0, 0)),
    MENU_CANCEL_ORDER: draw_text(menu_option_strings[LANGUAGE][MENU_CANCEL_ORDER], (0, 0, 0))
}

grid_size = 8
option_height = 24


# A menu popup containing multiple selectable menu options
class MenuPopup(GameObject):
    def __init__(self, tx=0, ty=0, team=Team.RED, options=None):
        super().__init__()

        # Tile the menu is for
        self.tx = tx
        self.ty = ty

        # Rendered coords
        # TODO: Avoid collisions with edges
        self.x = (self.tx + 1) * GRID_WIDTH
        self.y = self.ty * GRID_HEIGHT

        self.team = team

        self.subgrid_width = 9
        self.subgrid_height = 3 * len(options)

        self.options = options

        self.num_options = len(options)
        self.option_pos = 0

    def confirm(self):
        pygame.event.post(pygame.event.Event(E_CLOSE_MENU, {
            'gx': self.tx,
            'gy': self.ty,
            'option': self.options[self.option_pos],
            'team': self.team
        }))

    def cancel(self):
        pygame.event.post(pygame.event.Event(E_CLOSE_MENU, {}))

    def cursor_up(self):
        self.option_pos -= 1
        if self.option_pos < 0:
            self.option_pos = self.num_options - 1

    def cursor_down(self):
        self.option_pos += 1
        if self.option_pos > self.num_options - 1:
            self.option_pos = 0

    def step(self, event):
        super().step(event)

        if event.type == KEYDOWN:
            if event.key in KB_UP:
                self.cursor_up()
            elif event.key in KB_DOWN:
                self.cursor_down()
            elif event.key in KB_CONFIRM:
                self.confirm()
            elif event.key in (KB_CANCEL, KB_MENU):
                self.cancel()
        elif event.type == MOUSEMOTION:
            # Determine if the mouse is in the popup window
            mouse_coords = pygame.mouse.get_pos()
            mousex = int(mouse_coords[0] / SCREEN_SCALE)
            mousey = int(mouse_coords[1] / SCREEN_SCALE)

            min_x = self.x
            min_y = self.y + 8
            max_x = min_x + self.subgrid_width * grid_size
            max_y = min_y + self.subgrid_height * grid_size

            if min_x < mousex < max_x and min_y < mousey < max_y:
                # Determine where in the menu we are for the option pos
                self.option_pos = (mousey - min_y) // option_height
        elif event.type == MOUSEBUTTONDOWN:
            if event.button in KB_CONFIRM:
                self.confirm()
            elif event.button in KB_CANCEL:
                self.cancel()

    def render(self, screen):
        super().render(screen)

        screen.blit(draw_nine_slice_sprite(textbox_sprites, grid_size, self.subgrid_width, self.subgrid_height + 1),
                    (self.x, self.y))

        row_y = 0
        for option in self.options:
            # screen.blit(menu_option_sprites[option], (rx, ry + 8 + y * option_height))
            screen.blit(menu_option_text[option], (self.x + 24, self.y + 16 + row_y * option_height))
            row_y += 1

        # Render the option cursor
        screen.blit(menu_option_cursor, (self.x, self.y + 8 + self.option_pos * option_height))
