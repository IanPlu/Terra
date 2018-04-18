from pygame import USEREVENT
from pygame.event import Event

from terra.ai.task import Task, TaskType, Assignment
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.session import Manager
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.piece.attribute import Attribute
from terra.piece.piecetype import PieceType


# An AI player, in charge of giving orders to a team.
# When the Orders phase begins, it'll provide orders to its team.
class AIPlayer(GameObject):
    def __init__(self, team):
        super().__init__()

        self.team = team

        # Aliases for commonly accessed data
        self.my_pieces = None
        self.enemy_pieces = None
        self.map = None

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.START_PHASE_ORDERS, self.handle_orders_phase)

    # Rebuild the AI's understanding of the board, map, and pieces
    def parse_board_state(self):
        self.my_pieces = self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team)
        self.enemy_pieces = self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team)
        self.map = self.get_manager(Manager.MAP)

    # Generate a list of tasks that we'd like to accomplish this turn
    def generate_tasks(self):
        piece_manager = self.get_manager(Manager.PIECE)
        tasks = []

        # Get a list of open resource tiles
        harvestable_coords = [coord for coord in self.map.find_tiles_by_type(TileType.RESOURCE)
                              if len(piece_manager.get_pieces_at(coord[0], coord[1], PieceType.GENERATOR)) == 0]
        for coord in harvestable_coords:
            tasks.append(self.create_harvest_task(coord))

        # TODO: Sort tasks by priority

        return tasks

    def create_harvest_task(self, coord):
        return Task(self.team, TaskType.HARVEST_RESOURCE, coord[0], coord[1])

    # Create assignments for each task
    # TODO: Add weighting factors, run this multiple times to get different 'best' turns
    def assign_tasks(self, tasks):
        assignments = []
        for task in tasks:
            possible_assignments = {}
            eligible_pieces = task.get_eligible_pieces_for_task(self.get_manager(Manager.PIECE))
            # Score each piece, make an assignment
            for piece in eligible_pieces:
                possible_assignments[piece] = task.score_piece_for_task(piece, self.get_manager(Manager.MAP))

            # Add the best possible assignment to the master list
            if len(possible_assignments) > 0:
                piece = max(possible_assignments, key=lambda i: possible_assignments[i])
                assignments.append(Assignment(piece, task, possible_assignments[piece]))

        # Sort assignments by their score (lowest scores first)
        assignments.sort(key=lambda assignment: assignment.value)
        return assignments

    # Assign orders to pieces for each assignment
    def confirm_assignments(self, assignments):
        assigned_pieces = []
        assigned_tasks = []

        for assignment in assignments:
            if assignment.piece not in assigned_pieces and assignment.task not in assigned_tasks:
                assigned_pieces.append(assignment.piece)

                # TODO: How many pieces should be able to work on a task?
                assigned_tasks.append(assignment.task)

                # Set an order to the piece in the assignment
                self.set_order_for_task(assignment.piece, assignment.task)

    # Translate a task into an order for the piece to follow
    def set_order_for_task(self, piece, task):
        if task.task_type == TaskType.HARVEST_RESOURCE:
            # Get tiles adjacent to the target
            adjacent_tiles = self.get_manager(Manager.MAP)\
                .get_valid_adjacent_tiles_for_movement_type(task.tx, task.ty, piece.attr(Attribute.MOVEMENT_TYPE))

            # Filter and sort adjacent tiles to the nearest tile we can occupy / stand in
            adjacent_tiles = [tile for tile in adjacent_tiles if piece.is_tile_occupyable(tile)]
            adjacent_tiles.sort(key=lambda tile: abs(tile[0] - piece.gx) + abs(tile[1] - piece.gy))

            if not (piece.gx, piece.gy) in adjacent_tiles:
                # If we're not already on one of the adjacent tiles,
                # try to figure out paths to get next to the target, and then move to one of them
                path = piece.get_path_to_destinations(adjacent_tiles)
                if path:
                    destination = piece.step_along_path(path)
                    if destination:
                        # Try to get to the goal.
                        piece.set_order(Event(USEREVENT, {
                            'option': Option.MENU_MOVE,
                            'dx': destination[0],
                            'dy': destination[1],
                        }))
                    else:
                        # There's no valid partial step to our goal
                        pass
                else:
                    # There's no valid path to our goal anymore
                    pass
            else:
                # Once we're next to the goal, issue a BUILD order
                # TODO: Check that we have enough resources first
                piece.set_order(Event(USEREVENT, {
                    'option': PieceType.GENERATOR,
                    'dx': task.tx,
                    'dy': task.ty,
                }))

    def handle_orders_phase(self, event):
        self.parse_board_state()

        tasks = self.generate_tasks()

        assignments = self.assign_tasks(tasks)

        self.confirm_assignments(assignments)

        self.get_manager(Manager.TEAM).set_ai_turn_submitted(self.team)
