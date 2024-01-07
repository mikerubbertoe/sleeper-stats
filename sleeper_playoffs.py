from model.SleeperLeague import SleeperLeague
from model.Season import get_original_season_rankings
import logging
from logging.config import fileConfig

fileConfig('logging_config.ini')
logger = logging.getLogger()
def calculate_playoffs(sleeper: SleeperLeague, seasons):
    # num_playoff_team = sleeper.league['settings']['playoff_teams']
    # num_byes = math.pow(2, math.ceil(math.sqrt(num_playoff_team))) - num_playoff_team
    #
    # seeding = get_season_rankings(seasons)
    # upper = seeding[:num_playoff_team]
    # lower = seeding[num_playoff_team:]
    #
    # print(upper)
    # upper_bracket = Tree()
    upper_bracket = sleeper.league_object.get_playoff_winners_bracket()

def calculate_potential_playoffs_for_user(sleeper: SleeperLeague, potential_user_seasons, playoff_week_start):
    original_standings = get_original_season_rankings(sleeper.get_all_rosters())
    winner_bracket = sleeper.league_object.get_playoff_winners_bracket()
    loser_bracket = sleeper.league_object.get_playoff_losers_bracket()
    num_playoff_team = sleeper.league['settings']['playoff_teams']

    for k, seasons in potential_user_seasons.items():
        logger.debug(f"swapping with {potential_user_seasons[k][k].name}'s season")
        roster_id_to_new_seed = dict()
        for u in seasons.values():
            new_roster_id = original_standings[u.place - 1]
            roster_id_to_new_seed[new_roster_id] = u
        logger.info("calculating winners bracket results")
        winner_bracket_results = get_bracket_results(winner_bracket, roster_id_to_new_seed, seasons, playoff_week_start)
        logger.info("calculating losers bracket results")
        loser_bracket_results = get_bracket_results(loser_bracket, roster_id_to_new_seed, seasons, playoff_week_start)

        for k, v in winner_bracket_results.items():
            seasons[v.user_id].playoff_result = k
        for k, v in loser_bracket_results.items():
            seasons[v.user_id].playoff_result = k + num_playoff_team
        logger.debug(f"final winner bracket results {sorted(winner_bracket_results.items())}")
        logger.debug(f"final loser bracket results {sorted(loser_bracket_results.items())}")


def get_bracket_results(bracket, roster_id_mapping, seasons, playoff_week_start):
    final_places = dict()
    for matchup in bracket:
        team_1, team_2 = '', ''
        if 't1_from' in matchup.keys():
            key, game = list(matchup['t1_from'].keys())[0], list(matchup['t1_from'].values())[0]
            team_1 = bracket[game - 1][key]
        else:
            team_1 = matchup.get('t1', None)

        if 't2_from' in matchup.keys():
            key, game = list(matchup['t2_from'].keys())[0], list(matchup['t2_from'].values())[0]
            team_2 = bracket[game - 1][key]
        else:
            team_2 = matchup.get('t2', None)

        team_1_score = seasons[roster_id_mapping[int(team_1)].user_id].matchups[playoff_week_start + int(matchup['r']) - 2].actual_score
        team_2_score = seasons[roster_id_mapping[int(team_2)].user_id].matchups[playoff_week_start + int(matchup['r']) - 2].actual_score
        if team_1_score > team_2_score:
            matchup['w'] = team_1
            matchup['l'] = team_2
        elif team_2_score > team_1_score:
            matchup['w'] = team_2
            matchup['l'] = team_1
        #Accoring to sleeper "If any playoff matchups end with a tie score, the winner is automatically the higher seed."
        else:
            if seasons[roster_id_mapping[int(team_1)].user_id].place < seasons[roster_id_mapping[int(team_2)].user_id].place:
                matchup['w'] = team_1
                matchup['l'] = team_2
            else:
                matchup['w'] = team_2
                matchup['l'] = team_1

        if 'p' in matchup.keys():
            place = int(matchup['p'])
            final_places[place] = roster_id_mapping[matchup['w']]
            final_places[place + 1] = roster_id_mapping[matchup['l']]

        logger.debug(f"Round {matchup['r']}: {roster_id_mapping[int(team_1)]} ({team_1_score}) VS ({team_2_score}) {roster_id_mapping[int(team_2)]}")
    return final_places