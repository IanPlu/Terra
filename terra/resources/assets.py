import pygame
from terra.constants import Team
from terra.map.tiletype import TileType
from terra.event import *
from terra.util.drawingutil import get_nine_slice_sprites, get_sprites_from_strip, \
    swap_palette, generate_palette_list, swap_multiple_palette

# General
unit_palette = {
    Team.RED: generate_palette_list(pygame.image.load("resources/sprites/palettes/Red-Palette.png")),
    Team.BLUE: generate_palette_list(pygame.image.load("resources/sprites/palettes/Blue-Palette.png")),
}

# UI
spr_cursor = {
    Team.RED: pygame.image.load("resources/sprites/ui/Cursor.png")
}
spr_textbox = {
    Team.RED: get_nine_slice_sprites(pygame.image.load("resources/sprites/ui/Textbox_9slice.png"), 8)
}
spr_phase_indicator = [
    pygame.image.load("resources/sprites/ui/Phase_Icons0.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons1.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons2.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons3.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons4.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons5.png"),
    pygame.image.load("resources/sprites/ui/Phase_Icons6.png")
]

# Tile
spr_tile_selectable = pygame.image.load("resources/sprites/tiles/Tile_Selectable.png")
spr_tiles = {
    TileType.NONE: [pygame.image.load("resources/sprites/tiles/Tile_None.png")],
    TileType.SEA: get_sprites_from_strip(pygame.image.load("resources/sprites/tiles/Tile_Sea.png"), 24),
    TileType.GRASS: [pygame.image.load("resources/sprites/tiles/Tile_Grass.png")],
    TileType.WOODS: [pygame.image.load("resources/sprites/tiles/Tile_Woods.png")]
}
spr_coast_detail = {
    0: None,
    1: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail1.png"),
    2: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail2.png"),
    3: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail3.png"),
    4: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail4.png"),
    5: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail5.png"),
    6: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail6.png"),
    7: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail7.png"),
    8: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail8.png"),
    9: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail9.png"),
    10: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail10.png"),
    11: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail11.png"),
    12: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail12.png"),
    13: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail13.png"),
    14: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail14.png"),
    15: pygame.image.load("resources/sprites/tiles/coasts/Tile_CoastDetail15.png"),
}


# Units
spr_unit_colonist = {
    Team.RED: pygame.image.load("resources/sprites/units/Colonist.png"),
}
spr_unit_trooper = {
    Team.RED: pygame.image.load("resources/sprites/units/Trooper.png"),
}
spr_unit_ranger = {
    Team.RED: pygame.image.load("resources/sprites/units/Ranger.png"),
}
spr_unit_ghost = {
    Team.RED: pygame.image.load("resources/sprites/units/Ghost.png"),
}
spr_base_order_flags = get_nine_slice_sprites(pygame.image.load("resources/sprites/units/OrderFlags.png"), 8)
spr_order_flags = {
    MENU_CANCEL_ORDER: spr_base_order_flags[0],
    MENU_MOVE: spr_base_order_flags[1],
    MENU_RANGED_ATTACK: spr_base_order_flags[2]
}

spr_hp_flags = get_nine_slice_sprites(pygame.image.load("resources/sprites/units/HPFlags.png"), 8)


# Building
spr_building_base = {
    Team.RED: pygame.image.load("resources/sprites/buildings/Base.png")
}


def load_assets():
    palette_swapped_teams = [Team.BLUE]

    for team in palette_swapped_teams:
        spr_cursor[team] = swap_palette(spr_cursor[Team.RED], unit_palette[team])
        spr_unit_colonist[team] = swap_palette(spr_unit_colonist[Team.RED], unit_palette[team])
        spr_unit_trooper[team] = swap_palette(spr_unit_trooper[Team.RED], unit_palette[team])
        spr_unit_ranger[team] = swap_palette(spr_unit_ranger[Team.RED], unit_palette[team])
        spr_unit_ghost[team] = swap_palette(spr_unit_ghost[Team.RED], unit_palette[team])
        spr_textbox[team] = swap_multiple_palette(spr_textbox[Team.RED], unit_palette[team])
        spr_building_base[team] = swap_palette(spr_building_base[Team.RED], unit_palette[team])
