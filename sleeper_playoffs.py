import math

from model.SleeperLeague import SleeperLeague
from model.Season import Season, get_season_rankings
from treelib import Node, Tree

def calculate_playoffs(sleeper: SleeperLeague, seasons):
    num_playoff_team = sleeper.league.get_league()['settings']['playoff_teams']
    num_byes = math.pow(2, math.ceil(math.sqrt(num_playoff_team))) - num_playoff_team

    seeding = get_season_rankings(seasons)
    upper = seeding[:num_playoff_team]
    lower = seeding[num_playoff_team:]

    print(upper)
    upper_bracket = Tree()
