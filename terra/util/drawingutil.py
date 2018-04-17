import pygame

from terra.util.mathutil import clamp

pygame.font.init()


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
    from terra.resources.assets import font_pixelmix

    if shadow_color:
        background = font_pixelmix.render(text, False, shadow_color)
        foreground = font_pixelmix.render(text, False, color)

        text_size = background.get_size()
        text_surface = pygame.Surface((text_size[0] + 1, text_size[1] + 1), pygame.SRCALPHA, 32)

        text_surface.blit(background, (1, 1))
        text_surface.blit(background, (0, 1))
        text_surface.blit(foreground, (0, 0))
        return text_surface
    else:
        return font_pixelmix.render(text, False, color)


# Create a blittable surface with the provided text. Long text will wrap to the provided width in pixels.
# https://stackoverflow.com/a/42015712
def draw_multiline_text(text, color, shadow_color=None, width=192, height=192):
    from terra.resources.assets import font_pixelmix

    words = [word.split(' ') for word in text.splitlines()]
    space = font_pixelmix.size(' ')[0]

    text_surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)

    x = 0
    y = 0
    word_height = 0
    total_height = 0

    for line in words:
        for word in line:
            word_surface = font_pixelmix.render(word, False, color)
            word_width, word_height = word_surface.get_size()

            # Handle control characters
            if word == "\n":
                x = 0
                y += word_height
                total_height += word_height

            if x + word_width >= width:
                x = 0
                y += word_height
                total_height += word_height

            if shadow_color:
                shadow_surface = font_pixelmix.render(word, False, shadow_color)
                text_surface.blit(shadow_surface, (x + 1, y + 1))

            text_surface.blit(word_surface, (x, y))

            x += word_width + space

        x = 0
        y += word_height
        total_height += word_height

    if total_height < height:
        # Trim the surface, with a little wiggle room
        return text_surface.subsurface((0, 0, width, total_height + 24))
    else:
        return text_surface


# Return a list of sprites of the provided width from a sprite strip.
def get_sprites_from_strip(sprite, width):
    sprites = []
    strip_width, height = sprite.get_size()

    for x in range(strip_width // width):
        sprites.append(sprite.subsurface((x * width, 0, width, height)))

    return sprites


# Return a list of sprites, sliced for an animated indexed sprite. Assumes vertical rows are for animation frames.
# Returns: sprite[animation_frame][index]
def get_indexed_sprites_from_strip(sprite, width, height):
    sprites = []
    strip_width, strip_height = sprite.get_size()

    for y in range(strip_height // height):
        animated_sprites = []
        for x in range(strip_width // width):
            animated_sprites.append(sprite.subsurface((x * width, y * height, width, height)))
        sprites.append(animated_sprites)

    return sprites


# Return a list of sprites cut out of the provided sprite, which is subdivided into a 3x3 grid.
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
    # Restrict the number to 3 digits
    formatted_number = "{}".format(clamp(number, 0, 999))
    display = pygame.Surface((24, 8), pygame.SRCALPHA, 32)

    x = 16
    digits = [int(digit) for digit in formatted_number]
    digits.reverse()
    for digit in digits:
        if digit != -1:
            display.blit(spr_digit_icons[team][digit], (x, 0))
        x -= 8
    return display


# Return a 24x24 px surface containing a large display of the provided resource count.
def draw_resource_count(spr_resource_icon, spr_digit_icons, team, count):
    display = pygame.Surface((24, 24), pygame.SRCALPHA, 32)
    display.blit(spr_resource_icon[team], (0, 0))
    display.blit(draw_three_digit_number(spr_digit_icons, count, team), (0, 16))
    return display


# Return a 24x8 px surface containing a small display of the provided resource count.
def draw_small_resource_count(clear_color, spr_resource_icon_small, spr_digit_icons, team, count):
    display = pygame.Surface((24, 8), pygame.SRCALPHA, 32)
    display.fill(clear_color[team], (0, 0, 24, 8))
    display.blit(draw_three_digit_number(spr_digit_icons, count, team), (0, 0))
    display.blit(spr_resource_icon_small[team], (0, 0))
    return display
