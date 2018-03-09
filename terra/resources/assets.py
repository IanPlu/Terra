import sys
from enum import Enum
from os import path

import pygame

from terra.economy.upgrades import UpgradeType
from terra.effects.effecttype import EffectType
from terra.event import MENU_MOVE, MENU_CANCEL_ORDER, MENU_RANGED_ATTACK, MENU_BUILD_PIECE, \
    MENU_PURCHASE_UPGRADE, MENU_SUBMIT_TURN, MENU_SAVE_GAME, MENU_QUIT_BATTLE, MENU_SAVE_MAP, \
    MENU_RAISE_TILE, MENU_LOWER_TILE, MENU_REVISE_TURN
from terra.map.tiletype import TileType
from terra.piece.pieceattributes import Attribute
from terra.piece.piecetype import PieceType
from terra.settings import SFX_VOLUME
from terra.team import Team
from terra.util.drawingutil import get_nine_slice_sprites, get_sprites_from_strip, \
    swap_palette, generate_palette_list, swap_multiple_palette, get_indexed_sprites_from_strip


# External assets are divided into subdirectories by their type
class AssetType(Enum):
    SPRITE = "resources/sprites/"
    SOUND = "resources/sfx/"
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


# Load a sound and properly set it up
def load_sound(resource_name):
    sound = pygame.mixer.Sound(get_asset(AssetType.SOUND, resource_name))
    sound.set_volume(SFX_VOLUME)
    all_sounds.append(sound)
    return sound


pygame.mixer.init()


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
    Team.RED: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Phase_Icons.png")), 24)
}

spr_turn_submitted_indicator = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Turn_Submitted.png"))
}

spr_order_options_base = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Order_MenuOption.png")), 24)
spr_order_options = {
    Team.RED: {
        MENU_CANCEL_ORDER: spr_order_options_base[0],
        MENU_MOVE: spr_order_options_base[1],
        MENU_RANGED_ATTACK: spr_order_options_base[2],
        MENU_BUILD_PIECE: spr_order_options_base[3],
        MENU_PURCHASE_UPGRADE: spr_order_options_base[4],
        MENU_SUBMIT_TURN: spr_order_options_base[5],
        MENU_REVISE_TURN: spr_order_options_base[6],
        MENU_SAVE_GAME: spr_order_options_base[7],
        MENU_QUIT_BATTLE: spr_order_options_base[8],
        MENU_SAVE_MAP: spr_order_options_base[9],
        MENU_RAISE_TILE: spr_order_options_base[10],
        MENU_LOWER_TILE: spr_order_options_base[11],
    }
}

spr_piece_attribute_icons_base = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Piece_Attribute_Icons.png")), 12)
spr_piece_attribute_icons = {
    Team.RED: {
        Attribute.ARCHETYPE: spr_piece_attribute_icons_base[0],
        Attribute.MAX_HP: spr_piece_attribute_icons_base[1],
        Attribute.ATTACK: spr_piece_attribute_icons_base[2],
        Attribute.ARMOR: spr_piece_attribute_icons_base[3],
        Attribute.MIN_RANGE: spr_piece_attribute_icons_base[4],
        Attribute.MAX_RANGE: spr_piece_attribute_icons_base[5],
        Attribute.MOVEMENT_TYPE: spr_piece_attribute_icons_base[6],
        Attribute.MOVEMENT_RANGE: spr_piece_attribute_icons_base[7],
    }
}

