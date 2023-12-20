import sleeper_wrapper as Sleeper

class Week:
    def __init__(self, week=0, user="", max_score=0, actual_score=0, best_lineup=None, actual_lineup=None, matchup_id=0, opponent=0):
        self.week = week
        self.user = user
        self.max_score = max_score
        self.actual_score = actual_score
        self.best_lineup = best_lineup
        self.actual_lineup = actual_lineup
        self.matchup_id = matchup_id
        self.opponent = opponent

    def __repr__(self):
        return f"{self.user} week {self.week}: actual: {self.actual_score} max: {self.max_score}"


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