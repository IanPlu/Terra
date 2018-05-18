import pygame

from terra.economy.upgradetype import UpgradeType
from terra.effects.effecttype import EffectType
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.piece.attribute import Attribute
from terra.piece.piecetype import PieceType
from terra.resources.assetloading import AssetType, get_asset
from terra.settings import SETTINGS, Setting
from terra.team.team import Team
from terra.util.drawingutil import get_nine_slice_sprites, get_sprites_from_strip, \
    swap_palette, generate_palette_list, swap_multiple_palette


# Load a sound and properly set it up
def load_sound(resource_name):
    sound = pygame.mixer.Sound(get_asset(AssetType.SOUND, resource_name))
    sound.set_volume(SETTINGS.get(Setting.SFX_VOLUME) / 100)
    all_sounds.append(sound)
    return sound


pygame.mixer.init()


# General
unit_palette = {
    Team.RED: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Red-Palette.png"))),
    Team.BLUE: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Blue-Palette.png"))),
    Team.GREEN: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Green-Palette.png"))),
    Team.YELLOW: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Yellow-Palette.png"))),
    Team.NONE: generate_palette_list(pygame.image.load(get_asset(AssetType.SPRITE, "palettes/Neutral-Palette.png"))),
}

# UI
spr_game_icon = pygame.image.load(get_asset(AssetType.SPRITE, "ui/GameIcon.png"))

spr_title_text = pygame.image.load(get_asset(AssetType.SPRITE, "ui/TitleText.png"))
spr_main_menu_option_base = get_sprites_from_strip(pygame.image.load(
    get_asset(AssetType.SPRITE, "ui/MainMenuOption.png")), 24)
spr_main_menu_option = {
    Option.START: spr_main_menu_option_base[5],
    Option.NEW_GAME: spr_main_menu_option_base[0],
    Option.LOAD_GAME: spr_main_menu_option_base[6],
    Option.LEVEL_EDITOR: spr_main_menu_option_base[2],
    Option.SETTINGS: spr_main_menu_option_base[3],
    Option.QUIT: spr_main_menu_option_base[4],
    Option.LOCAL: spr_main_menu_option_base[0],
    Option.NETWORK: spr_main_menu_option_base[1],
    Option.HOST_GAME: spr_main_menu_option_base[7],
    Option.JOIN_GAME: spr_main_menu_option_base[8],
    Option.NEW_NETWORK_GAME: spr_main_menu_option_base[0],
    Option.LOAD_NETWORK_GAME: spr_main_menu_option_base[6],
    Option.NEW_MAP: spr_main_menu_option_base[2],
    Option.LOAD_MAP: spr_main_menu_option_base[6],
    Option.SAVE_SETTINGS: spr_main_menu_option_base[6],
    Option.START_BATTLE: spr_main_menu_option_base[0],
    Option.LEAVE_LOBBY: spr_main_menu_option_base[4],
    Option.AI_PERSONALITY: spr_main_menu_option_base[7],
    Option.ADD_HUMAN: spr_main_menu_option_base[5],
    Option.REMOVE_HUMAN: spr_main_menu_option_base[7],
    Option.TUTORIAL: spr_main_menu_option_base[5],
    Option.CAMPAIGN: spr_main_menu_option_base[0],
    Option.NEW_CAMPAIGN_GAME: spr_main_menu_option_base[0],
    Option.LOAD_CAMPAIGN_GAME: spr_main_menu_option_base[6],
}
spr_mission_completed = spr_main_menu_option_base[9]

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
spr_turn_thinking_indicator = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Turn_Thinking.png"))
}

spr_wait_icon = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Wait_Indicator.png"))
}

spr_contested_icon = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Caution.png"))
}

spr_order_options_base = get_sprites_from_strip(pygame.image.load(
    get_asset(AssetType.SPRITE, "ui/Order_MenuOption.png")), 24)
