
from model.DraftPlayer import DraftPlayer
from model.ScoringFormat import ScoringFormat, get_player_score
from model.SleeperLeague import SleeperLeague
from sleeper_wrapper import Drafts, Stats

def draft_picks_by_user(draft_id):
    user_draft = {}
    position_counter= {'QB': 1,
        'RB': 1,
        'WR': 1,
        'TE': 1,
        'K': 1,
        'DST': 1}
    keeper_position_counter= {'QB': 1,
        'RB': 1,
        'WR': 1,
        'TE': 1,
        'K': 1,
        'DST': 1}

    draft = Drafts(draft_id).get_all_picks()

    for i in range(len(draft)):
        drafted_player = draft[i]
        if drafted_player['is_keeper']:
            position_counter[drafted_player['metadata']['position']] += 1

    for i in range(len(draft)):
        drafted_player = draft[i]
        player = DraftPlayer(position=drafted_player['metadata']['position'],
                name=f"{drafted_player['metadata']['first_name']} {drafted_player['metadata']['last_name']}",
                pick_number=drafted_player['pick_no'], drafted_by=drafted_player['picked_by'], player_id=drafted_player['player_id'],
                drafted_as=position_counter[drafted_player['metadata']['position']], is_keeper=drafted_player['is_keeper'],
                draft_position=drafted_player['draft_slot'], round=drafted_player['round'])
        if drafted_player['picked_by'] not in user_draft.keys():
            user_draft[drafted_player['picked_by']] = [player]
        else:
            user_draft[drafted_player['picked_by']].append(player)

        if player.is_keeper:
            player.drafted_as = keeper_position_counter[drafted_player['metadata']['position']]
            keeper_position_counter[drafted_player['metadata']['position']] += 1
        else:
            position_counter[drafted_player['metadata']['position']] += 1

    return user_draft

def sort_all_player_scores(sleeper: SleeperLeague):
    all_stats = Stats().get_all_stats('regular', sleeper.league['season'])
    player_scores = {
        'WR': {},
        'RB': {},
        'QB': {},
        'TE': {},
        'K': {},
        'DST': {},
        'IDP': {}
    }

    for player_id, player in all_stats.items():
        if 'gp' not in player.keys():
            continue
        player_score = get_player_score(player_id, all_stats, sleeper.scoring_format)
        try:
            player_position = sleeper.allPlayers[player_id]['fantasy_positions']
            if player_position is not None:
                player_scores[player_position[0]][player_id] = player_score
        except KeyError:
            continue

    return player_scores

def update_drafted_player_total_score(user_draft, all_scores):
    for user, draft in user_draft.items():
        for drafted_player in draft:
            try:
                drafted_player.points_scored = round(all_scores[drafted_player.position][drafted_player.player_id], 2)
            except KeyError:
                continue
    return user_draft

def update_drafted_player_position_rank(user_draft, all_scores):
    for key, position in all_scores.items():
        all_scores[key] = [k for k in sorted(all_scores[key], key=all_scores[key].get, reverse=True)]

    for user, draft in user_draft.items():
        for drafted_player in draft:
            try:
                drafted_player.position_rank = all_scores[drafted_player.position].index(drafted_player.player_id) + 1
            except ValueError:
                drafted_player.position_rank = 999
    return user_draft