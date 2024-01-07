import logging
import time
from logging.config import fileConfig

import report_generator
from model.Week import Week, set_thrown_week
from model.SleeperLeague import SleeperLeague
from model.Season import Season
from model.Season import get_season_rankings
from model.ScoringFormat import get_player_score

fileConfig('logging_config.ini')
logger = logging.getLogger()

def get_all_matchup_results(sleeper: SleeperLeague, scoring_format):
    season = dict()
    for user in sleeper.users:
        season[user['user_id']] = Season(name=user['display_name'], user_id=user['user_id'], matchups=[])
    #num_weeks = min(sleeper.league['settings']['leg'], sleeper.league['settings']['playoff_week_start'])
    num_weeks = sleeper.league['settings']['leg']
    for week in range(1, num_weeks + 1):
        week_results = get_matchup_results_by_week(sleeper, week, scoring_format)
        for k, v in week_results.items():
            season[k].matchups.append(v)
            if week < sleeper.league['settings']['playoff_week_start']:
                season[k].points_earned += v.actual_score
                season[k].points_possible += round(v.max_score, 2)
                season[k].points_against += round(v.opponent_score, 2)
            if week > 1:
                v.points_for_up_to_now = season[k].matchups[week - 2].points_for_up_to_now + v.actual_score
            else:
                v.points_for_up_to_now = v.actual_score
        if week < sleeper.league['settings']['playoff_week_start']:
            update_season_rankings(season, week_results)

    for k, v in sleeper.get_all_rosters().items():
        season[v['owner_id']].roster_id = k

    find_playoff_teams(season, sleeper.league['settings']['playoff_teams'])
    return season

def update_season_rankings(season, week_results):
    for k, v in week_results.items():
        if v.result == 1:
            season[k].wins += 1
        elif v.result == -1:
            season[k].losses += 1
        else:
            season[k].ties += 1

    seeding = get_season_rankings(season)

    for i in range(len(seeding)):
        week_results[seeding[i]].place = i + 1
    return

def get_matchup_results_by_week(sleeper: SleeperLeague, week, scoring_format):
    logger.info("Gathering results for week %d", week)
    user_results_by_week = dict()
    users = sleeper.get_all_users()
    rosters = sleeper.get_all_rosters()

    logger.debug("Gathering matchups for week %d", week)
    matchups = sleeper.league_object.get_matchups(week)
    logger.debug("Matchups gathered")
    logger.debug("Gathering stats for week %d", week)
    week_stats = sleeper.stats.get_week_stats('regular', '2023', week)
    logger.debug("Stats gathered")

    #For each matchup in the week, collect the starters points and find the maximum score for the scoring format provided
    for matchup in matchups:
        user = users[rosters[matchup['roster_id']]['owner_id']]
        logger.debug("Gathering stat information for user %s for week %d", user['display_name'], week)
        actual_score = 0
        max_score = 0

        for player in matchup['starters']:
            actual_score += get_player_score(player, week_stats, scoring_format)
        best_lineup = calculate_best_lineup(sleeper, user, week, matchup, week_stats, scoring_format)

        #calculate the max score based on the scoring format used in the league
        for player in best_lineup:
            max_score += matchup['players_points'][player]
        new_week = Week(week, user['display_name'], round(max_score, 2), round(actual_score, 2), best_lineup, matchup['starters'], matchup['matchup_id'], 0, 0)
        user_results_by_week[user['user_id']] = new_week

    logger.debug("Determining opponents for each user in week %d", week)
    for k, v in user_results_by_week.items():
        if v.opponent == 0:
            for k2, v2 in user_results_by_week.items():
                if v.matchup_id == v2.matchup_id and k != k2:
                    user_results_by_week[k].opponent = k2
                    user_results_by_week[k].opponent_score = v2.actual_score
                    user_results_by_week[k2].opponent = k
                    user_results_by_week[k2].opponent_score = v.actual_score

                    set_thrown_week(user_results_by_week[k], user_results_by_week[k2])
                    break

    return user_results_by_week