spr_order_options = {
    Team.RED: {
        Option.MENU_CANCEL_ORDER: spr_order_options_base[0],
        Option.MENU_MOVE: spr_order_options_base[1],
        Option.MENU_RANGED_ATTACK: spr_order_options_base[2],
        Option.MENU_BUILD_PIECE: spr_order_options_base[3],
        Option.MENU_PURCHASE_UPGRADE: spr_order_options_base[4],
        Option.MENU_SUBMIT_TURN: spr_order_options_base[5],
        Option.MENU_REVISE_TURN: spr_order_options_base[6],
        Option.MENU_SAVE_GAME: spr_order_options_base[7],
        Option.MENU_QUIT_BATTLE: spr_order_options_base[8],
        Option.MENU_SAVE_MAP: spr_order_options_base[9],
        Option.MENU_MINE_TILE: spr_order_options_base[11],
        Option.MENU_DEMOLISH_SELF: spr_order_options_base[12],
        Option.MENU_HEAL_SELF: spr_order_options_base[15],
        Option.MENU_FILL_WITH_CURRENT_TILE: spr_order_options_base[10],
        Option.MENU_DESTROY_ALL_PIECES: spr_order_options_base[12],
        Option.MENU_CONCEDE: spr_order_options_base[0],
        Option.MENU_MIRROR_X: spr_order_options_base[13],
        Option.MENU_MIRROR_Y: spr_order_options_base[14],
        Option.MENU_SWAP_ACTIVE_PLAYER: spr_order_options_base[16],
    }
}

spr_combat_icon = {
    Team.RED: spr_main_menu_option[Option.NEW_GAME]
}
spr_build_icon = {
    Team.RED: spr_order_options[Team.RED][Option.MENU_BUILD_PIECE]
}

spr_menu_option_item_background = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/MenuOption_PieceBackground.png"))
}

spr_piece_attribute_icons_base = get_sprites_from_strip(pygame.image.load(
    get_asset(AssetType.SPRITE, "ui/Piece_Attribute_Icons.png")), 12)
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
        UpgradeType.RESOURCE_PRODUCTION: spr_upgrade_icons_base[0],
        UpgradeType.BUILDING_ARMOR: spr_upgrade_icons_base[1],

        UpgradeType.COLONIST_ATTACK: spr_upgrade_icons_base[2],
        UpgradeType.COLONIST_MAX_HP: spr_upgrade_icons_base[3],
        UpgradeType.COLONIST_MINING: spr_upgrade_icons_base[4],
        UpgradeType.COLONIST_UNCONTESTABLE: spr_upgrade_icons_base[5],

        UpgradeType.TROOPER_ATTACK: spr_upgrade_icons_base[6],
        UpgradeType.TROOPER_ARMOR: spr_upgrade_icons_base[7],
        UpgradeType.TROOPER_REGEN: spr_upgrade_icons_base[8],
        UpgradeType.TROOPER_COST: spr_upgrade_icons_base[9],

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

        UpgradeType.GUARDIAN_ARMOR_SHARE: spr_upgrade_icons_base[21],
        UpgradeType.GUARDIAN_ARMOR: spr_upgrade_icons_base[22],
        UpgradeType.GUARDIAN_MEDIC: spr_upgrade_icons_base[23],

        UpgradeType.BOLTCASTER_UNCONTESTABLE: spr_upgrade_icons_base[24],
        UpgradeType.BOLTCASTER_RANGE: spr_upgrade_icons_base[25],
        UpgradeType.BOLTCASTER_AP_ROUNDS: spr_upgrade_icons_base[26],

        UpgradeType.BANSHEE_SABOTAGE: spr_upgrade_icons_base[27],
        UpgradeType.BANSHEE_STRIKEFORMATION: spr_upgrade_icons_base[28],
        UpgradeType.BANSHEE_LURK: spr_upgrade_icons_base[29],

        UpgradeType.RESEARCH_TITAN: spr_upgrade_icons_base[30],
        UpgradeType.RESEARCH_EARTHRENDER: spr_upgrade_icons_base[31],
        UpgradeType.RESEARCH_DEMON: spr_upgrade_icons_base[32],

        UpgradeType.TITAN_LIFESTEAL: spr_upgrade_icons_base[33],
        UpgradeType.TITAN_AURA_DAMAGE: spr_upgrade_icons_base[34],

        UpgradeType.EARTHRENDER_CHAIN: spr_upgrade_icons_base[35],
        UpgradeType.EARTHRENDER_DAMAGE: spr_upgrade_icons_base[36],

        UpgradeType.DEMON_CAN_BUILD: spr_upgrade_icons_base[37],
        UpgradeType.DEMON_BASE_ATTACK: spr_upgrade_icons_base[38],
    }
}

