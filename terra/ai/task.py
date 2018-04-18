from enum import Enum
from terra.piece.piecearchetype import PieceArchetype
from terra.ai.pathfinder import get_path_to_destination
from terra.piece.attribute import Attribute


# Possible tasks the AI will try to complete
class TaskType(Enum):
    # Econ
    HARVEST_RESOURCE = "Harvest Resource"   # Attempt to harvest the designated Resource tile
    BUILD_BARRACKS = "Build Barracks"       # Attempt to build barracks near the designated area
    BUILD_UNIT = "Build Unit"               # Attempt to build units
    RESEARCH_UPGRADE = "Research Upgrade"   # Research general unit upgrades
    RESEARCH_NEW_UNIT = "Research Units"    # Research new unit types

    # Combat
    ATTACK_ENEMY = "Attack Enemy"           # Attempt to intercept and attack an enemy unit
    DEFEND_AREA = "Defend Area"             # Attempt to defend an area from enemies
    DESTROY_BUILDING = "Destroy Building"   # Attempt to destroy an enemy building


task_type_to_piece_archetype = {
    TaskType.HARVEST_RESOURCE: [PieceArchetype.WORKER]
}


# An instance of a task.
# Contains extra details about the task
class Task:
    def __init__(self, team, task_type, tx=None, ty=None):
        self.team = team
        self.task_type = task_type
        self.tx = tx
        self.ty = ty

        # True if this task type should be navigating to tiles adjacent to the target
        self.target_adjacent = task_type in [TaskType.HARVEST_RESOURCE]

    def __str__(self):
        base = "{} task".format(self.task_type.value)
        # 0 is an acceptable value, so check explicitly for None
        if self.tx is not None and self.ty is not None:
            base += " on tile ({}, {})".format(self.tx, self.ty)
        return base

    # Return all pieces for this team that can work this task
    def get_eligible_pieces_for_task(self, piece_manager):
        pieces = []
        for archetype in task_type_to_piece_archetype[self.task_type]:
            pieces.extend(piece_manager.get_all_pieces_by_archetype(self.team, archetype))
        return pieces

    # Return a score for this task
    def score_piece_for_task(self, piece, map):
        if self.tx is not None and self.ty is not None:
            if self.target_adjacent:
                destinations = map.get_valid_adjacent_tiles_for_movement_type(self.tx, self.ty,
                                                                              piece.attr(Attribute.MOVEMENT_TYPE))
            else:
                destinations = [(self.tx, self.ty)]

            path = piece.get_path_to_destinations(destinations)
            if path:
                # Return the length of the path
                return len(path)
            else:
                # Piece can't possibly reach the destination
                return 99999
        else:
            # TODO: Other heuristics
            return 99999


# An assignment between a task and a unit that will carry out that task.
# Contains a weighting that describes how accurate / strong of a pairing it is
class Assignment:
    def __init__(self, piece, task, value):
        self.piece = piece
        self.task = task
        self.value = value

    def __str__(self):
        return "{} with {}. Score: {}".format(self.piece, self.task, self.value)
