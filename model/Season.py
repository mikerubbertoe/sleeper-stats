class Season:
    def __init__(self, name='', user_id='', matchups=None, wins=0, losses=0, ties=0, made_playoffs=False, points_earned=0, points_against=0, points_possible=0):
        self.name = name
        self.user_id = user_id
        self.matchups = matchups
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.made_playoffs = made_playoffs
        self.points_earned = points_earned
        self.points_against = points_against
        self.points_possible = points_possible

    def __repr__(self):
        return f"{self.name}: {self.wins}-{self.losses}-{self.ties}"

    def get_record(self):
        record = f"{self.wins}-{self.losses}"
        if self.ties > 0:
            record += f"-{self.ties}"
        return record

    def get_season_accuracy(self):
        return round(self.points_earned / self.points_possible, 2)