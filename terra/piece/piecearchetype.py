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


# Map of archetype to the archetype that counters it
counter_archetype = {
    PieceArchetype.WORKER: PieceArchetype.MOBILITY,
    PieceArchetype.GROUND: PieceArchetype.RANGED,
    PieceArchetype.RANGED: PieceArchetype.MOBILITY,
    PieceArchetype.MOBILITY: PieceArchetype.GROUND,

    PieceArchetype.GENERATOR: PieceArchetype.GROUND,
    PieceArchetype.UTILITY: PieceArchetype.RANGED,
}
