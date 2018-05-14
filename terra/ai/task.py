from enum import Enum

from terra.economy.upgradeattribute import UpgradeAttribute
from terra.economy.upgrades import base_upgrades
from terra.piece.attribute import Attribute
from terra.piece.damagetype import DamageType
from terra.piece.piecearchetype import PieceArchetype
from terra.piece.piecesubtype import PieceSubtype
from terra.piece.piecetype import PieceType


# Possible tasks the AI will try to complete
class TaskType(Enum):
    # Econ
    MOVE_TO_RESOURCE = "Move to Resource"   # Step 1 in harvesting a resource-- moving to it
    HARVEST_RESOURCE = "Harvest Resource"   # Attempt to harvest the designated Resource tile
    BUILD_PIECE = "Build Piece"             # Attempt to build pieces
    RESEARCH_UPGRADE = "Research Upgrade"   # Research general upgrades
    TERRAFORM = "Terraform"                 # Terraform a tile

    # Combat
    ATTACK_ENEMY = "Attack Enemy"           # Attempt to intercept and attack an enemy unit
    DEFEND_TARGET = "Defend Area"           # TODO Attempt to defend a unit or area from enemies
    HEAL_SELF = "Heal Self"                 # Attempt to repair damage
    RETREAT = "Retreat"                     # Attempt to escape and move towards base


all_archetypes = [archetype for archetype in PieceArchetype]

# What piece archetypes are eligible for each task
task_type_to_piece_archetype = {
    TaskType.MOVE_TO_RESOURCE: [PieceArchetype.WORKER],
    TaskType.HARVEST_RESOURCE: [PieceArchetype.WORKER],
    TaskType.BUILD_PIECE: [PieceArchetype.WORKER, PieceArchetype.UTILITY],
    TaskType.RESEARCH_UPGRADE: [PieceArchetype.UTILITY],
    TaskType.TERRAFORM: [PieceArchetype.WORKER],

    TaskType.ATTACK_ENEMY: [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY],
    TaskType.DEFEND_TARGET: [PieceArchetype.GROUND, PieceArchetype.RANGED, PieceArchetype.MOBILITY],
    TaskType.HEAL_SELF: all_archetypes,
    TaskType.RETREAT: all_archetypes,
}

# Base task priority. If there's no preference from the AI personality, use this as base
base_task_priority = {
    TaskType.MOVE_TO_RESOURCE: 1.7,
    TaskType.HARVEST_RESOURCE: 1.8,
    TaskType.BUILD_PIECE: 1.6,
    TaskType.RESEARCH_UPGRADE: 1.5,
    TaskType.TERRAFORM: 1.5,

    TaskType.ATTACK_ENEMY: 1.8,
    TaskType.DEFEND_TARGET: 1.8,
    TaskType.HEAL_SELF: 2,
    TaskType.RETREAT: 2,
}