def calculate_best_lineup(sleeper, user, week, matchup, week_stats, scoring_format):
    # keep track of all the positions and who the highest scorer was in each position
    positions = {
        'WR': [],
        'RB': [],
        'QB': [],
        'TE': [],
        'FLEX': [],
        'K': [],
        'DST': []
    }
    multiple_positions = []
    # how to deal with taysem hill???
    # add to all available positions
    # keep track of which players have dual eligibility
    # after collecing all, find the index of the player in each of his positions
    # remove him from the list that has the higher index
    # basically chooses the position where he would have perfomred best in on the team
    logger.debug("calculating best roster for user %s in week %d", user['display_name'], week)
    for player in matchup['players']:
        p = sleeper.get_all_players()[player]

        # if the player can play multiple positions, deal with it later
        if len(p['fantasy_positions']) > 1:
            multiple_positions.append(player)

        # for each position, add them to their appropriate bucket and sort them based on who had the higher score
        for position in p['fantasy_positions']:

            try:
                if position != 'QB' and position != 'K' and position in positions.keys():
                    sort_player_score(positions['FLEX'], player, week_stats, scoring_format)
                sort_player_score(positions[position], player, week_stats, scoring_format)
            except KeyError:
                # an unenxpected position value came up and we shall ignore it
                continue

    # accounts for up to 2 positions
    for dual_player in multiple_positions:
        try:
            pos = sleeper.get_all_players()[dual_player]['fantasy_positions']
            pos1 = positions[pos[0]]
            pos2 = positions[pos[1]]

            score_index_1 = pos1.index(dual_player)
            score_index_2 = pos2.index(dual_player)

            if score_index_1 < score_index_2:
                pos2.remove(dual_player)
            elif score_index_2 < score_index_1:
                pos1.remove(dual_player)
            else:
                remaining_players_1 = len(pos1) - 1
                remaining_players_2 = len(pos2) - 1
                # if there are no remaining players on either list, then choose the first listed position
                if remaining_players_1 == 0 == remaining_players_2:
                    pos2.remove(dual_player)
                elif remaining_players_1 == 0:
                    pos2.remove(dual_player)
                elif remaining_players_2 == 0:
                    pos1.remove(dual_player)
                else:
                    next_highest_player1 = get_player_score(pos1[score_index_1 + 1], week_stats, scoring_format)
                    next_highest_player2 = get_player_score(pos1[score_index_2 + 1], week_stats, scoring_format)

                    if next_highest_player1 > next_highest_player2:
                        pos1.remove(dual_player)
                    else:
                        pos2.remove(dual_player)
        except KeyError:
            # an unenxpected position value came up and we shall ignore it
            continue
    # create the best lineup based on the number of available slots in the league

    best_lineup = []
    best_lineup.extend(positions['QB'][:sleeper.numQB])
    best_lineup.extend(positions['RB'][:sleeper.numRB])
    best_lineup.extend(positions['WR'][:sleeper.numWR])
    best_lineup.extend(positions['TE'][:sleeper.numTE])
    for flex_player in positions['FLEX']:
        if flex_player not in best_lineup:
            best_lineup.append(flex_player)
            break
    best_lineup.extend(positions['K'][:sleeper.numK])
    best_lineup.extend(positions['DST'][:sleeper.numDST])
    return best_lineup

def sort_player_score(position, player, week_stats, scoring_format):
    score = get_player_score(player, week_stats, scoring_format)
    for i in range(len(position)):
        score_to_beat = get_player_score(position[i], week_stats, scoring_format)
        if score > score_to_beat:
            position.insert(i, player)
            return position
    position.append(player)
    return position

def calculate_standings_regular_season(sleeper: SleeperLeague, all_seasons):
    for week in range(1, sleeper.league['settings']['playoff_week_start']):
        for user in all_seasons.keys():
            opponent = all_seasons[user].matchups[week - 1].opponent
            user_score = all_seasons[user].matchups[week - 1].actual_score
            opponent_score = all_seasons[opponent].matchups[week - 1].actual_score
            if user_score < opponent_score:
                all_seasons[user].losses += 1
            elif user_score > opponent_score:
                all_seasons[user].wins += 1
            else:
                all_seasons[user].ties += 1

    find_playoff_teams(all_seasons, sleeper.league['settings']['playoff_teams'])
    if logger.level == logging.DEBUG:
        for v in all_seasons.values():
            logger.debug(f"{v.name}: {v.get_record()}")

def caulculate_standings_for_all_schedules(sleeper: SleeperLeague, all_seasons):
    all_potential_seasons = dict()
    for k, v in (all_seasons.items()):
        user = v.user_id
        all_potential_seasons[user] = calculate_user_standings_for_all_schedule(sleeper, all_seasons, user)

    return all_potential_seasons

