from collections import defaultdict

class Season:
    def __init__(self, name='', user_id='', roster_id='', matchups=None, wins=0, losses=0, ties=0, made_playoffs=False, place=0, points_earned=0, points_against=0, points_possible=0):
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

    def __repr__(self):
        return f"{self.name}: {self.wins}-{self.losses}-{self.ties}"

    def get_record(self):
        record = f"{self.wins}-{self.losses}"
        if self.ties > 0:
            record += f"-{self.ties}"
        return record

    def get_season_accuracy(self):
        return round(self.points_earned / self.points_possible, 2)

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