spr_target = {
    Team.RED: pygame.image.load(get_asset(AssetType.SPRITE, "ui/Target.png"))
}

# Tile
spr_tile_selectable = pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Selectable.png"))
spr_tiles = {
    TileType.SEA: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Sea.png")),
    TileType.GRASS: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Grass.png")),
    TileType.WOODS: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Woods.png")),
    TileType.RESOURCE: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Resource.png")),
    TileType.MOUNTAIN: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Mountain.png")),
    TileType.COAST: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Coast.png")),
    TileType.HILL: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Hill.png")),
    TileType.METEOR: pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Meteor.png")),
}

spr_tiles_mini = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Minimap_Tile.png")), 4)

spr_coast_detail = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_Sea_Border.png")), 24)

spr_grid = pygame.image.load(get_asset(AssetType.SPRITE, "tiles/Tile_None.png"))


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
        PieceType.TITAN: pygame.image.load(get_asset(AssetType.SPRITE, "units/Titan.png")),
        PieceType.EARTHRENDER: pygame.image.load(get_asset(AssetType.SPRITE, "units/Earthrender.png")),
        PieceType.DEMON: pygame.image.load(get_asset(AssetType.SPRITE, "units/Demon.png")),

        # Buildings
        PieceType.BASE: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Base.png")),
        PieceType.GENERATOR: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Generator.png")),
        PieceType.BARRACKS: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Barracks.png")),
        PieceType.TOWER: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Tower.png")),
        PieceType.TECHLAB: pygame.image.load(get_asset(AssetType.SPRITE, "buildings/Techlab.png")),
    }
}

spr_base_order_flags = get_sprites_from_strip(pygame.image.load(get_asset(AssetType.SPRITE, "ui/OrderFlags.png")), 8)
spr_order_flags = {
    Option.MENU_CANCEL_ORDER: spr_base_order_flags[0],
    Option.MENU_MOVE: spr_base_order_flags[1],
    Option.MENU_RANGED_ATTACK: spr_base_order_flags[2],
    Option.MENU_BUILD_PIECE: spr_base_order_flags[3],
    Option.MENU_PURCHASE_UPGRADE: spr_base_order_flags[3],
    Option.MENU_SUBMIT_TURN: spr_base_order_flags[1],
    Option.MENU_REVISE_TURN: spr_base_order_flags[0],
    Option.MENU_SAVE_GAME: spr_base_order_flags[3],
    Option.MENU_QUIT_BATTLE: spr_base_order_flags[0],
    Option.MENU_SAVE_MAP: spr_base_order_flags[3],
    Option.MENU_MINE_TILE: spr_base_order_flags[7],
    Option.MENU_DEMOLISH_SELF: spr_base_order_flags[8],
    Option.MENU_HEAL_SELF: spr_base_order_flags[9],
    Option.MENU_FILL_WITH_CURRENT_TILE: spr_base_order_flags[0],
    Option.MENU_DESTROY_ALL_PIECES: spr_base_order_flags[0],
    Option.MENU_CONCEDE: spr_base_order_flags[0],
    Option.MENU_MIRROR_X: spr_base_order_flags[0],
    Option.MENU_MIRROR_Y: spr_base_order_flags[0],
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
    EffectType.ALERT: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Alert.png")),
    EffectType.PIECE_DESTROYED: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Piece_Destroyed.png")),
    EffectType.NO_MONEY: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_No_Money.png")),
    EffectType.ORDER_BLOCKED: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Order_Blocked.png")),
    EffectType.ARMOR_GRANTED: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Armor_Granted.png")),
    EffectType.HP_HEALED: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_HP_Healed.png")),
    EffectType.DUPLICATE_UPGRADE: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Duplicate_Upgrade.png")),
    EffectType.DEATH_AOE: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Poison_AOE.png")),
    EffectType.MONEY_LOST: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Money_Lost.png")),
    EffectType.PIECE_CONFLICT: pygame.image.load(get_asset(AssetType.SPRITE, "effects/FX_Piece_Hit.png")),
}


