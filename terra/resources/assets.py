import sys
from enum import Enum
from os import path

import pygame

from terra.battlephase import BattlePhase
from terra.economy.upgrades import UpgradeType
from terra.effects.effecttype import EffectType
from terra.event import MENU_MOVE, MENU_CANCEL_ORDER, MENU_RANGED_ATTACK, MENU_BUILD_PIECE, \
    MENU_PURCHASE_UPGRADE, MENU_SUBMIT_TURN, MENU_SAVE_GAME, MENU_QUIT_BATTLE, MENU_SAVE_MAP
from terra.mainmenu.option import Option
from terra.map.tiletype import TileType
from terra.piece.piecetype import PieceType
from terra.settings import LANGUAGE
from terra.strings import menu_option_strings, phase_strings, piece_name_strings, upgrade_name_strings, \
    notification_strings, main_menu_strings
from terra.team import Team
from terra.util.drawingutil import get_nine_slice_sprites, get_sprites_from_strip, \
    swap_palette, generate_palette_list, swap_multiple_palette, draw_text


# External assets are divided into subdirectories by their type
class AssetType(Enum):
    SPRITE = "resources/sprites/"
    MAP = "resources/maps/"
    LOG = "logs/"


# Resources might be located somewhere strange depending on how the application is packaged.
# Locate the directory we ask for regardless of whether we're an executable or not.
def get_base_path(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen / packaged into an executable
        datadir = path.dirname(sys.executable)
    else:
        # The application is not frozen (debugging or otherwise not packaged)
        datadir = path.dirname(__file__)

    return path.join(datadir, filename)


# Return a properly formatted path to the specified resource
def get_asset(asset_type, resource_name):
    return get_base_path(path.abspath(path.join(asset_type.value, resource_name)))


# General
unit_palette = {
    Team.RED: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Red-Palette.png"))),
    Team.BLUE: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Blue-Palette.png"))),
}

# UI
spr_cursor = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Cursor.png"))
}
spr_textbox = {
    Team.RED: get_nine_slice_sprites(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Textbox_9slice.png")), 8)
}
spr_phase_indicator = {
    Team.RED: [
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Start_Turn.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Orders.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Execute_Move.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Execute_Build.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Execute_Combat.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Execute_Ranged.png")),
        pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icon_Execute_Special.png"))
    ]
}

spr_turn_submitted_indicator = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Turn_Submitted.png"))
}

spr_upgrade_icons_base = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Upgrade_Icons.png")), 24)
spr_upgrade_icons = {
    Team.RED: {
        UpgradeType.RESOURCE_PRODUCTION_1: spr_upgrade_icons_base[0],
        UpgradeType.RESOURCE_PRODUCTION_2: spr_upgrade_icons_base[1],

        UpgradeType.COLONIST_ATTACK: spr_upgrade_icons_base[2],
        UpgradeType.COLONIST_MAX_HP: spr_upgrade_icons_base[3],
        # UpgradeType.COLONIST_TERRAFORMING: spr_upgrade_icons_base[4],
        # UpgradeType.COLONIST_UNCONTESTABLE: spr_upgrade_icons_base[5],

        UpgradeType.TROOPER_ATTACK: spr_upgrade_icons_base[6],
        UpgradeType.TROOPER_ARMOR: spr_upgrade_icons_base[7],
        # UpgradeType.TROOPER_REGEN: spr_upgrade_icons_base[8],
        # UpgradeType.TROOPER_ENTRENCHMENT: spr_upgrade_icons_base[9],

        UpgradeType.RANGER_ATTACK: spr_upgrade_icons_base[10],
        UpgradeType.RANGER_DISTANCE: spr_upgrade_icons_base[11],
        UpgradeType.RANGER_MOVEMENT: spr_upgrade_icons_base[12],
        # UpgradeType.RANGER_UNCONTESTABLE: spr_upgrade_icons_base[13],

        UpgradeType.GHOST_MOVEMENT: spr_upgrade_icons_base[14],
        # UpgradeType.GHOST_STEALTH: spr_upgrade_icons_base[15],
        UpgradeType.GHOST_ANTI_COLONIST: spr_upgrade_icons_base[16],
        # UpgradeType.GHOST_ANTI_PARTING_SHOTS: spr_upgrade_icons_base[17],

        UpgradeType.RESEARCH_GUARDIAN: spr_upgrade_icons_base[18],
        UpgradeType.RESEARCH_BOLTCASTER: spr_upgrade_icons_base[19],
        UpgradeType.RESEARCH_BANSHEE: spr_upgrade_icons_base[20],
    }
}

