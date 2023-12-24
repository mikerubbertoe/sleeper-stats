class Week:
    def __init__(self, week=0, user="", max_score=0, actual_score=0, best_lineup=None, actual_lineup=None, matchup_id=0, opponent=0, opponent_score=0, result=0, rank=0):
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
    def __repr__(self):
        return f"{self.user} week {self.week}: actual: {self.actual_score} max: {self.max_score}"
