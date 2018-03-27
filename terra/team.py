from enum import Enum


# Possible teams in the battle.
class Team(Enum):
    RED = "[RED]"
    BLUE = "[BLU]"
    GREEN = "[GRN]"
    YELLOW = "[YLO]"
    # Only used when setting up network games, when we don't HAVE a team yet
    NONE = "[NON]"
