from io import StringIO

from terra.engine.gameobject import GameObject
from terra.event.event import EventType
from terra.managers.session import Manager
from terra.resources.assetloading import get_asset, AssetType
from terra.map.maputils import get_loadable_maps


# Manager for campaign progress. Reads / writes to the campaign data file.
class CampaignManager(GameObject):
    def __init__(self):
        super().__init__()

    def register_handlers(self, event_bus):
        super().register_handlers(event_bus)

        event_bus.register_handler(EventType.E_BATTLE_OVER, self.handle_battle_end)

    def handle_battle_end(self, event):
        team_manager = self.get_manager(Manager.TEAM)
        if len(team_manager.teams) == 1 and team_manager.teams[0] == self.get_manager(Manager.PLAYER).active_team:
            # Mark campaign progress
            save_campaign_progress(self.get_map_name())


# Return a list of completed campaign maps from the progress file
def load_campaign_progress():
    try:
        progress_path = get_asset(AssetType.ATTRIBUTES, "campaign.cfg")
        progress = []

        with open(progress_path) as progress_file:
            lines = progress_file.read()
            for line in StringIO(lines):
                # Format: <mapname>
                values = line.rstrip().split(' ')
                if len(values) == 1:
                    progress.append(values[0])
        return progress
    except (IOError, KeyError) as e:
        print("Unable to load campaign file. Exception: {}".format(e))


# Record that a map has been cleared
def save_campaign_progress(map_name):
    all_maps = get_loadable_maps(AssetType.CAMPAIGN_MAP)
    progress = load_campaign_progress()

    # Trim the map name if necessary (.sav -> .map)
    if map_name.endswith(".sav"):
        map_name = map_name[:-4] + ".map"

    # Update the progress structure
    if map_name in all_maps:
        progress.append(map_name)

    # Make the items unique
    progress = list(set(progress))

    # Serialize and save the progress structure back to the file
    try:
        progress_path = get_asset(AssetType.ATTRIBUTES, "campaign.cfg")

        with open(progress_path, 'w') as progress_file:
            for mapname in progress:
                progress_file.write("{}\n".format(mapname))
    except IOError as e:
        print("Unable to save campaign file. Exception: {}".format(e))


# Return a list
def get_open_maps():
    all_maps = get_loadable_maps(AssetType.CAMPAIGN_MAP)
    completed_maps = load_campaign_progress()

    num_completed = len(completed_maps)
    num_available = min(len(all_maps), num_completed + 2)

    return all_maps[:num_available]