spr_target = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Target.png"))
}

# Tile
spr_tile_selectable = pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Selectable.png"))
spr_tiles = {
    TileType.SEA: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Sea.png")), 24),
    TileType.GRASS: [pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Grass.png"))],
    TileType.WOODS: [pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Woods.png"))],
    TileType.RESOURCE: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Resource.png")), 24),
    TileType.HILL: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Hill.png")), 24)
}
# noinspection PyUnresolvedReferences
spr_coast_detail = {
    0: None,
    1: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail1.png")),
    2: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail2.png")),
    3: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail3.png")),
    4: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail4.png")),
    5: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail5.png")),
    6: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail6.png")),
    7: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail7.png")),
    8: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail8.png")),
    9: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail9.png")),
    10: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail10.png")),
    11: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail11.png")),
    12: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail12.png")),
    13: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail13.png")),
    14: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail14.png")),
    15: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/coasts/Tile_CoastDetail15.png")),
}


# Pieces
spr_pieces = {
    Team.RED: {
        PieceType.DEFAULT: pygame.image.load(get_asset(AssetType.SPRITE, "units/Colonist.png")),

        # Tier 1 Units
        PieceType.COLONIST: pygame.image.load(get_asset(AssetType.SPRITE, "units/Colonist.png")),
        PieceType.TROOPER: pygame.image.load(get_asset(AssetType.SPRITE, "units/Trooper.png")),
        PieceType.RANGER: pygame.image.load(get_asset(AssetType.SPRITE, "units/Ranger.png")),
        PieceType.GHOST: pygame.image.load(get_asset(AssetType.SPRITE, "units/Ghost.png")),

        # Tier 2 Units
        PieceType.GUARDIAN: pygame.image.load(get_asset(AssetType.SPRITE, "units/Guardian.png")),
        PieceType.BOLTCASTER: pygame.image.load(get_asset(AssetType.SPRITE, "units/Boltcaster.png")),
        PieceType.BANSHEE: pygame.image.load(get_asset(AssetType.SPRITE, "units/Banshee.png")),

        # Tier 3 Units
        # PieceType.TITAN: pygame.image.load(get_asset(AssetType.SPRITE, "units/Titan.png")),
        # PieceType.EARTHRENDER: pygame.image.load(get_asset(AssetType.SPRITE, "units/Earthrender.png")),
        # PieceType.DEMON: pygame.image.load(get_asset(AssetType.SPRITE, "units/Demon.png")),

        # Buildings
        PieceType.BASE: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Base.png")),
        PieceType.CARBON_GENERATOR: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/CarbonGenerator.png")),
        PieceType.MINERAL_GENERATOR: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/MineralGenerator.png")),
        PieceType.GAS_GENERATOR: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/GasGenerator.png")),
        PieceType.BARRACKS: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Barracks.png")),
        # PieceType.TOWER: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Tower.png")),
        # PieceType.WAYSTATION: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Waystation.png")),
        # PieceType.TECHLAB: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/TechLab.png")),
    }
}

spr_base_order_flags = get_nine_slice_sprites(pygame.image.load(get_asset(AssetType.SPRITE, "units/OrderFlags.png")), 8)
spr_order_flags = {
    MENU_CANCEL_ORDER: spr_base_order_flags[0],
    MENU_MOVE: spr_base_order_flags[1],
    MENU_RANGED_ATTACK: spr_base_order_flags[2],
    MENU_BUILD_PIECE: spr_base_order_flags[3],
    MENU_PURCHASE_UPGRADE: spr_base_order_flags[3],
    MENU_SUBMIT_TURN: spr_base_order_flags[1],
    MENU_SAVE_GAME: spr_base_order_flags[3],
    MENU_QUIT_BATTLE: spr_base_order_flags[0],
    MENU_SAVE_MAP: spr_base_order_flags[3],
}

spr_digit_icons = {
    Team.RED: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/DigitIcons.png")), 8)
}

spr_resource_icon_carbon = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/ResourceIcon_Carbon.png"))
}
spr_resource_icon_minerals = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/ResourceIcon_Minerals.png"))
}
spr_resource_icon_gas = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/ResourceIcon_Gas.png"))
}

