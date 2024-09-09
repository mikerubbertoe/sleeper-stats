class DraftPlayer:
    def __init__(self, position='', name='', drafted_as=0, drafted_by='', points_scored=0.0, position_rank=0,
                 player_id='', pick_number=0, is_keeper=False, draft_position=0, round=0):
        self.position = position
        self.name = name
        self.drafted_as = drafted_as
        self.drafted_by = drafted_by
        self.points_scored = points_scored
        self.position_rank = position_rank
        self.player_id = player_id
        self.pick_number = pick_number
        self.is_keeper = is_keeper
        self.draft_position = draft_position
        self.round = round

    def __repr__(self):
        if self.is_keeper:
            return f'{self.name} (Keeper)'
        return f'{self.name} (pick {self.pick_number})'

    def __std__(self):
        if self.is_keeper:
            return f'{self.name} (keeper)'
        return f'{self.name} (pick {self.pick_number})'