from math import ceil
from random import sample
from threading import Thread

from pygame import USEREVENT
from pygame.event import Event

from terra.ai.pathfinder import navigate_all, get_terraform_tiles
from terra.ai.personality import create_default_personality
from terra.ai.task import Task, TaskType, Assignment
from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.economy.upgradetype import UpgradeType
from terra.economy.upgradetype import unit_research
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
from terra.piece.piecearchetype import PieceArchetype, counter_archetype
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
        self.is_thinking = False

        # Aliases for commonly accessed data
        self.my_pieces = None
        self.my_piece_counts = None
        self.my_archetype_counts = None
        self.enemy_pieces = None
        self.enemy_archetype_counts = None
        self.map = None

        self.personality = create_default_personality()

        # General map navigation
        self.came_from = {}
        self.distance_map = {}

        self.debug_print_tasks = False
        self.debug_print_assignments = False
        self.debug_print_confirmations = False

        self.do_threaded_planning = True

        self.parse_board_state()

        super().__init__()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        if self.do_threaded_planning:
            # When the player submits their turn, plan out the AI turn on a separate thread
            event_bus.register_handler(EventType.AI_REPLAN_TURN, self.begin_threaded_planning)
            event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.begin_threaded_planning)
        else:
            # At start of turn, do preplanning. Then complete planning the turn when the player submits their turn
            event_bus.register_handler(EventType.AI_REPLAN_TURN, self.do_all_planning)
            event_bus.register_handler(EventType.START_PHASE_START_TURN, self.do_preplanning)
            event_bus.register_handler(EventType.E_TURN_SUBMITTED, self.act_on_planning)

    def is_accepting_events(self):
        return self.get_mode() in [Mode.BATTLE, Mode.LOBBY]

    # Rebuild the AI's understanding of the board, map, and pieces
    def parse_board_state(self):
        piece_manager = self.get_manager(Manager.PIECE)
        self.my_pieces = piece_manager.get_all_pieces_for_team(self.team)
        self.my_piece_counts = dict(piece_manager.get_piece_counts(self.team))
        self.my_archetype_counts = piece_manager.get_archetype_counts(self.team, units_only=True)
        self.enemy_pieces = piece_manager.get_all_enemy_pieces(self.team)
        self.enemy_archetype_counts = piece_manager.get_enemy_archetype_counts(self.team, units_only=True)
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
        # Only supports one base, for the moment (no 3+ player games)
        bases = self.get_manager(Manager.PIECE).get_all_enemy_pieces(self.team, piece_type=PieceType.BASE)
        if len(bases) <= 0:
            return
        else:
            base = bases[0]
            self.came_from, self.distance_map = navigate_all((base.gx, base.gy), self.map, MovementType.GROUND)

    # Generate a list of tasks that we'd like to accomplish this turn
    def generate_tasks(self):
        # Tasks look like (Task(), priority)
        tasks = []

        tasks.extend(self.generate_combat_tasks())
        tasks.extend(self.generate_economic_tasks())
        tasks.extend(self.generate_research_tasks())

        tasks.sort(key=lambda pair: pair[1], reverse=True)

        if self.debug_print_tasks:
            print("== Tasks ==")
            for task in tasks:
                print(task)

        # Only return the tasks, not the priorities
        return [task for task, priority in tasks]

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

        # Get a list of reachable open resource tiles, add tasks to harvest them.
        harvestable_coords = [coord for coord in all_harvestable_coords if coord in self.distance_map.keys()]

        # Sort those resource tiles by whether they're immediately harvestable or not (Colonist adjacent)
        immediate_harvest_coords = [coord for coord in harvestable_coords if self.is_immediately_harvestable(coord)]
        moveto_coords = list(set(harvestable_coords) - set(immediate_harvest_coords))

        # Generate terraforming tasks for resources inaccessible from a path from the base
        if self.get_manager(Manager.TEAM).has_upgrade(self.team, UpgradeType.COLONIST_TERRAFORMING):
            terraforming_required_resources = list(set(all_harvestable_coords) - set(harvestable_coords))
            tasks.extend(self.create_terraforming_tasks(terraforming_required_resources))

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

    def generate_research_tasks(self):
        tasks = []
        piece_manager = self.get_manager(Manager.PIECE)
        team_manager = self.get_manager(Manager.TEAM)

        upgrades_to_research = []

        def queue_upgrade(upgrade):
            upgrades_to_research.append((self.score_researchable_upgrade(upgrade), upgrade))

        # If we don't have a tech lab, we should build one
        if len(piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.TECHLAB)) == 0:
            # Build a tech lab, since we don't have one
            tasks.append(self.create_build_techlab_task())
        else:
            # Generate research tasks to produce new unit types
            for upgrade in unit_research:
                if not team_manager.has_upgrade(self.team, upgrade):
                    queue_upgrade(upgrade)

            # Additionally, generate tasks to research upgrades in the tech lab's research list
            for upgrade in self.pick_researchable_upgrades(PieceType.TECHLAB, self.personality.research_to_consider):
                queue_upgrade(upgrade)

        # Generate economic research tasks. Pick an upgrade from the HQ's research list
        for upgrade in self.pick_researchable_upgrades(PieceType.BASE, self.personality.research_to_consider):
            queue_upgrade(upgrade)

        # Generate military research tasks. Pick an upgrade from the barracks' research list
        for upgrade in self.pick_researchable_upgrades(PieceType.BARRACKS, self.personality.research_to_consider):
            queue_upgrade(upgrade)

        # Take the top few research items, based on personality
        upgrades_to_research.sort(key=lambda pair: pair[0])
        num_to_research = min(self.personality.research_to_consider, len(upgrades_to_research))
        tasks.extend([self.create_research_task(upgrade) for upgrade in upgrades_to_research[0:num_to_research]])

        return tasks

    # Pick <number> upgrades that <piece_type> can research
    def pick_researchable_upgrades(self, piece_type, number):
        researchable_upgrades = self.get_manager(Manager.TEAM).attr(self.team, piece_type, Attribute.PURCHASEABLE_UPGRADES)
        k = min(number, len(researchable_upgrades))
        if k > 0:
            return sample(researchable_upgrades, k=k)
        else:
            return []

    def score_researchable_upgrade(self, upgrade):
        score = 10
        upgrade_attributes = base_upgrades.get(upgrade)

        # Score new unit research inherently higher
        if upgrade_attributes.get(UpgradeAttribute.NEW_BUILDABLE, None):
            score -= self.personality.new_unit_tier_priority

        # Weigh other research by how many pieces they'll affect (e.g. if we have lots of Troopers, upgrade them)
        total_pieces = len(self.my_pieces)
        if upgrade_attributes.get(UpgradeAttribute.DISPLAY_FOR, None):
            for piece_type in upgrade_attributes[UpgradeAttribute.DISPLAY_FOR]:
                piece_proportion = round(self.my_piece_counts.get(piece_type, 0) / total_pieces, 2)
                preference_weight = self.personality.unit_preference\
                    .get(self.get_manager(Manager.TEAM).attr(self.team, piece_type, Attribute.ARCHETYPE), 1.0)
                score -= 2 * piece_proportion * preference_weight

        return score

    def get_highest_piece_price(self):
        team_manager = self.get_manager(Manager.TEAM)
        buildable_pieces = team_manager.attr(self.team, PieceType.BARRACKS, Attribute.BUILDABLE_PIECES)

        # Find the highest cost buildable piece
        prices = [team_manager.attr(self.team, piece_type, Attribute.PRICE) for piece_type in buildable_pieces]
        return max(prices)

    # Return true if the specified coord is immediately harvestable (has an adjacent Colonist)
    def is_immediately_harvestable(self, coord):
        adjacent_colonists = [piece for piece in self.get_manager(Manager.PIECE).get_adjacent_pieces(coord[0], coord[1], self.team)
                              if piece.piece_type == PieceType.COLONIST]
        return len(adjacent_colonists) > 0

    def create_harvest_task(self, coord):
        task = Task(self.team, TaskType.HARVEST_RESOURCE, tx=coord[0], ty=coord[1], target=PieceType.GENERATOR)
        return task, self.personality.prioritize_task(task)

    def create_moveto_harvest_task(self, coord):
        task = Task(self.team, TaskType.MOVE_TO_RESOURCE, tx=coord[0], ty=coord[1])
        return task, self.personality.prioritize_task(task)

    def create_build_colonist_task(self):
        task = Task(self.team, TaskType.BUILD_PIECE, target=PieceType.COLONIST)
        return task, self.personality.prioritize_task(task)

    def create_build_barracks_task(self):
        task = Task(self.team, TaskType.BUILD_PIECE, target=PieceType.BARRACKS)
        return task, self.personality.prioritize_task(task)

    def create_build_techlab_task(self):
        task = Task(self.team, TaskType.BUILD_PIECE, target=PieceType.TECHLAB)
        return task, self.personality.prioritize_task(task)

    def create_research_task(self, upgrade_type):
        task = Task(self.team, TaskType.RESEARCH_UPGRADE, target=upgrade_type)
        return task, self.personality.prioritize_task(task)

    def create_attack_enemy_task(self, target):
        anticipated_x, anticipated_y = self.get_anticipated_movement(target)
        task = Task(self.team, TaskType.ATTACK_ENEMY, tx=anticipated_x, ty=anticipated_y, target=target)
        return task, self.personality.prioritize_task(task)

    def create_heal_task(self, injured):
        task = Task(self.team, TaskType.HEAL_SELF, target=injured)
        return task, self.personality.prioritize_task(task)

    def create_retreat_task(self, piece):
        bases = self.get_manager(Manager.PIECE).get_all_pieces_for_team(self.team, piece_type=PieceType.BASE)
        if len(bases) > 0:
            task = Task(self.team, TaskType.RETREAT, bases[0].gx, bases[0].gy, target=piece)
            return task, self.personality.prioritize_task(task)
        else:
            return None

    def create_terraforming_task(self, tile):
        task = Task(self.team, TaskType.TERRAFORM, tx=tile[0], ty=tile[1],
                    target=self.map.get_tile_type_at(tile[0], tile[1]))
        return task, self.personality.prioritize_task(task)

    def create_build_military_tasks(self):
        tasks = []
        counts_map = {}
        # Weight counts by personality
        for archetype, count in self.my_archetype_counts:
            counts_map[archetype] = count / self.personality.unit_preference[archetype]

        for archetype, count in self.enemy_archetype_counts:
            if count > 0 and len(self.enemy_pieces) > 0:
                # If the enemy has mainly one archetype, act like we have less of the counter unit than we do
                our_archetype = counter_archetype[archetype]
                counts_map[our_archetype] /= count / len(self.enemy_pieces)

        target_archetype = PieceArchetype.GROUND
        if len(counts_map.keys()) > 0:
            # Find the lowest count
            target_archetype, amount = min(counts_map.items(), key=lambda pair: pair[1])

        for piece_type in self.get_buildable_pieces(PieceType.BARRACKS, target_archetype):
            task = Task(self.team, TaskType.BUILD_PIECE, target=piece_type)
            tasks.append((task, self.personality.prioritize_task(task)))

        return tasks

    def create_terraforming_tasks(self, tiles):
        tasks = []
        tiles_to_terraform = set()
        piece_manager = self.get_manager(Manager.PIECE)

        bases = piece_manager.get_all_pieces_for_team(self.team, piece_type=PieceType.BASE)

        if len(bases) > 0 and len(tiles) > 0:
            base = bases[0]

            # Pick the tile closest to the base
            tile = min(tiles, key=lambda tile: abs(tile[0] - base.gx) + abs(tile[1] - base.gy))
            for terraform_tile in get_terraform_tiles((base.gx, base.gy), tile, self.map):
                tiles_to_terraform.add(terraform_tile)

        for tile in tiles_to_terraform:
            tasks.append(self.create_terraforming_task(tile))

        return tasks

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

    # Return a list of pieces we can build for this archetype
    def get_buildable_pieces(self, builder_type, piece_archetype):
        team_manager = self.get_manager(Manager.TEAM)
        buildable_at_barracks = team_manager.attr(self.team, builder_type, Attribute.BUILDABLE_PIECES)

        # Return all buildable pieces matching the archetype
        return [piece_type for piece_type in buildable_at_barracks
                if team_manager.attr(self.team, piece_type, Attribute.ARCHETYPE) == piece_archetype]

    # Create assignments for each task
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
                if newly_occupied_tiles is None:
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

        if task.task_type in [TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY, TaskType.TERRAFORM]:
            # Ranged units should issue attack orders instead of move orders when close enough to their target
            if piece.attr(Attribute.DAMAGE_TYPE) == DamageType.RANGED and \
                    task.task_type in [TaskType.ATTACK_ENEMY] and \
                    piece.attr(Attribute.MIN_RANGE) <= ranged_distance <= piece.attr(Attribute.MAX_RANGE):
                # Conduct a ranged attack on the target
                order = Option.MENU_RANGED_ATTACK
                tx = task.tx
                ty = task.ty
            # Terraforming orders should conduct the terraform action when adjacent
            elif task.task_type in [TaskType.TERRAFORM] and abs(piece.gx - task.tx) + abs(piece.gy - task.ty) <= 1:
                order = Option.MENU_RAISE_TILE if task.target == TileType.SEA else Option.MENU_LOWER_TILE
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
                    if len(valid_tiles) == 0:
                        # No possible valid destination! Just destroy ourselves
                        piece.set_order(Event(USEREVENT, {
                            'option': Option.MENU_DEMOLISH_SELF,
                        }))
                    else:
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

    # Begin planning the AI turn
    def begin_threaded_planning(self, event=None):
        thread = Thread(target=self.do_all_planning)
        thread.start()

    # Conduct preplanning and acting on that planning sequentially
    def do_all_planning(self, event=None):
        self.do_preplanning()
        self.act_on_planning()

    # Calculate what the world looks like right now
    def do_preplanning(self, event=None):
        self.is_thinking = True

        # Grok the board state, build some common aliases / queries
        self.parse_board_state()

        # Generate all potential tasks the AI might want to accomplish
        self.tasks = self.generate_tasks()

        # Generate assignments between tasks and pieces that can possibly execute the task
        self.assignments = self.assign_tasks(self.tasks)
        self.is_thinking = False

    # Act on planning and issue orders
    def act_on_planning(self, event=None):
        self.is_thinking = True

        # Confirm assignments in order of importance, issue concrete orders.
        assigned_pieces, assigned_tasks = self.confirm_assignments(self.assignments)

        # Pieces without orders should get out of the way of pieces with more important orders
        self.move_leftover_pieces(list(set(self.my_pieces) - set(assigned_pieces)))

        # Mark the turn as submitted so the game can progress when the player is ready
        self.get_manager(Manager.TEAM).set_turn_submitted(self.team)

        self.is_thinking = False
