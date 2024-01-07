import sleeper_wrapper as Sleeper
from model.ScoringFormat import ScoringFormat
class SleeperLeague:
    def __init__(self, league_id=-1):
        self.league_id = league_id
        self.players = Sleeper.Players()
        self.stats = Sleeper.Stats()
        self.league_object = Sleeper.League(league_id)
        self.league = Sleeper.League(league_id).get_league()
        self.users = Sleeper.League(league_id).get_users()
        self.rosters = Sleeper.League(league_id).get_rosters()
        self.numQB   = self.league['roster_positions'].count('QB')
        self.numRB   = self.league['roster_positions'].count('RB')
        self.numWR   = self.league['roster_positions'].count('WR')
        self.numTE   = self.league['roster_positions'].count('TE')
        self.numFlex = self.league['roster_positions'].count('FLEX')
        self.numK    = self.league['roster_positions'].count('K')
        self.numDST  = self.league['roster_positions'].count('DST')
        self.allPlayers = self.players.get_all_players()
        self.scoring_format = ScoringFormat(new_rules=self.league['scoring_settings'])
        self.scoring_format_name = self.get_scoring_type()
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

    def get_scoring_type(self):
        if self.scoring_format.__getattribute__('rec') == 1.0:
            return 'PPR'
        if (self.scoring_format.__getattribute__('rec') == 0.5) and (self.scoring_format.__getattribute__('rec_fd') == 0.5):
            return "HALF PPR & HALF PPFD"
        if self.scoring_format.__getattribute__('rec') == 0.5:
            return "HALF PPR"
        if self.scoring_format.__getattribute__('rec_fd') == 1.0:
            return "PPFD"
        if self.scoring_format.__getattribute__('rec_fd') == 0.5:
            return "HALF PPFD"
        if self.scoring_format.__getattribute__('rec') == 0.0:
            return "STD"
        return "CUSTOM"