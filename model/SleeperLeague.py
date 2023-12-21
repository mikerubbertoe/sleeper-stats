import sleeper_wrapper as Sleeper

class SleeperLeague:
    def __init__(self, league_id=-1):
        self.league_id = league_id
        self.players = Sleeper.Players()
        self.stats = Sleeper.Stats()
        self.league = Sleeper.League(league_id)
        self.numQB   = self.league.get_league()['roster_positions'].count('QB')
        self.numRB   = self.league.get_league()['roster_positions'].count('RB')
        self.numWR   = self.league.get_league()['roster_positions'].count('WR')
        self.numTE   = self.league.get_league()['roster_positions'].count('TE')
        self.numFlex = self.league.get_league()['roster_positions'].count('FLEX')
        self.numK    = self.league.get_league()['roster_positions'].count('K')
        self.numDST  = self.league.get_league()['roster_positions'].count('DST')
        self.allPlayers = self.players.get_all_players()
        self.users = self.league.get_users()
        self.rosters = self.league.get_rosters()

    def get_all_players(self):
        return self.allPlayers

    def get_all_users(self):
        users = dict()
        for user in self.users:
            users[user['user_id']] = user
        return users

    def get_all_rosters(self):
        rosters = dict()
        for roster in self.rosters:
            rosters[roster['roster_id']] = roster
        return rosters
