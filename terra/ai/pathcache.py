from terra.ai.pathfinder import navigate_all
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.piece.attribute import Attribute
from terra.piece.movementtype import MovementType

cached_movement_types = [MovementType.GROUND, MovementType.HEAVY, MovementType.HOVER, MovementType.FLYING]
terraforming_affected_movement_types = [MovementType.GROUND, MovementType.HEAVY, MovementType.HOVER]


# Cache for AI pathfinding.
# Stores BFS results for enemies, broken down by movement types.
class PathCache(GameObject):
    def __init__(self, piece_manager, map_manager, team):
        super().__init__()

        self.piece_manager = piece_manager
        self.map_manager = map_manager
        self.team = team

        # Pathfinding map to a goal, from all start points
        # self.paths[MovementType][(x, y)] = came_from map
        self.came_froms = {}

        # Actual distances to a goal, from all start points
        # self.distances[MovementType][(x, y)] = distance map
        self.distances = {}

        for movement_type in cached_movement_types:
            self.came_froms[movement_type] = {}
            self.distances[movement_type] = {}

        self.generate_paths()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_TILE_MINED, self.handle_tile_modified)

    # When a tile is modified, throw out pathing for GROUND, HEAVY, and HOVER types. (FLYING is fine)
    def handle_tile_modified(self, event=None):
        for movement_type in terraforming_affected_movement_types:
            self.came_froms[movement_type] = {}
            self.distances[movement_type] = {}

    # Generate paths to all enemies and store them.
    # Additionally, generate paths to open resource tiles
    def generate_paths(self, event=None):
        pieces = self.piece_manager.get_all_pieces_for_team(self.team)

        # Targets include enemy pieces to start
        targets = [(piece.gx, piece.gy) for piece in self.piece_manager.get_all_enemy_pieces(self.team)]

        # Determine which movement types we need to path for
        movement_types = set([piece.attr(Attribute.MOVEMENT_TYPE) for piece in pieces])\
            .intersection(set(cached_movement_types))

        # For each movement type and enemy, path to the target
        for movement_type in movement_types:
            for target in targets:
                # Check if we already have a path to this target. If so, skip pathing and just use the cache
                existing_path = self.get_map(target, movement_type)
                if not existing_path:
                    self.cache_path(target, movement_type)

    # Return the 'came_from' map to the target, for the provided movement type.
    def get_map(self, target, movement_type):
        return self.came_froms.get(movement_type, {}).get(target, None)

    # Return the 'distance' map to the target, for the provided movement type.
    def get_distance(self, target, movement_type):
        return self.distances.get(movement_type, {}).get(target, None)

    # Return the start among starts with the shortest distance to the target
    def get_shortest_distance_to_target(self, target, starts, movement_type):
        shortest = 999
        min_start = starts[0]

        for start in starts:
            distances = self.get_distance(target, movement_type)
            if distances:
                distance = distances.get(start, 999)
            else:
                # Just use the manhattan distance (ignoring terrain)
                distance = abs(start[0] - target[0]) + abs(start[1] - target[1])

            if distance <= shortest:
                shortest = distance
                min_start = start

        return min_start

    # Pathfind to the target for all possible contiguous start points, and cache it in 'paths' and 'distances'
    def cache_path(self, target, movement_type):
        came_from, distance = navigate_all(target, self.map_manager, movement_type)

        self.came_froms[movement_type][target] = came_from
        self.distances[movement_type][target] = distance

        return came_from

    def render(self, game_screen, ui_screen):
        super().render(game_screen, ui_screen)
        # Render debug info
