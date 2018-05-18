from random import uniform
from enum import Enum

from terra.ai.task import TaskType, base_task_priority
from terra.piece.piecearchetype import PieceArchetype


# Aliases for personality types, and the associated method to create them
class PersonalityType(Enum):
    DEFAULT = 0
    AGGRESSIVE = 1
    DEFENSIVE = 2
    BERSERKER = 3
    BUILDER = 4
    TECHER = 5
    RANDOM = 6


# Container for AI 'personality'. Controls thresholds for various behavior, how aggressive / defensive to act, etc.
#   * Aggressive - How likely this AI is to take offensive actions
#   * Defensive - How likely this AI is to take defensive actions
#   * Constructive - How likely this AI is to build and expand
#   * Scientific - How likely this AI is to research new upgrades
#   * Retreat Threshold - What health percentage this AI will start ordering units to retreat
#   * Unit Preference - How much this AI favors specific piece archetypes. e.x.: {PieceArchetype.GROUND: 1.0}
#   * Research to Consider - How many research items to consider each round
class Personality:
    def __init__(self, personality_type=PersonalityType.DEFAULT, aggressive=1.0, defensive=1.0, constructive=1.0,
                 scientific=1.0, retreat_threshold=0.6, unit_preference=None, research_to_consider=3, new_unit_tier_priority=3):
        self.personality_type = personality_type
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

    # Return a priority score for a task, based on our personality
    # Higher numbers are more important
    def prioritize_task(self, task):
        personal_priority = {
            TaskType.MOVE_TO_RESOURCE: self.constructive,
            TaskType.HARVEST_RESOURCE: self.constructive,
            TaskType.BUILD_PIECE: self.constructive,
            TaskType.RESEARCH_UPGRADE: self.scientific,
            TaskType.MINE: self.constructive,

            TaskType.ATTACK_ENEMY: self.aggressive,
            TaskType.DEFEND_TARGET: self.defensive,
            TaskType.HEAL_SELF: self.defensive,
            TaskType.RETREAT: self.defensive,
        }.get(task.task_type, 1)

        return personal_priority * base_task_priority.get(task.task_type, 1)


# Create a default balanced personality.
def create_default_personality():
    return Personality()


# Create an aggressive personality that favors aggressive actions and doesn't retreat often
def create_aggressive_personality():
    return Personality(
        personality_type=PersonalityType.AGGRESSIVE,
        aggressive=1.5,
        defensive=0.65,
        retreat_threshold=0.4
    )


# Create a defensive personality that favors defensive actions and retreating for healing
def create_defensive_personality():
    return Personality(
        personality_type=PersonalityType.DEFENSIVE,
        aggressive=0.65,
        defensive=1.5,
        constructive=1.1,
        retreat_threshold=0.8
    )


# Create a hyper-aggressive personality that never retreats and rarely defends
def create_berserker_personality():
    return Personality(
        personality_type=PersonalityType.BERSERKER,
        aggressive=2.0,
        defensive=0.2,
        retreat_threshold=0.0,
        scientific=0.0,
    )


# Create an AI that just wants to build neat stuff
def create_builder_personality():
    return Personality(
        personality_type=PersonalityType.BUILDER,
        aggressive=0.5,
        defensive=0.5,
        constructive=2.0,
        scientific=2.0,
    )


# Create an AI that wants to reach new unit tiers quickly and win by having better teched units
def create_fast_techer_personality():
    return Personality(
        personality_type=PersonalityType.TECHER,
        aggressive=0.8,
        defensive=1.2,
        constructive=1.1,
        scientific=2.5,
        new_unit_tier_priority=10
    )


# Create a completely random AI within the provided thresholds
def create_chaotic_personality(lower=0.0, upper=2.0):
    return Personality(
        personality_type=PersonalityType.RANDOM,
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


# Map of personality types to methods that will create that type
personality_method = {
    PersonalityType.DEFAULT: create_default_personality,
    PersonalityType.AGGRESSIVE: create_aggressive_personality,
    PersonalityType.DEFENSIVE: create_defensive_personality,
    PersonalityType.BERSERKER: create_berserker_personality,
    PersonalityType.BUILDER: create_builder_personality,
    PersonalityType.TECHER: create_fast_techer_personality,
    PersonalityType.RANDOM: create_chaotic_personality,
}
