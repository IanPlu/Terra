from queue import PriorityQueue, Queue

from terra.map.tiletype import TileType
from terra.piece.attribute import Attribute


# Utility methods for pathfinding around the map in various ways.
# This file owes its life to: https://www.redblobgames.com/pathfinding/a-star/introduction.html


# Pathfind a piece to the specified goal
def navigate(start, goal, map, piece=None, movement_type=None, blocked_coords=None):
    blocked = blocked_coords if not None else []
    if piece and not movement_type:
        movement_type = piece.attr(Attribute.MOVEMENT_TYPE)

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in map.get_valid_adjacent_tiles_for_movement_type(current[0], current[1], movement_type):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost

                priority = new_cost + piece.get_move_score(goal, next, blocked) if piece else new_cost

                # If there's an enemy on this tile, and we are susceptible to impedance, we can go no further. Stop here
                if piece and not piece.is_enemy_at_tile(next):
                    frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


# Generate all paths to a goal, as well as all distances to that goal.
def navigate_all(goal, map, movement_type):
    frontier = Queue()
    frontier.put(goal)

    # Track both distance and where we came from
    came_from = {goal: None}
    distance = {goal: 0}

    while not frontier.empty():
        current = frontier.get()

        for next in map.get_valid_adjacent_tiles_for_movement_type(current[0], current[1], movement_type):
            if next not in came_from:
                frontier.put(next)
                came_from[next] = current
                distance[next] = 1 + distance[current]

    return came_from, distance


# Given a goal and the 'came_from' map, reconstruct a single path to the goal
# If there's not actually a path to the destination, returns None.
def reconstruct_path(start, goal, came_from):
    current = goal
    path = []
    try:
        while current != start:
            path.append(current)
            current = came_from[current]
    except KeyError:
        return None

    path.append(start)
    path.reverse()
    return path


# TODO: Tighten this up-- it's not pathing correctly
def get_terraform_tiles(start, goal, map):
    tiles = []

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        neighbors = map.get_tiles_in_range(current[0], current[1], 1, 1)
        for next in neighbors:
            tile_cost = 6 if map.get_tile_type_at(next[0], next[1]) in [TileType.SEA, TileType.MOUNTAIN] else 1
            new_cost = cost_so_far[current] + tile_cost

            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost

                frontier.put(next, priority)
                came_from[next] = current

    path = reconstruct_path(start, goal, came_from)
    for tile_x, tile_y in path:
        if map.get_tile_type_at(tile_x, tile_y) in [TileType.SEA, TileType.MOUNTAIN]:
            tiles.append((tile_x, tile_y))

    return tiles


# Navigate and reconstruct the optimal path to the goal all in one.
def get_path_to_destination(start, goal, map, piece, blocked_coords=None):
    came_from, cost_so_far = navigate(start, goal, map, piece=piece, blocked_coords=blocked_coords)
    return reconstruct_path(start, goal, came_from)


