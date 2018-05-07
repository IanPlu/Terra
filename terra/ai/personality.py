from terra.piece.piecearchetype import PieceArchetype
from random import uniform


# Container for AI 'personality'. Controls thresholds for various behavior, how aggressive / defensive to act, etc.
#   * Aggressive - How likely this AI is to take offensive actions
#   * Defensive - How likely this AI is to take defensive actions
#   * Constructive - How likely this AI is to build and expand
#   * Scientific - How likely this AI is to research new upgrades
#   * Retreat Threshold - What health percentage this AI will start ordering units to retreat
#   * Unit Preference - How much this AI favors specific piece archetypes. e.x.: {PieceArchetype.GROUND: 1.0}
#   * Research to Consider - How many research items to consider each round
class Personality:
    def __init__(self, aggressive=1.0, defensive=1.0, constructive=1.0, scientific=1.0, retreat_threshold=0.6,
                 unit_preference=None, research_to_consider=3, new_unit_tier_priority=3):
        self.aggressive = aggressive
        self.defensive = defensive
        self.constructive = constructive
        self.scientific = scientific
        self.retreat_threshold = retreat_threshold
        self.research_to_consider = research_to_consider
        self.new_unit_tier_priority = new_unit_tier_priority

        self.unit_preference = unit_preference if unit_preference else {}

        # Fill in unspecified archetypes
        for archetype in PieceArchetype:
            if not self.unit_preference.get(archetype, None):
                self.unit_preference[archetype] = 1.0


# Create a default balanced personality.
def create_default_personality():
    return Personality()


# Create an aggressive personality that favors aggressive actions and doesn't retreat often
def create_aggressive_personality():
    return Personality(
        aggressive=1.5,
        defensive=0.65,
        retreat_threshold=0.4
    )


# Create a defensive personality that favors defensive actions and retreating for healing
def create_defensive_personality():
    return Personality(
        aggressive=0.65,
        defensive=1.5,
        constructive=1.1,
        retreat_threshold=0.8
    )


# Create a hyper-aggressive personality that never retreats and rarely defends
def create_berserker_personality():
    return Personality(
        aggressive=2.0,
        defensive=0.2,
        retreat_threshold=0.0,
        scientific=0.0,
    )


# Create an AI that just wants to build neat stuff
def create_builder_personality():
    return Personality(
        aggressive=0.5,
        defensive=0.5,
        constructive=2.0,
        scientific=2.0,
    )


# Create an AI that wants to reach new unit tiers quickly and win by having better teched units
def create_fast_techer_personality():
    return Personality(
        aggressive=0.8,
        defensive=1.2,
        constructive=1.1,
        scientific=2.5,
        new_unit_tier_priority=10
    )


# Create a completely random AI within the provided thresholds
def create_chaotic_personality(lower=0.0, upper=2.0):
    return Personality(
        aggressive=uniform(lower, upper),
        defensive=uniform(lower, upper),
        constructive=uniform(lower, upper),
        scientific=uniform(lower, upper),
        retreat_threshold=uniform(lower, upper),
        unit_preference={
            PieceArchetype.GROUND: uniform(lower, upper),
            PieceArchetype.RANGED: uniform(lower, upper),
            PieceArchetype.MOBILITY: uniform(lower, upper),
            PieceArchetype.WORKER: uniform(lower, upper),
            PieceArchetype.GENERATOR: uniform(lower, upper),
            PieceArchetype.UTILITY: uniform(lower, upper),
        }
    )