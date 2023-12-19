import sleeper_wrapper as Sleeper
from collections import defaultdict

class Week():
    def __init__(self, week=0, user="", max_score=0, actual_score=0, best_lineup=None, actual_lineup=None, matchup_id=0, opponent=0):
        self.week = week
        self.user = user
        self.max_score = max_score
        self.actual_score = actual_score
        self.best_lineup = best_lineup
        self.actual_lineup = actual_lineup
        self.matchup_id = matchup_id
        self.opponent = opponent

    def __repr__(self):
        return f"{self.user} week {self.week}: actual: {self.actual_score} max: {self.max_score}"


class SleeperLeague():
    def __init__(self, league_id=-1):
        self.league_id = league_id
        self.players = Sleeper.Players()
        self.stats = Sleeper.Stats()
        self.league = Sleeper.League(league_id)
        self.numQB   = self.league.get_league()['roster_positions'].count('QB')
        self.numRB   = self.league.get_league()['roster_positions'].count('RB')
        self.numWR   = self.league.get_league()['roster_positions'].count('WR')
        self.numTE   = self.league.get_league()['roster_positions'].count('TE')
        self.numFlex = self.league.get_league()['roster_positions'].count('FLEX')
        self.numK    = self.league.get_league()['roster_positions'].count('K')
        self.numDST  = self.league.get_league()['roster_positions'].count('DST')
        self.allPlayers = self.players.get_all_players()
        self.users = self.league.get_users()
        self.rosters = self.league.get_rosters()

    def get_all_players(self):
        return self.allPlayers

    def get_all_users(self):
        users = dict()
        for user in self.users:
            users[user['user_id']] = user
        return users

    def get_all_rosters(self):
        rosters = dict()
        for roster in self.rosters:
            rosters[roster['roster_id']] = roster
        return rosters



#def getLeague(league_id):


def getAllMatchupResults(sleeper: SleeperLeague):
    allWeeks = defaultdict(list)
    for week in range(1, sleeper.league.get_league()['settings']['leg'] + 1):
        weekResults = getMatchupResultsByWeek(sleeper, week)
        for k, v in weekResults.items():
            allWeeks[k].append(v)
    return allWeeks
def getMatchupResultsByWeek(sleeper: SleeperLeague, week):
    userResultsByWeek = dict()
    users = sleeper.get_all_users()
    players = sleeper.get_all_players()
    rosters = sleeper.get_all_rosters()
    matchups = sleeper.league.get_matchups(week)

    #For each matchup in the week, collect the starters points and find the maximum score for the scoring format provided
    for matchup in matchups:
        user = users[rosters[matchup['roster_id']]['owner_id']]
        starters = matchup['starters']
        actual_score = 0
        max_score = 0
        for i in range(len(starters)):
            points = matchup['starters_points'][i]
            actual_score += points

        #keep track of all the positions and who the highest scorer was in each position
        positions = {
            'WR' :[],
            'RB': [],
            'QB' : [],
            'TE' : [],
            'FLEX' : [],
            'K' : [],
            'DST' : []
        }
        multiplePositions = []
        #how to deal with taysem hill???
            #add to all available positions
            #keep track of which players have dual eligibility
            #after collecing all, find the index of the player in each of his positions
            #remove him from the list that has the higher index
            #basically chooses the position where he would have perfomred best in on the team
        for player in matchup['players']:
            p = players[player]

            #if the player can play multiple positions, deal with it later
            if len(p['fantasy_positions']) > 1:
                multiplePositions.append(player)

            #for each position, add them to their appropriate bucket and sort them based on who had the higher score
            for position in p['fantasy_positions']:
                p_score = matchup['players_points'][player]
                try:
                    if position != 'QB' and position != 'K' and positions[position]:
                        sortPlayerScore(positions['FLEX'], player, p_score, matchup['players_points'])
                    sortPlayerScore(positions[position], player, p_score, matchup['players_points'])
                except KeyError:
                    #an unenxpected position value came up and we shall ignore it
                    continue



        #accounts for up to 2 positions

        for dual_player in multiplePositions:
            try:
                pos = players[dual_player]['fantasy_positions']
                pos1 = positions[pos[0]]
                pos2 = positions[pos[1]]

                score_index1 = pos1.index(dual_player)
                score_index2 = pos2.index(dual_player)

                if score_index1 < score_index2:
                    pos2.remove(dual_player)
                elif score_index2 < score_index1:
                    pos1.remove(dual_player)
                else:
                    remaining_players_1 = len(pos1) - 1
                    remaining_players_2 = len(pos2) - 1
                    #if there are no remaining players on either list, then choose the first listed position
                    if remaining_players_1 == 0 == remaining_players_2:
                        pos2.remove(dual_player)
                    elif remaining_players_1 == 0:
                        pos2.remove(dual_player)
                    elif remaining_players_2 == 0:
                        pos1.remove(dual_player)
                    else:
                        next_highest_player1 = matchup['players_points'][pos1[score_index1 + 1]]
                        next_highest_player2 = matchup['players_points'][pos2[score_index2 + 1]]
                        if next_highest_player1 > next_highest_player2:
                            pos1.remove(dual_player)
                        else:
                            pos2.remove(dual_player)
            except KeyError:
                # an unenxpected position value came up and we shall ignore it
                continue
        #create the best lineup based on the number of available slots in the league
        bestLineup = []
        bestLineup.extend(positions['QB'][:sleeper.numQB])
        bestLineup.extend(positions['RB'][:sleeper.numRB])
        bestLineup.extend(positions['WR'][:sleeper.numWR])
        bestLineup.extend(positions['TE'][:sleeper.numTE])
        for flex_player in positions['FLEX']:
            if flex_player not in bestLineup:
                bestLineup.append(flex_player)
                break
        bestLineup.extend(positions['K'][:sleeper.numK])
        bestLineup.extend(positions['DST'][:sleeper.numDST])

        #calculate the max score based on the scoring format used in the league
        for player in bestLineup:
            max_score += matchup['players_points'][player]
        newWeek = Week(week, user['display_name'], round(max_score, 2), round(actual_score, 2), bestLineup, matchup['starters'], matchup['matchup_id'], 0)
        userResultsByWeek[user['user_id']] = newWeek

    for k, v in userResultsByWeek.items():
        if v.opponent == 0:
            for k2, v2 in userResultsByWeek.items():
                if v.matchup_id == v2.matchup_id and k != k2:
                    userResultsByWeek[k].opponent = k2
                    userResultsByWeek[k2].opponent = k
                    break
    return userResultsByWeek