# How much to prioritize an enemy target. Higher number = more important
enemy_target_priority = {
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
        self.target_adjacent = task_type in [TaskType.HARVEST_RESOURCE, TaskType.MOVE_TO_RESOURCE,
                                             TaskType.RETREAT, TaskType.TERRAFORM]
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

    def requires_pathfinding(self):
        return self.task_type in [
            TaskType.MOVE_TO_RESOURCE,
            TaskType.ATTACK_ENEMY,
            TaskType.BUILD_PIECE,
            TaskType.TERRAFORM,
        ]

    # Return all pieces for this team that can work this task
    def get_eligible_pieces_for_task(self, piece_manager):
        pieces = []
        for archetype in task_type_to_piece_archetype[self.task_type]:
            pieces.extend(piece_manager.get_all_pieces_by_archetype(self.team, archetype))

        # Additional filtering
        if self.task_type == TaskType.HARVEST_RESOURCE:
            pieces = [piece for piece in pieces if piece in piece_manager.get_adjacent_pieces(self.tx, self.ty, self.team)]
        elif self.task_type in [TaskType.BUILD_PIECE]:
            pieces = [piece for piece in pieces if self.target in piece.attr(Attribute.BUILDABLE_PIECES)]
        elif self.task_type in [TaskType.RESEARCH_UPGRADE]:
            pieces = [piece for piece in pieces if self.target in piece.attr(Attribute.PURCHASEABLE_UPGRADES)]
        elif self.task_type in [TaskType.ATTACK_ENEMY]:
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
        elif self.task_type == TaskType.TERRAFORM:
            # Only pieces with the 'terraform' attribute can work on this task
            pieces = [piece for piece in pieces if piece.attr(Attribute.TERRAFORMING)]

        return pieces

    # Return a score for this task. Higher values means a lower priority
    def score_piece_for_task(self, piece, distance_map):
        if self.task_type in [TaskType.MOVE_TO_RESOURCE, TaskType.ATTACK_ENEMY, TaskType.TERRAFORM]:
            # Calculate the distance. This isn't 100% accurate (sometimes things are in the way) but it's good enough
            distance = abs(self.tx - piece.gx) + abs(self.ty - piece.gy)

            if self.task_type == TaskType.ATTACK_ENEMY and self.target:
                # Generally prioritize more important / dangerous targets, and targets we're strong against
                base_priority = enemy_target_priority[self.target.piece_archetype]
                multiplier = piece.attr(Attribute.ATTACK_MULTIPLIER)[self.target.piece_archetype]

                # Multipliers >= 1 mean we're even to favored against the target, so prioritize it
                # Otherwise, we should avoid conflict with those targets
                target_priority = -base_priority * multiplier * 2 if multiplier >= 1 else \
                    base_priority * (1 - multiplier)
            else:
                target_priority = 0

            score = distance + target_priority
            # Don't return an end_pos-- we're going to step along this path, not warp to it.
            # Set the end pos later when we pathfind to the destination.
            return score, []
        elif self.task_type in [TaskType.HARVEST_RESOURCE, TaskType.BUILD_PIECE]:
            if self.target in piece.attr(Attribute.BUILDABLE_PIECES):
                destinations = [tile for tile in piece.get_base_buildable_tiles()
                                if piece.can_build_piece_onto_tile(self.target, tile)]
                if len(destinations) > 0:
                    # Use the distance map to find the best position along the critical path
                    self.tx, self.ty = min(destinations, key=lambda tile: distance_map.get(tile, 999))
                    score = 1 if self.target == PieceType.COLONIST else 2
                    occupied_tiles = [(self.tx, self.ty)]
                    if piece.piece_subtype != PieceSubtype.BUILDING:
                        # Building coords are already marked as occupied
                        occupied_tiles.append((piece.gx, piece.gy))

                    return score, occupied_tiles
                else:
                    # No valid place to build this piece
                    return 99999, []
            else:
                # Can't build the desired piece at all
                return 99999, []
        elif self.task_type in [TaskType.HEAL_SELF]:
            # Prioritize based on how low health we are
            score = -10 * piece.hp / piece.attr(Attribute.MAX_HP)
            return score, [(piece.gx, piece.gy)]
        elif self.task_type in [TaskType.RESEARCH_UPGRADE]:
            # Evaluate based on piece type. Tech labs are highest priority, because they have no other tasks
            # competing for for its attention.
            return {
                PieceType.TECHLAB: 3,
                PieceType.BASE: 5,
                PieceType.BARRACKS: 7,
            }.get(piece.piece_type, 99999), []
        else:
            return 99999, []

    # Return how many resources this task will cost -this- turn
    def get_planned_spending(self, team_manager):
        if self.task_type in [TaskType.BUILD_PIECE]:
            return team_manager.attr(self.team, self.target, Attribute.PRICE)
        elif self.task_type in [TaskType.RESEARCH_UPGRADE]:
            return base_upgrades[self.target][UpgradeAttribute.UPGRADE_PRICE]
        elif self.task_type in [TaskType.HARVEST_RESOURCE]:
            return team_manager.attr(self.team, PieceType.GENERATOR, Attribute.PRICE)
        else:
            return 0


# An assignment between a task and a unit that will carry out that task.
# Contains a weighting that describes how accurate / strong of a pairing it is
class Assignment:
    def __init__(self, piece, task, value, end_pos=None):
        self.piece = piece
        self.task = task
        self.value = value

        # Motion planning for executing this assignment
        self.end_pos = end_pos if end_pos else []
        self.path = None

        # Motion planning for this particular assignment
        self.tx = self.task.tx
        self.ty = self.task.ty

    def __str__(self):
        return "{} with {}. Score: {}".format(self.piece, self.task, self.value)

    # Return a list of coords that will be occupied if this assignment is carried out
    def get_end_position(self, planned_occupied_coords):
        if self.task.requires_pathfinding() and len(self.end_pos) == 0:
            # Pathfind, taking into account the planned occupied coords
            destination = (self.tx, self.ty)
            min_range = 0
            max_range = 0

            if self.task.target_adjacent:
                min_range = 1
                max_range = 1
            elif self.piece.attr(Attribute.DAMAGE_TYPE) == DamageType.RANGED:
                min_range = self.piece.attr(Attribute.MIN_RANGE)
                max_range = self.piece.attr(Attribute.MAX_RANGE)

            path = self.piece.get_path_to_target(destination, planned_occupied_coords, min_range, max_range,
                                                 self.piece.attr(Attribute.MOVEMENT_TYPE))

            if path:
                # Step along the path and modify the destination to be the furthest we can go along this path
                self.tx, self.ty = self.piece.step_along_path(path, planned_occupied_coords)
                return [(self.tx, self.ty)]
            else:
                # Return None to indicate no path
                return None
        else:
            return self.end_pos
