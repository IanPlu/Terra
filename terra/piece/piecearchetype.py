from enum import Enum, auto


# Possible piece classes or archetypes.
class PieceArchetype(Enum):
    # Unit archetypes
    WORKER = auto()
    GROUND = auto()
    RANGED = auto()
    MOBILITY = auto()

    # Building archetypes
    GENERATOR = auto()
    UTILITY = auto()
