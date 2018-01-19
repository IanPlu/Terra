from terra.engine.gameobject import GameObject


# Contains and manages all resources and upgrades for all teams
class TeamManager(GameObject):
    def __init__(self, battle, teams):
        super().__init__()

        self.battle = battle
        self.teams = teams

        self.carbon = {}
        self.minerals = {}
        self.gas = {}
        self.upgrades = {}

        # Initialize resources and upgrades for each team provided
        for team in self.teams:
            self.carbon[team] = 0
            self.minerals[team] = 0
            self.gas[team] = 0
            self.upgrades = []

    def __str__(self):
        return_string = ""
        for team in self.teams:
            return_string = return_string + "{} team with {} carbon, {} minerals, and {} gas.\n"\
                .format(team, self.carbon[team], self.minerals[team], self.gas[team])
        return return_string

    def add_resources(self, team, new_resources):
        self.carbon[team] = self.carbon[team] + new_resources[0]
        self.minerals[team] = self.minerals[team] + new_resources[1]
        self.gas[team] = self.gas[team] + new_resources[2]
