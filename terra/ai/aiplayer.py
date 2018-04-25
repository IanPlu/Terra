from math import floor

from pygame import USEREVENT
from pygame.event import Event

from terra.ai.personality import create_default_personality
from terra.ai.task import Task, TaskType, Assignment
from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.session import Manager
from terra.map.tiletype import TileType
from terra.menu.option import Option
from terra.mode import Mode
from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType
from terra.piece.piecetype import PieceType
from terra.piece.piecearchetype import PieceArchetype


# An AI player, in charge of giving orders to a team.
# When the Orders phase begins, it'll provide orders to its team.
class AIPlayer(GameObject):
    def __init__(self, team):
        super().__init__()

        self.team = team

        # Turn planning data
        self.planned_spending = 0
        self.planned_occupied_coords = []

        # Aliases for commonly accessed data
        self.my_pieces = None
        self.enemy_pieces = None
        self.map = None

        self.personality = create_default_personality()

        self.debug_print_tasks = True
        self.debug_print_assignments = True

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.START_PHASE_ORDERS, self.handle_orders_phase)

    def is_accepting_events(self):
        return self.get_mode() in [Mode.BATTLE, Mode.LOBBY]

    # Rebuild the AI's understanding of the board, map, and pieces
    def parse_board_state(self):
        self.planned_spending = 0
        self.planned_occupied_coords = []

        self.my_pieces = self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team)
        self.enemy_pieces = self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team)
        self.map = self.get_manager(Manager.MAP)

    # Generate a list of tasks that we'd like to accomplish this turn
    def generate_tasks(self):
        tasks = []

        tasks.extend(self.generate_combat_tasks())
        tasks.extend(self.generate_economic_tasks())

        # TODO: Sort tasks by priority

        if self.debug_print_tasks:
            print("== Tasks ==")
            for task in tasks:
                print(task)

        return tasks

    # Generate tasks focused on attacking the enemy.
    def generate_combat_tasks(self):
        tasks = []
        enemy_pieces = self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team)

        # Order our pieces to retreat and heal when they get low
        injured_pieces = [piece for piece in self.my_pieces if piece.hp / piece.attr(Attribute.MAX_HP) <=
                          self.personality.retreat_threshold]
        for injured in injured_pieces:
            # If it's not safe to heal here, create an order to retreat
            if injured.is_contested():
                task = self.create_retreat_task(injured)
                if task:
                    tasks.append(task)
            else:
                tasks.append(self.create_heal_task(injured))

        # Try to attack all enemies
        for enemy in enemy_pieces:
            tasks.append(self.create_attack_enemy_task(enemy))

        return tasks

    def generate_economic_tasks(self):
        tasks = []
        piece_manager = self.get_manager(Manager.PIECE)

        # Get a list of open resource tiles, add tasks to harvest them
        harvestable_coords = [coord for coord in self.map.find_tiles_by_type(TileType.RESOURCE)
                              if len(piece_manager.get_pieces_at(coord[0], coord[1], PieceType.GENERATOR)) == 0]
        # Sort those resource tiles by whether they're immediately harvestable or not
        immediate_harvest_coords = [coord for coord in harvestable_coords if self.is_immediately_harvestable(coord)]
        moveto_coords = list(set(harvestable_coords) - set(immediate_harvest_coords))

        for coord in immediate_harvest_coords:
            tasks.append(self.create_harvest_task(coord))
        for coord in moveto_coords:
            tasks.append(self.create_moveto_harvest_task(coord))

        # Determine how many colonists we should have, and add tasks to build more if needed
        current_num_colonists = len(piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.COLONIST))
        # TODO: This needs to be ceil and not floor. On small maps will always produce <1.
        # Need to account for density of resource tiles too
        desired_num_colonists = floor((self.map.width * self.map.height) / 150) if len(harvestable_coords) > 0 else 0

        if current_num_colonists < desired_num_colonists:
            tasks.append(self.create_build_colonist_task())

        # Build new military units whenever possible, at each barracks
        for _ in piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.BARRACKS):
            tasks.extend(self.create_build_military_tasks())

        return tasks

    # Return true if the specified coord is immediately harvestable (has an adjacent Colonist)
    def is_immediately_harvestable(self, coord):
        adjacent_colonists = [piece for piece in self.get_manager(Manager.PIECE).get_adjacent_pieces(coord[0], coord[1], self.team)
                              if piece.piece_type == PieceType.COLONIST]
        return len(adjacent_colonists) > 0

    def create_harvest_task(self, coord):
        return Task(self.team, TaskType.HARVEST_RESOURCE, coord[0], coord[1])

    def create_moveto_harvest_task(self, coord):
        return Task(self.team, TaskType.MOVE_TO_RESOURCE, coord[0], coord[1])

    def create_build_colonist_task(self):
        return Task(self.team, TaskType.BUILD_UNIT, target=PieceType.COLONIST)

    def create_attack_enemy_task(self, target):
        return Task(self.team, TaskType.ATTACK_ENEMY, target.gx, target.gy, target)

    def create_heal_task(self, injured):
        return Task(self.team, TaskType.HEAL_SELF, target=injured)

    def create_retreat_task(self, piece):
        bases = self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team, piece_type=PieceType.BASE)
        if len(bases) > 0:
            return Task(self.team, TaskType.RETREAT, bases[0].gx, bases[0].gy, target=piece)
        else:
            return None

    def create_build_military_tasks(self):
        # TODO: Add weighting for piece types based on personality
        tasks = []
        counts = self.get_manager(Manager.PIECE).get_archetype_counts(self.team, units_only=True)
        target_archetype = PieceArchetype.GROUND

        if len(counts) > 0:
            target_archetype, amount = counts[-1]

        for piece_type in self.get_buildable_pieces(target_archetype):
            tasks.append(Task(self.team, TaskType.BUILD_UNIT, target=piece_type))

        return tasks

    # Return a list of pieces we can build for this archetype
    # TODO: Query for upgrades and higher tier units
    def get_buildable_pieces(self, piece_archetype):
        return {
            PieceArchetype.GROUND: [PieceType.TROOPER],
            PieceArchetype.RANGED: [PieceType.RANGER],
            PieceArchetype.MOBILITY: [PieceType.GHOST],
        }[piece_archetype]

    # Create assignments for each task
    # TODO: Add weighting factors, run this multiple times to get different 'best' turns
    def assign_tasks(self, tasks):
        assignments = []
        for task in tasks:
            eligible_pieces = task.get_eligible_pieces_for_task(self.get_manager(Manager.PIECE))
            # Preplan each assignment, and score it
            for piece in eligible_pieces:
                assignment = self.create_assignment(piece, task)
                if assignment:
                    assignments.append(assignment)

        # Sort assignments by their score (lowest scores first)
        assignments.sort(key=lambda assignment: assignment.value)

        if self.debug_print_assignments:
            print("== Assignments ==")
            for assignment in assignments:
                print(assignment)

        return assignments

    def create_assignment(self, piece, task):
        battle_map = self.get_manager(Manager.MAP)

        if task.task_type in [TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY, TaskType.RETREAT]:
            # TASK: Move towards a target.
            #   MOVE_TO_RESOURCE: Attempt to reach tiles adjacent to the target resource, with intent to harvest.
            #   ATTACK_ENEMY: Attempt to reach the enemy tile, with intent to harm.
            #   RETREAT: Attempt to move away from attackers.

            if task.target_adjacent:
                # Get tiles adjacent to the target
                adjacent_tiles = battle_map.get_valid_adjacent_tiles_for_movement_type(task.tx, task.ty,
                                                                                       piece.attr(Attribute.MOVEMENT_TYPE))

                # Filter and sort adjacent tiles to the nearest tile we can occupy / stand in
                tiles = [tile for tile in adjacent_tiles if piece.is_tile_occupyable(tile)]
                tiles.sort(key=lambda tile: abs(tile[0] - piece.gx) + abs(tile[1] - piece.gy))
            else:
                # Move directly to the target tile
                tiles = [(task.tx, task.ty)]

            # Try to path towards our goal(s)
            path = piece.get_path_to_destinations(tiles)
            if path:
                # Try to step incrementally towards the goal.
                destination = piece.step_along_path(path)
                distance = abs(destination[0] - piece.gx) + abs(destination[1] - piece.gy)
                score = task.score_piece_for_task(piece, battle_map) + distance

                return Assignment(piece, task, score, end_pos=[destination], path=path)
            else:
                if (piece.gx, piece.gy) in tiles:
                    # We are already at the destination!
                    return Assignment(piece, task, task.score_piece_for_task(piece, battle_map))
                else:
                    # There's no valid path to our goal anymore
                    # TODO: RETREAT tasks don't care (just want to get away), so still issue an assignment
                    return None
        elif task.task_type == TaskType.HARVEST_RESOURCE:
            # TASK: Harvest an adjacent resource tile
            # We're next to the goal already, presumably, so no pathfinding
            score = task.score_piece_for_task(piece, battle_map)
            return Assignment(piece, task, score, end_pos=[(piece.gx, piece.gy), (task.tx, task.ty)])
        elif task.task_type in [TaskType.BUILD_UNIT]:
            # Task: Build the specified unit.
            score = task.score_piece_for_task(piece, battle_map)
            if task.tx and task.ty:
                return Assignment(piece, task, score, end_pos=[(piece.gx, piece.gy), (task.tx, task.ty)])
        elif task.task_type == TaskType.HEAL_SELF:
            # TASK: Heal self.
            score = task.score_piece_for_task(piece, battle_map)
            return Assignment(piece, task, score, end_pos=[(piece.gx, piece.gy), (task.tx, task.ty)])
        else:
            return None

    # Assign orders to pieces for each assignment
    def confirm_assignments(self, assignments):
        assigned_pieces = []
        assigned_tasks = []

        # TODO: Add understanding of piece occupation + orders
        # e.g. allow a piece to move onto the same tile a second piece was just in, if that second piece is moving away
        # Allow building onto a tile where a second piece is, if that second piece is moving away

        for assignment in assignments:
            if assignment.piece not in assigned_pieces and assignment.task not in assigned_tasks:
                can_confirm_assignment = True

                # Only confirm the assignment if we can afford it
                new_spending = assignment.task.get_planned_spending(self.get_manager(Manager.TEAM))
                if new_spending > 0 and self.planned_spending + new_spending > \
                        self.get_manager(Manager.TEAM).resources[self.team]:
                    can_confirm_assignment = False

                # Only confirm the assignment if it won't occupy the same tile twice
                newly_occupied_tiles = assignment.end_pos
                if newly_occupied_tiles and not set(self.planned_occupied_coords).isdisjoint(set(newly_occupied_tiles)):
                    can_confirm_assignment = False

                # If no other objections, allow the assignment to happen
                if can_confirm_assignment:
                    # Remove the piece from the eligible pool
                    assigned_pieces.append(assignment.piece)

                    # Remove the task from the eligible pool
                    if not assignment.task.allow_multiple_assignments:
                        assigned_tasks.append(assignment.task)

                    # Set an order to the piece in the assignment
                    self.set_order_for_task(assignment)

                    # Mark planned spending
                    self.planned_spending += new_spending
                    # Mark occupied locations
                    if assignment.end_pos:
                        for pos in assignment.end_pos:
                            self.planned_occupied_coords.append(pos)

        return assigned_pieces, assigned_tasks

    # Translate a task into an order for the piece to follow
    def set_order_for_task(self, assignment):
        piece = assignment.piece
        task = assignment.task

        piece.current_path = assignment.path

        if task.task_type in [TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY]:

            # Ranged units should issue attack orders when close enough
            distance = abs(task.tx - piece.gx) + abs(task.ty - piece.gy)
            if piece.attr(Attribute.DAMAGE_TYPE) == DamageType.RANGED and \
                    task.task_type in [TaskType.ATTACK_ENEMY] and \
                    piece.attr(Attribute.MIN_RANGE) <= distance <= piece.attr(Attribute.MAX_RANGE):
                # Conduct a ranged attack on the target
                # TODO: Currently will not try to step backwards out of its minimum range
                piece.set_order(Event(USEREVENT, {
                    'option': Option.MENU_RANGED_ATTACK,
                    'dx': task.tx,
                    'dy': task.ty,
                }))
            else:
                # Move to the specified end position.
                dx, dy = assignment.end_pos[0]
                piece.set_order(Event(USEREVENT, {
                    'option': Option.MENU_MOVE,
                    'dx': dx,
                    'dy': dy,
                }))
        elif task.task_type == TaskType.HARVEST_RESOURCE:
            # We're next to the goal, so issue a BUILD order
            piece.set_order(Event(USEREVENT, {
                'option': PieceType.GENERATOR,
                'dx': task.tx,
                'dy': task.ty,
            }))
        elif task.task_type == TaskType.BUILD_UNIT:
            piece.set_order(Event(USEREVENT, {
                'option': task.target,
                'dx': task.tx,
                'dy': task.ty,
            }))
        elif task.task_type == TaskType.HEAL_SELF:
            piece.set_order(Event(USEREVENT, {
                'option': Option.MENU_HEAL_SELF,
            }))

    def handle_orders_phase(self, event):
        self.parse_board_state()

        # TODO new planning strategy:
        # - Generate tasks
        # - Generate assignments (do NOT path towards the target, or do very minimal pathing)
        # - Confirm assignments in order of importance (either via piece or via task)
        #       * Do full pathing and planning here, so we can account for the planned occupied tiles better

        tasks = self.generate_tasks()

        assignments = self.assign_tasks(tasks)

        assigned_pieces, assigned_tasks = self.confirm_assignments(assignments)

        # TODO: Handle any unclaimed tasks?
        # leftover_tasks = [task for task in tasks if task not in assigned_tasks]

        # TODO: Fill in unspent resources?

        self.get_manager(Manager.TEAM).set_ai_turn_submitted(self.team)