def calculate_user_standings_for_all_schedule(sleeper: SleeperLeague, all_seasons, user):
    all_potential_season = dict()
    for u in all_seasons.keys():
        all_potential_season[u] = dict()

    for v in (all_seasons.values()):
        original_season_id = v.user_id
        potential_seasons = dict()
        num_weeks = sleeper.league['settings']['leg']
        for u in all_seasons.keys():
            potential_seasons[u] = Season(all_seasons[u].name, all_seasons[u].user_id, all_seasons[u].roster_id,
                points_earned=all_seasons[u].points_earned,
                points_possible=all_seasons[u].points_possible)

        for week in range(1, num_weeks + 1):
            current_week_results = dict()
            for u in all_seasons.keys():
                opponent = all_seasons[u].matchups[week - 1].opponent

                # If the u we are currently looking at is the one we are doing the projections for, we need to flip the opponent
                # they are facing with the original schedule
                if u == user:
                    opponent = all_seasons[original_season_id].matchups[week - 1].opponent
                    # If we see we are playing ourselves, that means the matchup is user vs original_season_id and set the opponent
                    # back to the original season id
                    if opponent == user:
                        opponent = original_season_id

                # If the u we are currently looking at is the one original schedule id, we need to flip the opponent
                # they are facing with the user
                elif u == original_season_id:
                    opponent = all_seasons[user].matchups[week - 1].opponent
                    # If we see we are playing ourselves, that means the matchup is user vs original_season_id and set the opponent
                    # back to the user id
                    if opponent == original_season_id:
                        opponent = user

                # if the opponent we are playing is the user, flip it to the original season id
                elif opponent == user:
                    opponent = original_season_id

                # if the opponent we are playing is the original season id, flip it to the user
                elif opponent == original_season_id:
                    opponent = user

                user_score = all_seasons[u].matchups[week - 1].actual_score
                opponent_score = all_seasons[opponent].matchups[week - 1].actual_score
                if week < sleeper.league['settings']['playoff_week_start']:
                    potential_seasons[u].points_against += opponent_score

                week_result = Week(week, all_seasons[u].name, all_seasons[u].matchups[week - 1].max_score, user_score, all_seasons[u].matchups[week - 1].best_lineup, all_seasons[u].matchups[week - 1].actual_lineup, 0, opponent, opponent_score)
                potential_seasons[u].matchups.append(week_result)
                current_week_results[u] = week_result

            for v in current_week_results.values():
                set_thrown_week(v, current_week_results[v.opponent])

            if week < sleeper.league['settings']['playoff_week_start']:
                update_season_rankings(potential_seasons, current_week_results)

        find_playoff_teams(potential_seasons, sleeper.league['settings']['playoff_teams'])
        all_potential_season[original_season_id] = potential_seasons
    return all_potential_season

def find_playoff_teams(season, num_playoff_teams):
    seeding = get_season_rankings(season)

    for i in range(len(seeding)):
        if i < num_playoff_teams:
            season[seeding[i]].made_playoffs = True
        season[seeding[i]].place = i + 1

# def main():
#     logger.info("Starting")
#     start = time.time()
#     sleeper = SleeperLeague(917999692448034816)
#     logger.info("Connected to sleeper API [%s]", time.time() - start)
#     new_rules = {'fg_made_50p': 0.0,
#     'fg_made_40_49': 0.0,
#     'fg_made_30_39': 0.0,
#     'fg_made_20_29': 0.0,
#     'fg_made_0_19': 0.0,
#     'xp_made': 0.0,
#     'fg_miss': 0.0,
#     'xp_miss': 0.0}
#     sf = ScoringFormat(new_rules=new_rules)
#
#     sf = ScoringFormat('PPFD')
#     logger.info("Getting all matchup results")
#     start = time.time()
#     all_weeks = get_all_matchup_results(sleeper, sf)
#     #all_weeks2 = get_all_matchup_results(sleeper, sf)
#     logger.info("All matchup results gathered [%s]", time.time() - start)
#     calculate_playoffs(sleeper, all_weeks)
#     report_generator.generate_all_week_reports(sleeper, all_weeks)
#     report_generator.generate_all_user_report(sleeper, all_weeks)
#     #a = caulculate_standings_for_all_schedules(sleeper, all_weeks)
#     #report_generator.generate_all_season_report(sleeper, a)
#
#     #u = calculate_user_standings_for_all_schedule(sleeper, all_weeks, '471079573686054912')
#     #report_generator.generate_all_season_report_for_user(sleeper, '471079573686054912', u)
#
#     logger.info("Done")
#     #report_generator.generate_user_report(sleeper, all_weeks, '735058243386212352')
#
# if __name__ == '__main__':
#     # cProfile.run('main()', sort='tottime')
#     main()