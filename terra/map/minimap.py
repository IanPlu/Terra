from pygame import Surface, SRCALPHA

from terra.map.maputils import load_map_from_file
from terra.piece.piecetype import PieceType
from terra.resources.assetloading import AssetType
from terra.resources.assets import team_color, clear_color, light_color, shadow_color, light_team_color, \
    spr_pieces, spr_tiles_mini
from terra.strings import get_string, formatted_strings, draw_text
from terra.team.team import Team


# Generate a surface containing a minimap of the passed in bitmap
# Optionally, render blips for pieces
def generate_minimap(bitmap, pieces=None):
    height = len(bitmap)
    width = len(bitmap[0])

    minimap = Surface((width * 4, height * 4), SRCALPHA, 32)

    for x in range(width):
        for y in range(height):
            minimap.blit(spr_tiles_mini[bitmap[y][x]], (x * 4, y * 4))

    # Generate team-colored blips on the map for each piece
    if pieces:
        for piece in pieces:
            data = piece.split(' ')
            team = Team[data[2]]
            x, y = int(data[0]), int(data[1])
            minimap.fill(team_color[team], (x * 4 + 1, y * 4 + 1, 2, 2))
            minimap.fill(clear_color[team], (x * 4 + 1, y * 4 + 3, 2, 1))

    return minimap


# Return a surface containing a preview of the map, with data about what kind of teams, pieces, and upgrades are present
def draw_map_preview(container_width, container_height, bitmap, pieces, teams):
    container = Surface((container_width, container_height), SRCALPHA, 32)

    translated_teams = {}
    piece_totals = {}
    # Determine the teams in the game
    for team in teams:
        data = team.split(' ')
        team = Team[data[0]]
        translated_teams[team] = int(data[1])
        piece_totals[team] = 0

    # Determine how many pieces each team has
    for piece in pieces:
        data = piece.split(' ')
        piece_totals[Team[data[2]]] += 1

    # Render a container for the whole thing
    container.fill(light_color, (0, 0, container_width, container_height))
    container.fill(shadow_color[Team.RED], (1, 1, container_width - 2, container_height - 3))

    # Render the minimap
    minimap = generate_minimap(bitmap, pieces)

    # Trim giant maps to fit in the window
    if minimap.get_width() > container_width - 8:
        minimap = minimap.subsurface((0, 0, container_width - 8, minimap.get_width()))
    if minimap.get_height() > container_height - 38:
        minimap = minimap.subsurface((0, 0, minimap.get_width(), container_height - 38))

    minimap_x_offset = (container_width - minimap.get_width()) / 2
    container.blit(minimap, (minimap_x_offset, 32))
    container.fill(clear_color[Team.RED], (minimap_x_offset, 32 + minimap.get_height(), minimap.get_width(), 2))

    # Render teams + piece counts
    xoffset = 0
    container.fill(light_team_color[Team.RED], (1, 1, container_width - 2, 21))
    container.fill(light_color, (1, 22, container_width - 2, 2))

    for team, resource_count in translated_teams.items():
        piece_count = piece_totals[team]
        container.blit(spr_pieces[team][PieceType.TROOPER].subsurface((0, 0, 24, 24)), (container_width - 24 + xoffset, 0))

        display_string = get_string(formatted_strings, "QUANTITY").format(piece_count)
        container.blit(draw_text(display_string, light_color, shadow_color[Team.RED]), (container_width - 16 + xoffset, 14))

        xoffset -= 24

    return container


# Return a surface containing a preview of the map, with data about what kind of teams, pieces, and upgrades are present
def draw_map_preview_from_file(container_width, container_height, mapname, asset_type=AssetType.MAP):
    bitmap, pieces, teams, upgrades, meta = load_map_from_file(mapname, asset_type=asset_type)
    return draw_map_preview(container_width, container_height, bitmap, pieces, teams)
