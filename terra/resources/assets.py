import pygame
from terra.constants import Team
from terra.map.tiletype import TileType
from terra.piece.unit.unittype import UnitType
from terra.piece.building.buildingtype import BuildingType
from terra.effects.effecttype import EffectType
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
spr_phase_indicator = {
    Team.RED: [
        pygame.image.load("resources/sprites/ui/Phase_Icons0.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons1.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons2.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons3.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons4.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons5.png"),
        pygame.image.load("resources/sprites/ui/Phase_Icons6.png")
    ]
}

spr_turn_submitted_indicator = {
    Team.RED: pygame.image.load("resources/sprites/ui/Turn_Submitted_Icon.png")
}
spr_turn_not_submitted_indicator = {
    Team.RED: pygame.image.load("resources/sprites/ui/Turn_Not_Submitted_Icon.png")
}

# Tile
spr_tile_selectable = pygame.image.load("resources/sprites/tiles/Tile_Selectable.png")
spr_tiles = {
    TileType.NONE: [pygame.image.load("resources/sprites/tiles/Tile_None.png")],
    TileType.SEA: get_sprites_from_strip(pygame.image.load("resources/sprites/tiles/Tile_Sea.png"), 24),
    TileType.GRASS: [pygame.image.load("resources/sprites/tiles/Tile_Grass.png")],
    TileType.WOODS: [pygame.image.load("resources/sprites/tiles/Tile_Woods.png")],
    TileType.RESOURCE: [pygame.image.load("resources/sprites/tiles/Tile_Resource.png")]
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
    MENU_BUILD_UNIT: spr_base_order_flags[3],
    MENU_BUILD_CARBON_GENERATOR: spr_base_order_flags[4],
    MENU_BUILD_MINERAL_GENERATOR: spr_base_order_flags[5],
    MENU_BUILD_GAS_GENERATOR: spr_base_order_flags[6],
    MENU_BUILD_BARRACKS: spr_base_order_flags[3],
}

spr_digit_icons = {
    Team.RED: get_sprites_from_strip(pygame.image.load("resources/sprites/ui/DigitIcons.png"), 8)
}

spr_resource_icon_carbon = {
    Team.RED: pygame.image.load("resources/sprites/ui/ResourceIcon_Carbon.png")
}
spr_resource_icon_minerals = {
    Team.RED: pygame.image.load("resources/sprites/ui/ResourceIcon_Minerals.png")
}
spr_resource_icon_gas = {
    Team.RED: pygame.image.load("resources/sprites/ui/ResourceIcon_Gas.png")
}


# Buildings
spr_buildings = {
    Team.RED: {
        BuildingType.BUILDING: pygame.image.load("resources/sprites/buildings/Base.png"),
        BuildingType.BASE: pygame.image.load("resources/sprites/buildings/Base.png"),
        BuildingType.CARBON_GENERATOR: pygame.image.load("resources/sprites/buildings/CarbonGenerator.png"),
        BuildingType.MINERAL_GENERATOR: pygame.image.load("resources/sprites/buildings/MineralGenerator.png"),
        BuildingType.GAS_GENERATOR: pygame.image.load("resources/sprites/buildings/GasGenerator.png"),
        BuildingType.BARRACKS: pygame.image.load("resources/sprites/buildings/Barracks.png"),
    }
}

# Effects
spr_effects = {
    EffectType.ALERT: get_sprites_from_strip(pygame.image.load("resources/sprites/effects/FX_Alert.png"), 24),
    EffectType.PIECE_DESTROYED: get_sprites_from_strip(pygame.image.load("resources/sprites/effects/FX_Piece_Destroyed.png"), 24),
    EffectType.NO_MONEY: get_sprites_from_strip(pygame.image.load("resources/sprites/effects/FX_No_Money.png"), 24)
}


# Colors
light_color = (248, 240, 211)
clear_color = {
    Team.RED: (46, 29, 29),
    Team.BLUE: (41, 56, 71)
}
shadow_color = {
    Team.RED: (82, 51, 51),
    Team.BLUE: (67, 87, 107)
}


# Text
text_menu_option = {
    MENU_MOVE: draw_text(menu_option_strings[LANGUAGE][MENU_MOVE], (0, 0, 0)),
    MENU_CANCEL_ORDER: draw_text(menu_option_strings[LANGUAGE][MENU_CANCEL_ORDER], (0, 0, 0)),
    MENU_RANGED_ATTACK: draw_text(menu_option_strings[LANGUAGE][MENU_RANGED_ATTACK], (0, 0, 0)),
    MENU_BUILD_UNIT: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_UNIT], (0, 0, 0)),
    MENU_BUILD_CARBON_GENERATOR: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_CARBON_GENERATOR], (0, 0, 0)),
    MENU_BUILD_MINERAL_GENERATOR: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_MINERAL_GENERATOR], (0, 0, 0)),
    MENU_BUILD_GAS_GENERATOR: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_GAS_GENERATOR], (0, 0, 0)),
    MENU_BUILD_BARRACKS: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_BARRACKS], (0, 0, 0))
}

text_notifications = {
    EffectType.ALERT: draw_text(notification_strings[LANGUAGE][EffectType.ALERT], (0, 0, 0)),
    EffectType.NO_MONEY: draw_text(notification_strings[LANGUAGE][EffectType.NO_MONEY], (0, 0, 0)),
}

text_unit_name = {}

phase_text = {}
for team in Team:
    phase_text[team] = {}
    for _, phase in BattlePhase.__members__.items():
        phase_text[team][phase] = draw_text(phase_strings[LANGUAGE][phase], light_color, shadow_color[team])


def load_assets():
    palette_swapped_teams = [Team.BLUE]

    # Generate palette swaps for other teams
    for team in palette_swapped_teams:
        spr_cursor[team] = swap_palette(spr_cursor[Team.RED], unit_palette[team])
        spr_textbox[team] = swap_multiple_palette(spr_textbox[Team.RED], unit_palette[team])
        spr_digit_icons[team] = swap_multiple_palette(spr_digit_icons[Team.RED], unit_palette[team])

        spr_phase_indicator[team] = swap_multiple_palette(spr_phase_indicator[Team.RED], unit_palette[team])
        spr_resource_icon_carbon[team] = swap_palette(spr_resource_icon_carbon[Team.RED], unit_palette[team])
        spr_resource_icon_minerals[team] = swap_palette(spr_resource_icon_minerals[Team.RED], unit_palette[team])
        spr_resource_icon_gas[team] = swap_palette(spr_resource_icon_gas[Team.RED], unit_palette[team])

        spr_turn_submitted_indicator[team] = swap_palette(spr_turn_submitted_indicator[Team.RED], unit_palette[team])
        spr_turn_not_submitted_indicator[team] = swap_palette(spr_turn_not_submitted_indicator[Team.RED], unit_palette[team])

        spr_units[team] = {}
        spr_buildings[team] = {}

        for unit_type in UnitType:
            spr_units[team][unit_type] = swap_palette(spr_units[Team.RED][unit_type], unit_palette[team])
        for building_type in BuildingType:
            spr_buildings[team][building_type] = swap_palette(spr_buildings[Team.RED][building_type], unit_palette[team])

    # Generate text surfaces for each unit and building type
    for unit_type in UnitType:
        text_unit_name[unit_type] = draw_text(unit_name_strings[LANGUAGE][unit_type], (0, 0, 0))
