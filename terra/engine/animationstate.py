from enum import Enum


# Common animation state constants for use in indexed AnimatedGameObjects.
class AnimationState(Enum):
    IDLE = 0
    MOVING = 1
