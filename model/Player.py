class Player:
    def __init__(self, name='', player_id='', points_scored=0.0, games_played=0, fantasy_positions=None, position_ranking=0):
        self.name = name
        self.player_id = player_id
        self.points_scored = points_scored
        self.games_played = games_played
        self.fantasy_positions = fantasy_positions
        self.position_ranking = position_ranking
        self.ppg = 0


    def __str__(self):
        return f'{self.name} - {self.points_scored}'

    def __repr__(self):
        return f'{self.name} - {self.points_scored}'
