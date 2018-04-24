

# Container for AI 'personality'. Controls thresholds for various behavior, how aggressive / defensive to act, etc.
#   * Aggressive - How likely this AI is to take offensive actions
#   * Defensive - How likely this AI is to take defensive actions
#   * Constructive - How likely this AI is to build and expand
#   * Retreat Threshold - What health percentage this AI will start ordering units to retreat
class Personality:
    def __init__(self, aggressive=1.0, defensive=1.0, constructive=1.0, retreat_threshold=0.6,
                 ground_weight=1.0, ranged_weight=1.0, mobility_weight=1.0):
        self.aggressive = aggressive
        self.defensive = defensive
        self.constructive = constructive
        self.retreat_threshold = retreat_threshold

        self.ground_weight = ground_weight
        self.ranged_weight = ranged_weight
        self.mobility_weight = mobility_weight


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
        retreat_threshold=0.0
    )