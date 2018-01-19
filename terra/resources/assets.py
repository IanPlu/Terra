import pygame
from terra.constants import Team
from terra.map.tiletype import TileType
from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType
from terra.strings import *
from terra.event import *
from terra.settings import LANGUAGE
from terra.util.drawingutil import get_nine_slice_sprites, get_sprites_from_strip, \
    swap_palette, generate_palette_list, swap_multiple_palette, draw_text

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
spr_units = {
    Team.RED: {
        UnitType.UNIT: pygame.image.load("resources/sprites/units/Colonist.png"),
        UnitType.COLONIST: pygame.image.load("resources/sprites/units/Colonist.png"),
        UnitType.TROOPER: pygame.image.load("resources/sprites/units/Trooper.png"),
        UnitType.RANGER: pygame.image.load("resources/sprites/units/Ranger.png"),
        UnitType.GHOST: pygame.image.load("resources/sprites/units/Ghost.png"),
    }
}

spr_base_order_flags = get_nine_slice_sprites(pygame.image.load("resources/sprites/units/OrderFlags.png"), 8)
spr_order_flags = {
    MENU_CANCEL_ORDER: spr_base_order_flags[0],
    MENU_MOVE: spr_base_order_flags[1],
    MENU_RANGED_ATTACK: spr_base_order_flags[2],
    MENU_BUILD_UNIT: spr_base_order_flags[3]
}

spr_hp_flags = get_nine_slice_sprites(pygame.image.load("resources/sprites/units/HPFlags.png"), 8)


# Buildings
spr_buildings = {
    Team.RED: {
        BuildingType.BUILDING: pygame.image.load("resources/sprites/buildings/Base.png"),
        BuildingType.BASE: pygame.image.load("resources/sprites/buildings/Base.png")
    }
}


# Text
text_menu_option = {
    MENU_MOVE: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE], (0, 0, 0)),
    MENU_CANCEL_ORDER: draw_text(menu_option_strings[LANGUAGE][MENU_CANCEL_ORDER], (0, 0, 0)),
    MENU_RANGED_ATTACK: draw_text(menu_option_strings[LANGUAGE][MENU_RANGED_ATTACK], (0, 0, 0)),
    MENU_BUILD_UNIT: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_UNIT], (0, 0, 0))
}
text_unit_name = {}


def load_assets():
    palette_swapped_teams = [Team.BLUE]

    # Generate palette swaps for other teams
    for team in palette_swapped_teams:
        spr_cursor[team] = swap_palette(spr_cursor[Team.RED], unit_palette[team])
        spr_textbox[team] = swap_multiple_palette(spr_textbox[Team.RED], unit_palette[team])

        spr_units[team] = {}
        spr_buildings[team] = {}

        for unit_type in UnitType:
            spr_units[team][unit_type] = swap_palette(spr_units[Team.RED][unit_type], unit_palette[team])
        for building_type in BuildingType:
            spr_buildings[team][building_type] = swap_palette(spr_buildings[Team.RED][building_type], unit_palette[team])

    # Generate text surfaces for each unit type
    for unit_type in UnitType:
        text_unit_name[unit_type] = draw_text(unit_name_strings[LANGUAGE][unit_type], (0, 0, 0))
