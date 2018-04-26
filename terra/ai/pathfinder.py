from queue import PriorityQueue
from terra.piece.attribute import Attribute


# Pathfind a piece to the specified goal
# https://www.redblobgames.com/pathfinding/a-star/introduction.html
def navigate(start, goal, map, piece, blocked_coords=None):
    blocked = blocked_coords if not None else []

    frontier = PriorityQueue()
    frontier.put(start, 0)

    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in map.get_valid_adjacent_tiles_for_movement_type(current[0], current[1], piece.attr(Attribute.MOVEMENT_TYPE)):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost

                priority = new_cost + piece.get_move_score(goal, next, blocked)

                # If there's an enemy on this tile, and we are susceptible to impedance, we can go no further. Stop here
                if not piece.is_enemy_at_tile(next):
                    frontier.put(next, priority)
                came_from[next] = current

    return came_from, cost_so_far


# Reconstruct the optimal path from the search
# Once we have the path, step through it <movement_range> times to get where along the path we should move to
# Note: Sometimes there isn't a path to the destination, and this will return None
def get_path_to_destination(start, goal, map, piece, blocked_coords=None):
    came_from, cost_so_far = navigate(start, goal, map, piece, blocked_coords)

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


