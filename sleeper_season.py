import logging
from logging.config import fileConfig
from collections import defaultdict
import time

import report_generator
from sleeper import SleeperLeague, Week

fileConfig('logging_config.ini')
logger = logging.getLogger()

# class Week:
#     def __init__(self, week=0, user="", max_score=0, actual_score=0, best_lineup=None, actual_lineup=None, matchup_id=0, opponent=0):
#         self.week = week
#         self.user = user
#         self.max_score = max_score
#         self.actual_score = actual_score
#         self.best_lineup = best_lineup
#         self.actual_lineup = actual_lineup
#         self.matchup_id = matchup_id
#         self.opponent = opponent
#
#     def __repr__(self):
#         return f"{self.user} week {self.week}: actual: {self.actual_score} max: {self.max_score}"
#
#
# class SleeperLeague:
#     def __init__(self, league_id=-1):
#         self.league_id = league_id
#         self.players = Sleeper.Players()
#         self.stats = Sleeper.Stats()
#         self.league = Sleeper.League(league_id)
#         self.numQB   = self.league.get_league()['roster_positions'].count('QB')
#         self.numRB   = self.league.get_league()['roster_positions'].count('RB')
#         self.numWR   = self.league.get_league()['roster_positions'].count('WR')
#         self.numTE   = self.league.get_league()['roster_positions'].count('TE')
#         self.numFlex = self.league.get_league()['roster_positions'].count('FLEX')
#         self.numK    = self.league.get_league()['roster_positions'].count('K')
#         self.numDST  = self.league.get_league()['roster_positions'].count('DST')
#         self.allPlayers = self.players.get_all_players()
#         self.users = self.league.get_users()
#         self.rosters = self.league.get_rosters()
#
#     def get_all_players(self):
#         return self.allPlayers
#
#     def get_all_users(self):
#         users = dict()
#         for user in self.users:
#             users[user['user_id']] = user
#         return users
#
#     def get_all_rosters(self):
#         rosters = dict()
#         for roster in self.rosters:
#             rosters[roster['roster_id']] = roster
#         return rosters
#
#

def get_all_matchup_results(sleeper: SleeperLeague, scoring_format):
    all_weeks = defaultdict(list)
    for week in range(1, sleeper.league.get_league()['settings']['leg'] + 1):
        week_results = get_matchup_results_by_week(sleeper, week, scoring_format)
        for k, v in week_results.items():
            all_weeks[k].append(v)
    return all_weeks

def get_matchup_results_by_week(sleeper: SleeperLeague, week, scoring_format):
    user_results_by_week = dict()
    users = sleeper.get_all_users()
    rosters = sleeper.get_all_rosters()
    logger.info("Gathering matchups for week %d", week)
    matchups = sleeper.league.get_matchups(week)
    logger.debug("Matchups gathered")
    logger.info("Gathering stats for week %d", week)
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
        new_week = Week(week, user['display_name'], round(max_score, 2), round(actual_score, 2), best_lineup, matchup['starters'], matchup['matchup_id'], 0)
        user_results_by_week[user['user_id']] = new_week

    logger.info("Determining opponents for each user in week %d", week)
    for k, v in user_results_by_week.items():
        if v.opponent == 0:
            for k2, v2 in user_results_by_week.items():
                if v.matchup_id == v2.matchup_id and k != k2:
                    user_results_by_week[k].opponent = k2
                    user_results_by_week[k2].opponent = k
                    break
    return user_results_by_week

def calculate_best_lineup(sleeper, user, week, matchup, week_stats, scoring_format):
    logger.debug("Gathering stat information for user %s for week %d", user['display_name'], week)

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

def get_player_score(player, week_stats, scoring_format):
    score = 0
    type = scoring_format
    try:
        if scoring_format == 'pts_ppfd':
            score += week_stats[player].get('rush_fd', 0) + week_stats[player].get('rec_fd', 0)
            type = 'pts_std'
        score += week_stats[player].get(type, 0)
        return score
    except KeyError:
        return 0

# def calculate_alternate_scoring_scores(sleeper: SleeperLeague, all_weeks, type):
#     alternateall_weeks = defaultdict(list)
#     for week in range(1, sleeper.league.get_league()['settings']['leg'] + 1):
#         weekStats = sleeper.stats.get_week_stats('regular', '2023', week)
#         for user in all_weeks.keys():
#             user_week = all_weeks[user][week - 1]
#             actual_score = 0
#             for player_id in user_week.actual_lineup:
#                 if type == 'pts_ppfd':
#                     actual_score += weekStats[player_id].get('rush_fd', 0) + weekStats[player_id].get('rec_fd', 0)
#                     type = 'pts_std'
#                 try:
#                     actual_score += weekStats[player_id].get(type, 0)
#                 except KeyError:
#                     continue
#             alternateall_weeks[user].append(Week(week, user_week.user, 0, round(actual_score, 2), None, user_week.actual_lineup, user_week.matchup_id, user_week.opponent))
#     return alternateall_weeks

def calculate_standings_regular_season(sleeper: SleeperLeague, all_weeks):
    standings = defaultdict(lambda: [0] * 3)
    for week in range(1, sleeper.league.get_league()['settings']['playoff_week_start']):
        for user in all_weeks.keys():
            user_score = all_weeks[user][week - 1].actual_score
            opponent_score = all_weeks[all_weeks[user][week - 1].opponent][week - 1].actual_score
            if user_score < opponent_score:
                standings[user][1] += 1
            elif user_score > opponent_score:
                standings[user][0] += 1
            else:
                standings[user][2] += 1
            logger.debug(f"{all_weeks[user][week - 1].user}  {all_weeks[user][week - 1].actual_score} - {all_weeks[all_weeks[user][week - 1].opponent][week - 1].actual_score}  {all_weeks[all_weeks[user][week - 1].opponent][week - 1].user}")
    return standings

def main():
    logger.info("Starting")
    start = time.time()
    sleeper = SleeperLeague(917999692448034816)
    logger.info("Connected to sleeper API [%s]", time.time() - start)

    logger.info("Getting all matchup results")
    start = time.time()
    all_weeks = get_all_matchup_results(sleeper, "pts_half_ppr")
    logger.info("All matchup results gathered [%s]", time.time() - start)
    #pts_ppr, pts_half_ppr, pts_std, pts_ppfd
    #alternateWeeks = calculate_alternate_scoring_scores(sleeper, all_weeks, 'pts_ppr')
    data = report_generator.generate_week_report(sleeper, all_weeks, 1)
    report_generator.generate_user_report(sleeper, all_weeks, '735058243386212352')
    standings = calculate_standings_regular_season(sleeper, all_weeks)
    print(standings)
main()