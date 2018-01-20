from terra.constants import Team
from terra.economy.resourcetypes import ResourceType


# Base resource yield tables.
base_resource_yields = {
    ResourceType.CARBON: 10,
    ResourceType.MINERALS: 10,
    ResourceType.GAS: 10
}

# Actual up to date resource yield tables, specific to each team.
# Upgrades can mutate this value over the course of the game.
resource_yields = {}

# Propagate base values to each team
for team in Team:
    resource_yields[team] = base_resource_yields