def sortPlayerScore(position, player, score, player_scores):
    for i in range(len(position)):
        score_to_beat = player_scores[position[i]]
        if score > score_to_beat:
            position.insert(i, player)
            return position
    position.append(player)
    return position

def calculate_alternate_scoring_scores(sleeper: SleeperLeague, allWeeks, type):
    alternateAllWeeks = defaultdict(list)
    for week in range(1, sleeper.league.get_league()['settings']['leg'] + 1):
        weekStats = sleeper.stats.get_week_stats('regular', '2023', week)
        for user in allWeeks.keys():
            user_week = allWeeks[user][week - 1]
            actual_score = 0
            for player_id in user_week.actual_lineup:
                if type == 'pts_ppfd':
                    actual_score += weekStats[player_id].get('rush_fd', 0) + weekStats[player_id].get('rec_fd', 0)
                    type = 'pts_std'
                try:
                    actual_score += weekStats[player_id].get(type, 0)
                except KeyError:
                    continue
            alternateAllWeeks[user].append(Week(week, user_week.user, 0, round(actual_score, 2), None, user_week.actual_lineup, user_week.matchup_id, user_week.opponent))
    return alternateAllWeeks

def calculate_standings_regular_season(sleeper: SleeperLeague, allWeeks):
    standings = defaultdict(lambda: [0] * 3)
    for week in range(1, sleeper.league.get_league()['settings']['playoff_week_start']):
        for user in allWeeks.keys():
            userScore = allWeeks[user][week - 1].actual_score
            opponentScore = allWeeks[allWeeks[user][week].opponent][week - 1].actual_score
            if userScore < opponentScore:
                standings[user][1] += 1
            elif userScore > opponentScore:
                standings[user][0] += 1
            else:
                standings[user][2] += 1
            print(f"{allWeeks[user][week - 1].user}  {allWeeks[user][week - 1].actual_score} - {allWeeks[allWeeks[user][week].opponent][week - 1].actual_score}  {allWeeks[allWeeks[user][week].opponent][week - 1].user}")
    return standings
# Stats.get_player_week_score(Stats.get_week_stats('regular', 2023, 1), 4831)
#
# roster = l = League.get_rosters_players()
#
# players = loadAllPlayers()
# users = loadUsers()
# rosters = loadRosters()

def main():
    sleeper = SleeperLeague(917999692448034816)
    allWeeks = getAllMatchupResults(sleeper)
    #pts_ppr, pts_half_ppr, pts_std, pts_ppfd
    alternateWeeks = calculate_alternate_scoring_scores(sleeper, allWeeks, 'pts_ppr')
    standings = calculate_standings_regular_season(sleeper, allWeeks)
    print(standings)
main()