spr_upgrade_icons_base = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/Upgrade_Icons.png")), 24)
spr_upgrade_icons = {
    Team.RED: {
        UpgradeType.RESOURCE_PRODUCTION_1: spr_upgrade_icons_base[0],
        UpgradeType.RESOURCE_PRODUCTION_2: spr_upgrade_icons_base[1],

        UpgradeType.COLONIST_ATTACK: spr_upgrade_icons_base[2],
        UpgradeType.COLONIST_MAX_HP: spr_upgrade_icons_base[3],
        UpgradeType.COLONIST_TERRAFORMING: spr_upgrade_icons_base[4],
        UpgradeType.COLONIST_UNCONTESTABLE: spr_upgrade_icons_base[5],

        UpgradeType.TROOPER_ATTACK: spr_upgrade_icons_base[6],
        UpgradeType.TROOPER_ARMOR: spr_upgrade_icons_base[7],
        UpgradeType.TROOPER_REGEN: spr_upgrade_icons_base[8],
        UpgradeType.TROOPER_ENTRENCHMENT: spr_upgrade_icons_base[9],

        UpgradeType.RANGER_ATTACK: spr_upgrade_icons_base[10],
        UpgradeType.RANGER_DISTANCE: spr_upgrade_icons_base[11],
        UpgradeType.RANGER_MOVEMENT: spr_upgrade_icons_base[12],
        UpgradeType.RANGER_UNCONTESTABLE: spr_upgrade_icons_base[13],

        UpgradeType.GHOST_MOVEMENT: spr_upgrade_icons_base[14],
        UpgradeType.GHOST_ATTACK: spr_upgrade_icons_base[15],
        UpgradeType.GHOST_ANTI_COLONIST: spr_upgrade_icons_base[16],
        UpgradeType.GHOST_STEAL: spr_upgrade_icons_base[17],

        UpgradeType.RESEARCH_GUARDIAN: spr_upgrade_icons_base[18],
        UpgradeType.RESEARCH_BOLTCASTER: spr_upgrade_icons_base[19],
        UpgradeType.RESEARCH_BANSHEE: spr_upgrade_icons_base[20],

        UpgradeType.GUARDIAN_ENTRENCHMENT: spr_upgrade_icons_base[21],
        UpgradeType.GUARDIAN_ARMOR: spr_upgrade_icons_base[22],
        UpgradeType.GUARDIAN_MEDIC: spr_upgrade_icons_base[23],

        UpgradeType.BOLTCASTER_UNCONTESTABLE: spr_upgrade_icons_base[24],
        UpgradeType.BOLTCASTER_RANGE: spr_upgrade_icons_base[25],
        UpgradeType.BOLTCASTER_AP_ROUNDS: spr_upgrade_icons_base[26],

        UpgradeType.BANSHEE_SABOTAGE: spr_upgrade_icons_base[27],
        UpgradeType.BANSHEE_STRIKEFORMATION: spr_upgrade_icons_base[28],
        UpgradeType.BANSHEE_LURK: spr_upgrade_icons_base[29],
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
    TileType.MOUNTAIN: [pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Mountain.png"))],
    TileType.COAST: get_indexed_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Coast.png")), 24, 24),
    TileType.HILL: [pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Hill.png"))],
}

spr_coast_detail = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Sea_Border.png")), 24)


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
        PieceType.GENERATOR: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Generator.png")),
        PieceType.BARRACKS: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Barracks.png")),
        PieceType.TOWER: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Tower.png")),
        # PieceType.WAYSTATION: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Waystation.png")),
        PieceType.TECHLAB: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Techlab.png")),
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
    MENU_REVISE_TURN: spr_base_order_flags[0],
    MENU_SAVE_GAME: spr_base_order_flags[3],
    MENU_QUIT_BATTLE: spr_base_order_flags[0],
    MENU_SAVE_MAP: spr_base_order_flags[3],
    MENU_RAISE_TILE: spr_base_order_flags[7],
    MENU_LOWER_TILE: spr_base_order_flags[7],

}

spr_digit_icons = {
    Team.RED: get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/DigitIcons.png")), 8)
}

spr_resource_icon = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/ResourceIcon.png"))
}

spr_resource_icon_small = {
    Team.RED: spr_base_order_flags[5]
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
    EffectType.HP_HEALED: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_HP_Healed.png")), 24),
    EffectType.DUPLICATE_UPGRADE: get_sprites_from_strip(
        pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Duplicate_Upgrade.png")), 24),
}


# Colors
light_color = (248, 240, 211)
dark_color = (82, 51, 51)
darker_color = (46, 29, 29)
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

# Audio
all_sounds = []
sfx_cursor_move = load_sound("cursor/sfx_cursor_move.wav")
sfx_cursor_select = load_sound("cursor/sfx_cursor_select.wav")
sfx_cursor_cancel = load_sound("cursor/sfx_cursor_cancel.wav")


def load_assets():
    palette_swapped_teams = [Team.BLUE]

    # Generate palette swaps for other teams
    for team in palette_swapped_teams:
        spr_cursor[team] = swap_palette(spr_cursor[Team.RED], unit_palette[team])
        spr_textbox[team] = swap_multiple_palette(spr_textbox[Team.RED], unit_palette[team])
        spr_digit_icons[team] = swap_multiple_palette(spr_digit_icons[Team.RED], unit_palette[team])

        spr_phase_indicator[team] = swap_multiple_palette(spr_phase_indicator[Team.RED], unit_palette[team])
        spr_resource_icon[team] = swap_palette(spr_resource_icon[Team.RED], unit_palette[team])
        spr_resource_icon_small[team] = swap_palette(spr_resource_icon_small[Team.RED], unit_palette[team])

        spr_turn_submitted_indicator[team] = swap_palette(spr_turn_submitted_indicator[Team.RED],
                                                          unit_palette[team])
        spr_target[team] = swap_palette(spr_target[Team.RED], unit_palette[team])

        spr_pieces[team] = {}
        for piece_type in PieceType:
            spr_pieces[team][piece_type] = swap_palette(spr_pieces[Team.RED][piece_type], unit_palette[team])

        spr_upgrade_icons[team] = {}
        for upgrade_type in UpgradeType:
            spr_upgrade_icons[team][upgrade_type] = swap_palette(spr_upgrade_icons[Team.RED][upgrade_type], unit_palette[team])

        spr_order_options[team] = {}
        for option in spr_order_options[Team.RED]:
            spr_order_options[team][option] = swap_palette(spr_order_options[Team.RED][option], unit_palette[team])

        spr_piece_attribute_icons[team] = {}
        for icon in spr_piece_attribute_icons[Team.RED]:
            spr_piece_attribute_icons[team][icon] = swap_palette(spr_piece_attribute_icons[Team.RED][icon], unit_palette[team])