# Colors
light_color = (248, 240, 211)
dark_color = (51, 46, 46)
darker_color = (13, 12, 12)

light_team_color = {
    Team.RED: (247, 126, 126),
    Team.BLUE: (114, 210, 239),
    Team.GREEN: (84, 158, 91),
    Team.YELLOW: (196, 178, 94),
    Team.NONE: (219, 218, 224),
}
team_color = {
    Team.RED: (230, 53, 53),
    Team.BLUE: (56, 154, 226),
    Team.GREEN: (33, 117, 62),
    Team.YELLOW: (156, 132, 62),
    Team.NONE: (185, 181, 196),
}
clear_color = {
    Team.RED: (46, 29, 29),
    Team.BLUE: (41, 56, 71),
    Team.GREEN: (26, 23, 10),
    Team.YELLOW: (41, 27, 10),
    Team.NONE: (45, 38, 51),
}
shadow_color = {
    Team.RED: (82, 51, 51),
    Team.BLUE: (67, 87, 107),
    Team.GREEN: (48, 43, 39),
    Team.YELLOW: (74, 46, 10),
    Team.NONE: (74, 63, 84),
}

# Audio
all_sounds = []
sfx_cursor_move = load_sound("Cursor_Move.wav")
sfx_cursor_select = load_sound("Cursor_Move2.wav")
sfx_cursor_cancel = load_sound("Cursor_Move3.wav")

sfx_turn_submitted = load_sound("Notification2.wav")
sfx_all_turns_submitted = load_sound("Notification.wav")

sfx_piece_hit = load_sound("Hit1.wav")
sfx_order_canceled = load_sound("Interrupt.wav")

sfx_ranged_attack = load_sound("Attack1.wav")
sfx_piece_conflict = load_sound("Combat.wav")
sfx_building_built = load_sound("Build1.wav")
sfx_unit_built = load_sound("Build2.wav")

# Fonts
font_pixelmix = pygame.font.Font(get_asset(AssetType.FONT, "pixelmix.ttf"), 8)


def load_assets():
    palette_swapped_teams = [Team.BLUE, Team.GREEN, Team.YELLOW, Team.NONE]

    # Generate palette swaps for other teams
    for team in palette_swapped_teams:
        spr_cursor[team] = swap_palette(spr_cursor[Team.RED], unit_palette[team])
        spr_textbox[team] = swap_multiple_palette(spr_textbox[Team.RED], unit_palette[team])
        spr_digit_icons[team] = swap_multiple_palette(spr_digit_icons[Team.RED], unit_palette[team])

        spr_phase_indicator[team] = swap_multiple_palette(spr_phase_indicator[Team.RED], unit_palette[team])
        spr_resource_icon[team] = swap_palette(spr_resource_icon[Team.RED], unit_palette[team])
        spr_resource_icon_small[team] = swap_palette(spr_resource_icon_small[Team.RED], unit_palette[team])

        spr_turn_submitted_indicator[team] = swap_palette(spr_turn_submitted_indicator[Team.RED], unit_palette[team])
        spr_turn_thinking_indicator[team] = swap_palette(spr_turn_thinking_indicator[Team.RED], unit_palette[team])

        spr_wait_icon[team] = swap_palette(spr_wait_icon[Team.RED], unit_palette[team])
        spr_contested_icon[team] = swap_palette(spr_contested_icon[Team.RED], unit_palette[team])
        spr_target[team] = swap_palette(spr_target[Team.RED], unit_palette[team])
        spr_menu_option_item_background[team] = swap_palette(spr_menu_option_item_background[Team.RED], unit_palette[team])

        spr_combat_icon[team] = swap_palette(spr_combat_icon[Team.RED], unit_palette[team])
        spr_build_icon[team] = swap_palette(spr_build_icon[Team.RED], unit_palette[team])

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
