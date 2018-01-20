import pygame
from enum import Enum

pygame.font.init()


class Font(Enum):
    COURIER = pygame.font.SysFont('Arial', 11)


# Generate a list of colors in the provided image as a palette
def generate_palette_list(palette):
    return palette.get_palette()


# Return a sprite with the provided palette
def swap_palette(sprite, palette):
    new_sprite = sprite.copy()
    new_sprite.set_palette(palette)
    return new_sprite


# Swap the palette of a list of sprites
def swap_multiple_palette(sprites, palette):
    new_sprites = []
    for sprite in sprites:
        new_sprites.append(swap_palette(sprite, palette))
    return new_sprites


# Create a blittable surface with the provided text
def draw_text(text, color, shadow_color=None):
    if shadow_color:
        background = Font.COURIER.value.render(text, False, shadow_color)
        foreground = Font.COURIER.value.render(text, False, color)

        text_size = background.get_size()
        text_surface = pygame.Surface((text_size[0] + 1, text_size[1] + 1), pygame.SRCALPHA, 32)

        text_surface.blit(background, (1, 1))
        text_surface.blit(foreground, (0, 0))
        return text_surface
    else:
        return Font.COURIER.value.render(text, False, color)


def get_sprites_from_strip(sprite, width):
    sprites = []
    strip_width, height = sprite.get_size()

    for x in range(strip_width // width):
        sprites.append(sprite.subsurface((x * width, 0, width, height)))

    return sprites


# Return a list of sprites cut out of the provided sprite
def get_nine_slice_sprites(sprite, slice_size):
    sprites = []

    for y in range(3):
        for x in range(3):
            sprites.append(sprite.subsurface((x * slice_size, y * slice_size, slice_size, slice_size)))

    return sprites


# Return a surface of the desired size, using a sprite split into 9 pieces and tiled accordingly.
def draw_nine_slice_sprite(sprites, grid_size, grid_width, grid_height):
    surface = pygame.Surface((grid_width * grid_size, grid_height * grid_size), pygame.SRCALPHA, 32)

    # Draw top row
    surface.blit(sprites[0], (0, 0))
    x = 1
    y = 0
    while x < grid_width - 1:
        surface.blit(sprites[1], (x * grid_size, y * grid_size))
        x += 1
    surface.blit(sprites[2], (x * grid_size, y * grid_size))

    # Draw middle row
    y = 1
    while y < grid_height - 1:
        surface.blit(sprites[3], (0, y * grid_size))
        x = 1
        while x < grid_width - 1:
            surface.blit(sprites[4], (x * grid_size, y * grid_size))
            x += 1
        surface.blit(sprites[5], (x * grid_size, y * grid_size))
        y += 1

    # Draw bottom row
    surface.blit(sprites[6], (0, y * grid_size))
    x = 1
    while x < grid_width - 1:
        surface.blit(sprites[7], (x * grid_size, y * grid_size))
        x += 1
    surface.blit(sprites[8], (x * grid_size, y * grid_size))

    return surface


# Return a surface containing a three digit number in 8x8 digit sprites
def draw_three_digit_number(spr_digit_icons, number, team):
    formatted_number = "{0:0=3d}".format(number)

    digits = [int(digit) for digit in str(formatted_number)]
    display = pygame.Surface((len(digits) * 8, 8))

    x = 0
    for digit in digits:
        display.blit(spr_digit_icons[team][digit], (x, 0))
        x = x + 8
    return display
