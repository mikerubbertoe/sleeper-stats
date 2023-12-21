class OpponentSeason:
    def __init__(self, season="", name="", matchups=None, wins=0, losses=0, ties=0, playoffs_made=False):
        self.season = season
        self.name = name
        self.matchups = matchups
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.playoffs_made = playoffs_made

    def get_record(self):
        record = f"{self.wins}-{self.losses}"
        if self.ties > 0:
            record += f"-{self.ties}"
        return record
