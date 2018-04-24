from enum import Enum

from terra.piece.attribute import Attribute
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType


# Possible tasks the AI will try to complete
class TaskType(Enum):
    # Econ
    MOVE_TO_RESOURCE = "Move to Resource"   # x Step 1 in harvesting a resource-- moving to it
    HARVEST_RESOURCE = "Harvest Resource"   # x Attempt to harvest the designated Resource tile
    BUILD_BARRACKS = "Build Barracks"       # Attempt to build barracks near the designated area
    BUILD_UNIT = "Build Unit"               # Attempt to build units
    RESEARCH_UPGRADE = "Research Upgrade"   # Research general unit upgrades
    RESEARCH_NEW_UNIT = "Research Units"    # Research new unit types

    # Combat
    ATTACK_ENEMY = "Attack Enemy"           # / Attempt to intercept and attack an enemy unit
    DEFEND_AREA = "Defend Area"             # Attempt to defend an area from enemies
    DESTROY_BUILDING = "Destroy Building"   # Attempt to destroy an enemy building
    HEAL_SELF = "Heal Self"                 # x Attempt to repair damage
    RETREAT = "Retreat"                     # x Attempt to escape and move towards base


all_archetypes = [archetype for archetype in PieceArchetype]

task_type_to_piece_archetype = {
    TaskType.MOVE_TO_RESOURCE: [PieceArchetype.WORKER],
    TaskType.HARVEST_RESOURCE: [PieceArchetype.WORKER],
    TaskType.BUILD_BARRACKS: [PieceArchetype.WORKER],
    TaskType.BUILD_UNIT: [PieceArchetype.UTILITY],
    TaskType.RESEARCH_UPGRADE: [PieceArchetype.UTILITY],
    TaskType.RESEARCH_NEW_UNIT: [PieceArchetype.UTILITY],

    TaskType.ATTACK_ENEMY: [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY],
    TaskType.DEFEND_AREA: [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY],
    TaskType.DESTROY_BUILDING: [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY],
    TaskType.HEAL_SELF: all_archetypes,
    TaskType.RETREAT: all_archetypes,
}

# How much to prioritize an enemy target. Higher number = more important
enemy_target_priority = {
    # TODO: Make BASE pieces their own archetype
    PieceArchetype.UTILITY: 1,
    PieceArchetype.GENERATOR: 1,
    PieceArchetype.WORKER: 2,
    PieceArchetype.GROUND: 3,
    PieceArchetype.RANGED: 3,
    PieceArchetype.MOBILITY: 3,
}


# An instance of a task.
# Contains extra details about the task
class Task:
    def __init__(self, team, task_type, tx=None, ty=None, target=None):
        self.team = team
        self.task_type = task_type
        self.tx = tx
        self.ty = ty

        self.target = target

        # True if this task type should be navigating to tiles adjacent to the target
        self.target_adjacent = task_type in [TaskType.HARVEST_RESOURCE, TaskType.MOVE_TO_RESOURCE, TaskType.RETREAT]
        # True if this task type should allow any number of pieces to be assigned to it
        self.allow_multiple_assignments = task_type in [TaskType.ATTACK_ENEMY]

    def __str__(self):
        base = "{} task".format(self.task_type.value)
        if self.target is not None:
            base += " with target {}".format(self.target)
        # 0 is an acceptable value, so check explicitly for None
        elif self.tx is not None and self.ty is not None:
            base += " on tile ({}, {})".format(self.tx, self.ty)
        return base

    # Return all pieces for this team that can work this task
    def get_eligible_pieces_for_task(self, piece_manager):
        pieces = []
        for archetype in task_type_to_piece_archetype[self.task_type]:
            pieces.extend(piece_manager.get_all_pieces_by_archetype(self.team, archetype))

        # Additional filtering
        if self.task_type == TaskType.HARVEST_RESOURCE:
            pieces = [piece for piece in pieces if piece in piece_manager.get_adjacent_pieces(self.tx, self.ty, self.team)]
        elif self.task_type in [TaskType.BUILD_UNIT]:
            pieces = [piece for piece in pieces if self.target in piece.attr(Attribute.BUILDABLE_PIECES)]
        elif self.task_type == TaskType.ATTACK_ENEMY:
            # Filter out pieces that can't attack this target
            eligible_pieces = []
            targets = piece_manager.get_enemy_pieces_at(self.tx, self.ty, self.team)
            # TODO: This is real ugly. Streamline and improve
            if len(targets) > 0:
                for piece in pieces:
                    for target in targets:
                        if not (piece.attr(Attribute.CANT_ATTACK_BUILDINGS) and target.attr(Attribute.SUBTYPE) == PieceSubtype.BUILDING):
                            eligible_pieces.append(piece)

            pieces = eligible_pieces
        elif self.task_type == TaskType.HEAL_SELF:
            # Only the target piece can work on this task
            pieces = [self.target]

        return pieces

    # Return a score for this task. Higher values means a lower priority
    def score_piece_for_task(self, piece, map):
        if self.task_type in [TaskType.HARVEST_RESOURCE, TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY]:
            if self.target_adjacent:
                destinations = map.get_valid_adjacent_tiles_for_movement_type(self.tx, self.ty,
                                                                              piece.attr(Attribute.MOVEMENT_TYPE))
            else:
                destinations = [(self.tx, self.ty)]

            path = piece.get_path_to_destinations(destinations)
            path_length = len(path) if path else 9999

            target_priority = 0
            if self.task_type == TaskType.ATTACK_ENEMY and self.target:
                # Generally prioritize more important / dangerous targets, and targets we're strong against
                base_priority = enemy_target_priority[self.target.piece_archetype]
                multiplier = piece.attr(Attribute.ATTACK_MULTIPLIER)[self.target.piece_archetype]

                # Multipliers >= 1 mean we're even to favored against the target, so prioritize it
                # Otherwise, we should avoid conflict with those targets
                target_priority = -base_priority * multiplier * 2 if multiplier >= 1 else \
                    base_priority * (1 - multiplier)

            return path_length + target_priority
        elif self.task_type in [TaskType.BUILD_UNIT]:
            if self.target in piece.attr(Attribute.BUILDABLE_PIECES):
                destinations = [tile for tile in piece.get_base_buildable_tiles()
                                if piece.can_build_piece_onto_tile(self.target, tile)]
                if len(destinations) > 0:
                    self.tx, self.ty = destinations[0]
                    return 1 if self.target == PieceType.COLONIST else 2
                else:
                    # No valid place to build this piece
                    return 99999
            else:
                # Can't build the desired piece
                return 99999
        elif self.task_type in [TaskType.HEAL_SELF]:
            # Prioritize based on how low health we are
            return -10 * piece.hp / piece.attr(Attribute.MAX_HP)
        else:
            return 99999

    # Return how many resources this task will cost -this- turn
    def get_planned_spending(self, team_manager):
        if self.task_type in [TaskType.BUILD_UNIT]:
            return team_manager.attr(self.team, self.target, Attribute.PRICE)
        elif self.task_type in [TaskType.HARVEST_RESOURCE]:
            return team_manager.attr(self.team, PieceType.GENERATOR, Attribute.PRICE)
        else:
            return 0


# An assignment between a task and a unit that will carry out that task.
# Contains a weighting that describes how accurate / strong of a pairing it is
class Assignment:
    def __init__(self, piece, task, value, end_pos=None, path=None):
        self.piece = piece
        self.task = task
        self.value = value

        # Optional. Motion planning for executing this assignment
        self.end_pos = end_pos
        self.path = path

    def __str__(self):
        return "{} with {}. Score: {}".format(self.piece, self.task, self.value)