spr_resource_icon_carbon_small = {
    Team.RED: spr_base_order_flags[4]
}
spr_resource_icon_minerals_small = {
    Team.RED: spr_base_order_flags[5]
}
spr_resource_icon_gas_small = {
    Team.RED: spr_base_order_flags[6]
}

# Effects
spr_effects = {
    EffectType.ALERT: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Alert.png")), 24),
    EffectType.PIECE_DESTROYED: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Piece_Destroyed.png")), 24),
    EffectType.NO_MONEY: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_No_Money.png")), 24),
    EffectType.ORDER_BLOCKED: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Order_Blocked.png")), 24),
    EffectType.ARMOR_GRANTED: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Armor_Granted.png")), 24),
}


# Colors
light_color = (248, 240, 211)
light_team_color = {
    Team.RED: (247, 126, 126),
    Team.BLUE: (114, 210, 239)
}
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
    MENU_BUILD_PIECE: draw_text(menu_option_strings[LANGUAGE][MENU_BUILD_PIECE], (0, 0, 0)),
    MENU_PURCHASE_UPGRADE: draw_text(menu_option_strings[LANGUAGE][MENU_PURCHASE_UPGRADE], (0, 0, 0)),
    MENU_SUBMIT_TURN: draw_text(menu_option_strings[LANGUAGE][MENU_SUBMIT_TURN], (0, 0, 0)),
    MENU_SAVE_GAME: draw_text(menu_option_strings[LANGUAGE][MENU_SAVE_GAME], (0, 0, 0)),
    MENU_QUIT_BATTLE: draw_text(menu_option_strings[LANGUAGE][MENU_QUIT_BATTLE], (0, 0, 0)),
    MENU_SAVE_MAP: draw_text(menu_option_strings[LANGUAGE][MENU_SAVE_MAP], (0, 0, 0)),
}

text_notifications = {
    EffectType.ALERT: draw_text(notification_strings[LANGUAGE][EffectType.ALERT], (0, 0, 0)),
    EffectType.NO_MONEY: draw_text(notification_strings[LANGUAGE][EffectType.NO_MONEY], (0, 0, 0)),
}

text_piece_name = {}
text_upgrade_name = {}

phase_text = {}
for team in Team:
    phase_text[team] = {}
    for _, phase in BattlePhase.__members__.items():
        phase_text[team][phase] = draw_text(phase_strings[LANGUAGE][phase], light_color, shadow_color[team])

text_main_menu = {}
for _, option in Option.__members__.items():
    text_main_menu[option] = draw_text(main_menu_strings[LANGUAGE][option], light_color, shadow_color[Team.RED])


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

        spr_resource_icon_carbon_small[team] = swap_palette(spr_resource_icon_carbon_small[Team.RED], unit_palette[team])
        spr_resource_icon_minerals_small[team] = swap_palette(spr_resource_icon_minerals_small[Team.RED], unit_palette[team])
        spr_resource_icon_gas_small[team] = swap_palette(spr_resource_icon_gas_small[Team.RED], unit_palette[team])

        spr_turn_submitted_indicator[team] = swap_palette(spr_turn_submitted_indicator[Team.RED],
                                                          unit_palette[team])
        spr_target[team] = swap_palette(spr_target[Team.RED], unit_palette[team])

        spr_pieces[team] = {}
        for piece_type in PieceType:
            spr_pieces[team][piece_type] = swap_palette(spr_pieces[Team.RED][piece_type], unit_palette[team])

        spr_upgrade_icons[team] = {}
        for upgrade_type in UpgradeType:
            spr_upgrade_icons[team][upgrade_type] = swap_palette(spr_upgrade_icons[Team.RED][upgrade_type], unit_palette[team])

    # Generate text surfaces for each unit and building type
    for piece_type in PieceType:
        text_piece_name[piece_type] = draw_text(piece_name_strings[LANGUAGE][piece_type], (0, 0, 0))

    # Generate text surfaces for each upgrade type
    for upgrade_type in UpgradeType:
        text_upgrade_name[upgrade_type] = draw_text(upgrade_name_strings[LANGUAGE][upgrade_type], (0, 0, 0))
