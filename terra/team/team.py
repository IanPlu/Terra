from enum import Enum


# Possible teams in the battle.
class Team(Enum):
    RED = "[RED]"
    BLUE = "[BLU]"
    GREEN = "[GRN]"
    YELLOW = "[YLO]"
    # Not a playable team. Neutral units & when we don't have a team yet for network games
    NONE = "[NON]"
