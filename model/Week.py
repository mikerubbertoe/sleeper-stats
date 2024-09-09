class Week:
    def __init__(self, week=0, user="", max_score=0, actual_score=0, best_lineup=None, actual_lineup=None, matchup_id=0,
                 opponent=0, opponent_score=0, result=0, rank=0, thrown_week='', rush_tds=0, rec_tds=0):
        self.week = week
        self.user = user
        self.max_score = max_score
        self.actual_score = actual_score
        self.best_lineup = best_lineup
        self.actual_lineup = actual_lineup
        self.matchup_id = matchup_id
        self.opponent = opponent
        self.opponent_score = opponent_score
        self.result = result
        self.current_rank = rank
        self.thrown_week = thrown_week
        self.points_for_up_to_now = 0
        self.week_median = 0
        self.rush_tds = rush_tds
        self.rec_tds = rec_tds

    def __repr__(self):
        result = ''
        if self.result == 1:
            result = 'W'
        elif self.result == -1:
            result = 'L'
        else:
            result = 'T'
        return f"{self.user} week {self.week} ({result}): actual: {self.actual_score} max: {self.max_score}"

    def __str__(self):
        result = ''
        if self.result == 1:
            result = 'W'
        elif self.result == -1:
            result = 'L'
        else:
            result = 'T'
        return f"{self.user} week {self.week} ({result}): actual: {self.actual_score} max: {self.max_score}"

def set_thrown_week(team_1, team_2):
    if team_1.actual_score < team_2.actual_score:
        team_1.result = -1
        team_2.result = 1
        if team_1.max_score > team_2.actual_score:
            team_1.thrown_week = 'YES'
        else:
            team_1.thrown_week = 'NO'
    elif team_2.actual_score < team_1.actual_score:
        team_1.result = 1
        team_2.result = -1
        if team_2.max_score > team_1.actual_score:
            team_2.thrown_week = 'YES'
        else:
            team_2.thrown_week = 'NO'
    else:
        team_1.result = 0
        team_2.result = 0
        if team_1.max_score > team_2.actual_score:
            team_1.thrown_week = 'YES'
        else:
            team_1.thrown_week = 'NO'
        if team_2.max_score > team_1.actual_score:
            team_2.thrown_week = 'YES'
        else:
            team_2.thrown_week = 'NO'