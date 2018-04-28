from math import ceil

from pygame import USEREVENT
from pygame.event import Event

from terra.ai.pathfinder import navigate_all
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
from terra.piece.movementtype import MovementType
from terra.piece.piece import Piece
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType


# An AI player, in charge of giving orders to a team.
# When the Orders phase begins, it'll provide orders to its team.
class AIPlayer(GameObject):
    def __init__(self, team):
        self.team = team

        # Turn planning data
        self.planned_spending = 0
        self.planned_occupied_coords = []
        self.tasks = []
        self.assignments = []
        self.income = 0

        # Aliases for commonly accessed data
        self.my_pieces = None
        self.enemy_pieces = None
        self.map = None

        self.personality = create_default_personality()

        # General map navigation
        self.came_from = {}
        self.distance_map = {}

        self.debug_print_tasks = False
        self.debug_print_assignments = False
        self.debug_print_confirmations = False
        self.debug_assign_orders_immediately = False

        super().__init__()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        if self.debug_assign_orders_immediately:
            event_bus.register_handler(EventType.START_PHASE_ORDERS, self.debug_handle_orders_phase)
        else:
            event_bus.register_handler(EventType.START_PHASE_ORDERS, self.handle_orders_phase)
            event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.handle_turn_submitted)

    def is_accepting_events(self):
        return self.get_mode() in [Mode.BATTLE, Mode.LOBBY]

    # Rebuild the AI's understanding of the board, map, and pieces
    def parse_board_state(self):
        piece_manager = self.get_manager(Manager.PIECE)
        self.my_pieces = piece_manager.get_all_pieces_for_team(self.team)
        self.enemy_pieces = piece_manager.get_all_enemy_pieces(self.team)
        self.map = self.get_manager(Manager.MAP)

        self.income = piece_manager.get_income(self.team)
        self.planned_spending = 0
        # Mark buildings as planned occupied tiles to start
        self.planned_occupied_coords = [(piece.gx, piece.gy) for piece in self.my_pieces
                                        if piece.piece_subtype == PieceSubtype.BUILDING]

        self.calculate_line_of_play()

    def calculate_line_of_play(self):
        # NOTES:
        # 1. Do basic GROUND pathfinding from my base to the enemy base. This is the critical path
        #       1a. Recalculate this any time terraforming occurs and the critical path may have changed
        #       1b. There may be multiple critical paths. Do pathfinding multiple times, and take ALL paths with the
        #           same lowest distance score as critical paths(?)
        # 2. Calculate where each piece for each team is on the critical path.
        #       - From the home team side to the enemy team side, mark the first time we encounter an enemy on the line
        #       - Then mark the last time we encountered an ally
        #       - The midpoint between these two marks if the Line of Play

        # Do basic pathfinding to the enemy base from every location.
        # Most importantly this produces a distance map from every tile to the enemy base.
        # TODO: Only supports one base, for the moment
        bases = self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team, piece_type=PieceType.BASE)
        if len(bases) <= 0:
            return
        else:
            base = bases[0]
            self.came_from, self.distance_map = navigate_all((base.gx, base.gy), self.map, MovementType.GROUND)

    # Generate a list of tasks that we'd like to accomplish this turn
    def generate_tasks(self):
        tasks = []

        tasks.extend(self.generate_combat_tasks())
        tasks.extend(self.generate_economic_tasks())
        tasks.extend(self.generate_research_tasks())

        # TODO: Sort tasks by priority

        if self.debug_print_tasks:
            print("== Tasks ==")
            for task in tasks:
                print(task)

        return tasks

    # Generate tasks focused on combat. Attack enemies, defend key areas, retreat wounded units.
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

        # TODO: Generate tasks to defend key targets (Base, Barracks, Colonists)
        # Generate base defense task with priority and assignment limit based on number of nearby enemies
        # Generate barracks defense task with similar (but lower) priority to base defense
        # Generate Colonist defense tasks. Try to keep close / move WITH the Colonist

        # Try to attack all enemies
        for enemy in enemy_pieces:
            tasks.append(self.create_attack_enemy_task(enemy))

        return tasks

    # Generate economy-focused tasks, like harvesting resources
    def generate_economic_tasks(self):
        tasks = []
        piece_manager = self.get_manager(Manager.PIECE)

        # Get all possible harvestable coordinates
        all_harvestable_coords = [coord for coord in self.map.find_tiles_by_type(TileType.RESOURCE)
                                  if len(piece_manager.get_pieces_at(coord[0], coord[1], PieceType.GENERATOR)) == 0]

        # Get a list of open resource tiles, add tasks to harvest them. Search only the reachable tiles from the HQ.
        harvestable_coords = [coord for coord in all_harvestable_coords if coord in self.distance_map.keys()]

        # Sort those resource tiles by whether they're immediately harvestable or not
        immediate_harvest_coords = [coord for coord in harvestable_coords if self.is_immediately_harvestable(coord)]
        moveto_coords = list(set(harvestable_coords) - set(immediate_harvest_coords))

        # TODO: Generate terraforming tasks to get to these resources
        terraforming_required_resources = list(set(all_harvestable_coords) - set(harvestable_coords))

        for coord in immediate_harvest_coords:
            tasks.append(self.create_harvest_task(coord))
        for coord in moveto_coords:
            tasks.append(self.create_moveto_harvest_task(coord))

        # Determine how many colonists we should have, and add tasks to build more if needed
        current_num_colonists = len(piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.COLONIST))
        num_open_resources = len(harvestable_coords)
        map_size = len(self.distance_map)

        desired_num_colonists = ceil(map_size / 150) if num_open_resources > 0 else 0

        if current_num_colonists < desired_num_colonists:
            tasks.append(self.create_build_colonist_task())

        # Build new military units whenever possible, at each barracks
        for _ in piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.BARRACKS):
            tasks.extend(self.create_build_military_tasks())

        # Build new barracks when possible
        current_num_barracks = len(piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.BARRACKS))
        highest_piece_price = self.get_highest_piece_price()
        income_threshold = highest_piece_price * current_num_barracks
        # If our income is surpassing our ability to produce units, build more barracks
        if self.income > income_threshold:
            tasks.append(self.create_build_barracks_task())

        return tasks

    # TODO: Weigh upgrade choices by personality + unit preferences
    def generate_research_tasks(self):
        tasks = []
        piece_manager = self.get_manager(Manager.PIECE)

        # If we don't have a tech lab, we should build one
        if len(piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.TECHLAB)) == 0:
            # Build a tech lab, since we don't have one
            tasks.append(self.create_build_techlab_task())
        else:
            # Generate research tasks to produce new unit types
            # Additionally, generate tasks to research upgrades in the tech lab's research list
            pass

        # Generate economic research tasks. Pick an upgrade from the HQ's research list
        # TODO

        # Generate military research tasks. Pick an upgrade from the barracks' research list
        # TODO

        return tasks

    # TODO: Figure out the piece price by tech level
    def get_highest_piece_price(self):
        has_t2_units = False
        has_t3_units = False

        if has_t3_units:
            return 12
        elif has_t2_units:
            return 5
        else:
            return 3

    # Return true if the specified coord is immediately harvestable (has an adjacent Colonist)
    def is_immediately_harvestable(self, coord):
        adjacent_colonists = [piece for piece in self.get_manager(Manager.PIECE).get_adjacent_pieces(coord[0], coord[1], self.team)
                              if piece.piece_type == PieceType.COLONIST]
        return len(adjacent_colonists) > 0

    def create_harvest_task(self, coord):
        return Task(self.team, TaskType.HARVEST_RESOURCE, coord[0], coord[1], target=PieceType.GENERATOR)

    def create_moveto_harvest_task(self, coord):
        return Task(self.team, TaskType.MOVE_TO_RESOURCE, coord[0], coord[1])

    def create_build_colonist_task(self):
        return Task(self.team, TaskType.BUILD_PIECE, target=PieceType.COLONIST)

    def create_build_barracks_task(self):
        return Task(self.team, TaskType.BUILD_PIECE, target=PieceType.BARRACKS)

    def create_build_techlab_task(self):
        return Task(self.team, TaskType.BUILD_PIECE, target=PieceType.TECHLAB)

    def create_attack_enemy_task(self, target):
        anticipated_x, anticipated_y = self.get_anticipated_movement(target)
        return Task(self.team, TaskType.ATTACK_ENEMY, anticipated_x, anticipated_y, target)

    def get_anticipated_movement(self, piece):
        if piece.piece_subtype == PieceSubtype.BUILDING:
            # Buildings usually don't go anywhere
            return piece.gx, piece.gy
        else:
            # TODO: Try to anticipate where the enemy will be
            # 1. Determine the movement range of the enemy (tile selection UI)
            # 2. Score each tile in range based on targets it might attack
            # 3. Score likelihood of it moving at all(buildings don't move, ranged units might attack, might repair)
            # Use all this to determine the most likely tile the unit will be on next turn and target THAT tile instead
            return piece.gx, piece.gy

    def create_heal_task(self, injured):
        return Task(self.team, TaskType.HEAL_SELF, target=injured)

    def create_retreat_task(self, piece):
        bases = self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team, piece_type=PieceType.BASE)
        if len(bases) > 0:
            return Task(self.team, TaskType.RETREAT, bases[0].gx, bases[0].gy, target=piece)
        else:
            return None

    def create_build_military_tasks(self):
        # TODO: Add weighting based on enemy team composition
        tasks = []
        counts = self.get_manager(Manager.PIECE).get_archetype_counts(self.team, units_only=True)
        counts_map = {}
        # Weight counts by personality
        for archetype, count in counts:
            counts_map[archetype] = count / self.personality.unit_construction_weight[archetype]

        target_archetype = PieceArchetype.GROUND
        if len(counts) > 0:
            # Find the lowest count
            target_archetype, amount = min(counts_map.items(), key=lambda pair: pair[1])

        for piece_type in self.get_buildable_pieces(target_archetype):
            tasks.append(Task(self.team, TaskType.BUILD_PIECE, target=piece_type))

        return tasks

    # Return a list of pieces we can build for this archetype
    # TODO: Query for upgrades / higher tier units
    def get_buildable_pieces(self, piece_archetype):
        return {
            PieceArchetype.GROUND: [PieceType.TROOPER],
            PieceArchetype.RANGED: [PieceType.RANGER],
            PieceArchetype.MOBILITY: [PieceType.GHOST],
        }[piece_archetype]

    # Create assignments for each task
    # TODO: Add weighting factors, run this multiple times to get different 'best' turns(?)
    def assign_tasks(self, tasks):
        assignments = []
        # For each task, create assignments of each eligible piece and score it by suitability
        for task in tasks:
            for eligible_piece in task.get_eligible_pieces_for_task(self.get_manager(Manager.PIECE)):
                score, end_pos = task.score_piece_for_task(eligible_piece, self.distance_map)
                assignments.append(Assignment(eligible_piece, task, score, end_pos=end_pos))

        # Sort assignments by their score (lowest scores first)
        assignments.sort(key=lambda a: a.value)

        if self.debug_print_assignments:
            print("== Assignments ==")
            for assignment in assignments:
                print(assignment)

        return assignments

    # Assign orders to pieces for each assignment
    def confirm_assignments(self, assignments):
        if self.debug_print_confirmations:
            print("== Confirming {} assignments".format(len(assignments)))

        assigned_pieces = []
        assigned_tasks = []

        for assignment in assignments:
            if assignment.value < 99999 and assignment.piece not in assigned_pieces and \
                    assignment.task not in assigned_tasks:
                enough_money = True
                tiles_free = True

                # Only confirm the assignment if we can afford it
                new_spending = assignment.task.get_planned_spending(self.get_manager(Manager.TEAM))
                if new_spending > 0 and self.planned_spending + new_spending > \
                        self.get_manager(Manager.TEAM).resources[self.team]:
                    enough_money = False

                # Only confirm the assignment if it won't occupy the same tile twice
                newly_occupied_tiles = assignment.get_end_position(self.planned_occupied_coords)
                if not newly_occupied_tiles:
                    tiles_free = False
                elif not set(self.planned_occupied_coords).isdisjoint(set(newly_occupied_tiles)):
                    tiles_free = False

                # If no other objections, allow the assignment to happen
                if enough_money and tiles_free:
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
                    for coord in newly_occupied_tiles:
                        self.planned_occupied_coords.append(coord)

                    if self.debug_print_confirmations:
                        print("+ Set order for assignment {}".format(assignment))
                elif self.debug_print_confirmations:
                    print("- Elected not to set order for assignment {} due to objections:\n"
                          "   Enough money? {}, {}\n"
                          "   Tiles free? {}, {}".format(assignment, enough_money, new_spending,
                                                         tiles_free, newly_occupied_tiles))

        return assigned_pieces, assigned_tasks

    # Translate a task into an order for the piece to follow
    def set_order_for_task(self, assignment):
        piece = assignment.piece
        task = assignment.task

        assignment.path = piece.current_path

        order = None
        tx = assignment.tx
        ty = assignment.ty

        if isinstance(task.target, Piece):
            ranged_distance = abs(task.target.gx - piece.gx) + abs(task.target.gy - piece.gy)
        else:
            ranged_distance = 0

        if task.task_type in [TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY]:
            # Ranged units should issue attack orders instead of move orders when close enough to their target
            if piece.attr(Attribute.DAMAGE_TYPE) == DamageType.RANGED and \
                    task.task_type in [TaskType.ATTACK_ENEMY] and \
                    piece.attr(Attribute.MIN_RANGE) <= ranged_distance <= piece.attr(Attribute.MAX_RANGE):
                # Conduct a ranged attack on the target
                order = Option.MENU_RANGED_ATTACK
                tx = task.tx
                ty = task.ty
            else:
                # Move to the specified end position.
                order = Option.MENU_MOVE
        elif task.task_type == TaskType.HARVEST_RESOURCE:
            # We're next to the goal, so issue a BUILD order
            order = PieceType.GENERATOR
        elif task.task_type == TaskType.BUILD_PIECE:
            # We're next to the goal, so issue a BUILD order
            order = task.target
        elif task.task_type == TaskType.HEAL_SELF:
            # Heal ourselves in place
            order = Option.MENU_HEAL_SELF
        elif task.task_type == TaskType.RESEARCH_UPGRADE:
            # Research an upgrade
            order = task.target

        # Assign the order to the piece, simulating a menu event
        if order:
            piece.set_order(Event(USEREVENT, {
                'option': order,
                'dx': tx,
                'dy': ty,
            }))

    # Give leftover pieces an order
    def move_leftover_pieces(self, leftovers):
        for piece in leftovers:
            movement_range = piece.attr(Attribute.MOVEMENT_RANGE)
            movement_type = piece.attr(Attribute.MOVEMENT_TYPE)

            if movement_range > 0:
                if (piece.gx, piece.gy) in self.planned_occupied_coords:
                    valid_tiles = self.map.get_tiles_in_range(piece.gx, piece.gy, 0, movement_range, movement_type)

                    # Remove planned coords from valid tiles
                    valid_tiles = list(set(valid_tiles) - set(self.planned_occupied_coords))

                    # Pick an arbitrary tile and pathfind to it
                    # destination = valid_tiles[randint(0, len(valid_tiles) - 1)]
                    destination = valid_tiles[0]
                    path = piece.get_path_to_target(destination, self.planned_occupied_coords, movement_type=movement_type)
                    final_goal = piece.step_along_path(path, self.planned_occupied_coords)

                    if final_goal == (piece.gx, piece.gy):
                        # We couldn't find a path to get out of the way, so delete ourselves
                        piece.set_order(Event(USEREVENT, {
                            'option': Option.MENU_DEMOLISH_SELF,
                        }))
                    else:
                        # Update the planned occupied coords, issue the order
                        self.planned_occupied_coords.append(final_goal)

                        piece.set_order(Event(USEREVENT, {
                            'option': Option.MENU_MOVE,
                            'dx': final_goal[0],
                            'dy': final_goal[1],
                        }))
                else:
                    # Add ourselves to the planned occupied coords
                    self.planned_occupied_coords.append((piece.gx, piece.gy))

    def debug_handle_orders_phase(self, event):
        self.handle_orders_phase(event)
        self.handle_turn_submitted(event)

    # Calculate what the world looks like right now
    def handle_orders_phase(self, event):
        self.parse_board_state()

        # Generate all potential tasks the AI might want to accomplish
        self.tasks = self.generate_tasks()

        # Generate assignments between tasks and pieces that can possibly execute the task
        self.assignments = self.assign_tasks(self.tasks)

    # Act on planning and issue orders
    def handle_turn_submitted(self, event):
        # Confirm assignments in order of importance, issue concrete orders.
        assigned_pieces, assigned_tasks = self.confirm_assignments(self.assignments)

        # TODO: Handle any unclaimed tasks?
        # leftover_tasks = [task for task in tasks if task not in assigned_tasks]

        # Pieces without orders should get out of the way of pieces with more important orders
        self.move_leftover_pieces(list(set(self.my_pieces) - set(assigned_pieces)))

        # TODO: Fill in unspent resources?

        # Mark the turn as submitted so the game can progress when the player is ready
        self.get_manager(Manager.TEAM).set_turn_submitted(self.team)
