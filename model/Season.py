from collections import defaultdict

class Season:
    def __init__(self, name='', user_id='', roster_id='', matchups=None, wins=0, losses=0, ties=0, made_playoffs=False,
                 place=0, points_earned=0, points_against=0, points_possible=0):
        if matchups is None:
            matchups = list()
        self.name = name
        self.user_id = user_id
        self.roster_id = roster_id
        self.matchups = matchups
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.made_playoffs = made_playoffs
        self.place = place
        self.points_earned = points_earned
        self.points_against = points_against
        self.points_possible = points_possible
        self.playoff_result = 0
        self.reception_tds = 0
        self.rush_tds = 0
        self.rostered_players = {}

    def __repr__(self):
        return f"{self.name}: {self.wins}-{self.losses}-{self.ties}"

    def get_record(self):
        record = f"{self.wins}-{self.losses}"
        if self.ties > 0:
            record += f"-{self.ties}"
        return record

    def get_season_accuracy(self):
        return round(self.points_earned / self.points_possible, 2)

    def update_all_rostered_player_rankings_and_ppg(self, sleeper):

        for k, v in self.rostered_players.items():
            player_position = v.fantasy_positions[0]
            position_rank = 0
            try:
                position_rank = sleeper.player_position_scores_current_format[player_position].index(k) + 1
            except ValueError:
                position_rank = 999
            v.position_ranking = position_rank
            v.ppg = round(v.points_scored / v.games_played, 2) if v.games_played > 0 else 0

    def get_top_players_for_user(self, num_top_players):
        sorted_players = [k for k in sorted(self.rostered_players.values(),
                          key=lambda player: player.points_scored, reverse=True)]
        top_players = sorted_players[:num_top_players]

        return top_players

def get_season_rankings(seasons):
    seeding = []
    for k, user in seasons.items():
        added = False
        for i in range(len(seeding)):
            opponent = seasons[seeding[i]]
            if user.wins > seasons[seeding[i]].wins or (
                    user.wins == opponent.wins and user.points_earned > opponent.points_earned):
                seeding.insert(i, k)
                added = True
                break
        if not added:
            seeding.append(k)
    return seeding

def get_original_season_rankings(rosters):
    seeding = []
    for roster in rosters.values():
        wins = roster['settings']['wins']
        losses = roster['settings']['losses']
        ties = roster['settings']['ties']
        points_earned = roster['settings']['fpts'] + (roster['settings']['fpts_decimal'] / 100)
        added = False
        for i in range(len(seeding)):
            opponent = seeding[i]
            if wins > opponent[1] or (wins == opponent[1] and points_earned > opponent[4]):
                seeding.insert(i, (roster['roster_id'], wins, losses, ties, points_earned))
                added = True
                break
        if not added:
            seeding.append((roster['roster_id'], wins, losses, ties, points_earned))

    return [s[0] for s in seeding]
def get_weekly_rankings(seasons, week):
    seeding = []
    for k, user in seasons.items():
        added = False
        for i in range(len(seeding)):
            opponent = seasons[seeding[i]]
            if user.matchups[week - 1].place < opponent.matchups[week - 1].place:
                seeding.insert(i, k)
                added = True
                break
        if not added:
            seeding.append(k)
    return seeding

def get_record_up_to_week(seasons, week, wins_above_median_active):
    partial_records = defaultdict(Season)
    for i in range(week):
        for k, user in seasons.items():
            user_result = user.matchups[i].result
            if user_result > 0:
                partial_records[k].wins += 1
            elif user_result < 0:
                partial_records[k].losses += 1
            else:
                partial_records[k].ties += 1

            if wins_above_median_active:
                week_median = user.matchups[i].week_median
                week_score = user.matchups[i].actual_score
                if week_score > week_median:
                    partial_records[k].wins += 1
                elif week_score < week_median:
                    partial_records[k].losses += 1
                else:
                    partial_records[k].ties += 1
    for k, v in partial_records.items():
        partial_records[k] = v.get_record()
    return partial_records

def update_players_played_rankings(seasons, player_rankings):
    for user in seasons:
        for player in user.players_played:
            if player.fantasy_positions is None:
                continue
            position = player.fantasy_positions[0]
            final_rank = player_rankings[position].index(player.player_id) + 1
            player.position_ranking = final_rank