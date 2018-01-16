import pygame
from enum import Enum

pygame.font.init()


class Font(Enum):
    COURIER = pygame.font.SysFont('Arial', 11)


def swap_palette():
    # TODO: do some pixelarray magic
    pass


# Create a blittable surface with the provided text
def draw_text(text, color):
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
