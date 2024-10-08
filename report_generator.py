import os.path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import time
import logging
from colour import Color

from logging.config import fileConfig
from model.SleeperLeague import SleeperLeague
from model.Season import Season, get_weekly_rankings, get_record_up_to_week

fileConfig('logging_config.ini')
logger = logging.getLogger()
mplstyle.use('fast')

#matplotlib is not thread safe and the majority of the time that is spent in these functions (which is the majority of the program)
#is spent in matplotlib. Theres really isnt a way around this that I have been able to think of so as of right now I cant
#think of a way to speed this up :(
#multiprocessing is being a bitch
def generate_all_week_reports(sleeper, all_weeks):
    num_weeks = min(sleeper.league['settings']['last_scored_leg'] + 1, sleeper.league['settings']['playoff_week_start'])
    logger.info(f"Generating weekly reports for week 1 - week {min(num_weeks - 1, sleeper.league['settings']['playoff_week_start'] - 1)}")
    start = time.time()

    for i in range(1,  num_weeks):
        generate_week_report(sleeper, all_weeks, i)
    logger.info(f"Done [{time.time() - start}]")

def generate_week_report(sleeper: SleeperLeague, all_weeks, week):
    logger.debug(f"Generating weekly report for week {week}")
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Acual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]
    row_labels = [f"Matchup {i}" for i in range(1, (len(all_weeks.keys()) // 2) + 1)]
    matchup_gathered = set()
    week_results = []
    coloring = []
    for user in all_weeks.keys():
        if user not in matchup_gathered:
            opponent = all_weeks[user].matchups[week - 1].opponent
            matchup_gathered.add(user)
            matchup_gathered.add(all_weeks[user].matchups[week - 1].opponent)
            formatted_match, winner = format_matchup(user, opponent, all_weeks, week)
            week_results.append(formatted_match)
            coloring.append(get_cell_coloring(winner, len(column_labels)))

    fig, ax = plt.subplots(2, 1, figsize=(1.4 * len(column_labels), 0.4 * (1 + len(row_labels) + len(row_labels) * 2) * 1.2))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(week_results, columns=column_labels)

    ax[0].axis('tight')  # turns off the axis lines and labels
    ax[0].axis('off')  # changes x and y axis limits such that all data is shown
    ax[0].get_xaxis().set_visible(False)
    ax[0].get_yaxis().set_visible(False)

    # plotting data
    table = ax[0].table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     #colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    ax[0].set_title(f"{sleeper.league['name']} {sleeper.league['season']} Week {week} ({sleeper.scoring_format_name})")
    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])


    column_labels = ["Team", "Record", "Rank", "Points Scored"]
    data = []
    seeding = get_weekly_rankings(all_weeks, week)
    records = get_record_up_to_week(all_weeks, week, sleeper.wins_above_median_active)
    week_median = round(next(iter(all_weeks.values())).matchups[week - 1].week_median, 2)
    for i in range(len(seeding)):
        user = all_weeks[seeding[i]]
        new_rank = i + 1

        if week > 1:
            previous_rank = all_weeks[seeding[i]].matchups[week - 2].place
            if (i + 1) < previous_rank:
                new_rank = f"{(i + 1)}  (\u25B2 {previous_rank - (i + 1)})"
            elif (i + 1) > previous_rank:
                new_rank = f"{(i + 1)}  (\u25BC {(i + 1) - previous_rank})"
            else:
                new_rank = f"{(i + 1)}  -"
        row = [user.name, records[user.user_id], new_rank, round(user.matchups[week - 1].points_for_up_to_now, 2)]
        data.append(row)

    df = pd.DataFrame(data, columns=column_labels)
    ax[1].text(0.025, 0.066, f'Week Median: {week_median}', color='black', bbox=dict(facecolor='#c9673c',
                edgecolor='black', boxstyle='square, pad=1.0'))
    ax[1].axis('tight')  # turns off the axis lines and labels
    ax[1].axis('off')  # changes x and y axis limits such that all data is shown
    ax[1].get_xaxis().set_visible(False)
    ax[1].get_yaxis().set_visible(False)
    plt.draw()

    # plotting data
    table = ax[1].table(cellText=df.values,
                        colLabels=df.columns,
                        colColours=["#c9673c"] * len(column_labels),
                        colWidths=[0.1] * len(column_labels),
                        loc="center",
                        cellLoc='center')

    plt.tight_layout()
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)


    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/week/week_{week}_report",
                bbox_inches='tight')

    plt.close(fig)
    plt.close('all')

def generate_all_user_report(sleeper: SleeperLeague, all_weeks):
    logger.info("Generating season reports for all users")
    start = time.time()

    for user_id in all_weeks.keys():
        generate_user_report(sleeper, all_weeks, user_id)
    logger.info(f"Done [{time.time() - start}]")

def generate_user_report(sleeper: SleeperLeague, all_weeks, user):
    logger.debug(f"Generating season report for user {all_weeks[user].name}")
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Actual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]

    num_weeks = min(len(all_weeks[user].matchups) + 1, int(sleeper.league['settings']['playoff_week_start']))
    row_labels = [f"Week {i}" for i in range(1, num_weeks)]
    week_results = []
    coloring = []

    counter = 1
    for matchup in all_weeks[user].matchups:
        week = matchup.week
        opponent = all_weeks[user].matchups[week - 1].opponent
        formatted_match, winner = format_matchup(user, opponent, all_weeks, week)
        week_results.append(formatted_match)
        coloring.append(get_cell_coloring(winner, len(column_labels)))

        counter += 1
        if counter == sleeper.league['settings']['playoff_week_start']:
            break


    fig, ax = plt.subplots(1, 1, figsize=(1.4 * len(column_labels), .4 * len(row_labels) * 1.2))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(week_results, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.draw()

    # plotting data
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center')
    ax.set_title(f"{sleeper.league['name']} {sleeper.league['season']} {all_weeks[user].name}'s Season "
                 f"({sleeper.scoring_format_name})") #800

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if 0 < row <= len(coloring) and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])
        # if col in range(4, 6):
        #     cell.set_text_props(fontproperties=FontProperties(weight='bold'))

    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/user/{all_weeks[user].name}_all_matchups_report",
                bbox_inches='tight')

    plt.tight_layout()
    fig.clf()
    plt.close()

def generate_all_season_report(sleeper: SleeperLeague, all_potential_seasons):
    logger.info("Generating all potentials season reports for all users")
    start = time.time()
    for user_id, user_seasons in all_potential_seasons.items():
        generate_all_season_report_for_user(sleeper, user_id, user_seasons)
    logger.info(f"Done [{time.time() - start}]")
def generate_all_season_report_for_user(sleeper: SleeperLeague, user, all_potential_seasons):
    logger.debug(f"Generating all potential seasons report for user {all_potential_seasons[user][user].name}")

    column_labels = [f"{sleeper.get_all_users()[opponent]['display_name']}'s Schedule" for opponent in all_potential_seasons.keys()]
    #num_weeks = min(sleeper.league['settings']['leg'], sleeper.league['settings']['playoff_week_start'])
    #row_labels = [f"Week {i}" for i in range(1, num_weeks)]
    row_labels =['Record', 'Seed', 'Playoffs Made?', 'Playoff Results']
    data = []
    record = []
    seed = []
    playoffs = []
    playoff_results = []
    coloring = []
    playoff_result_color = []
    col_color = []
    for opponent in all_potential_seasons.keys():
        season: Season = all_potential_seasons[opponent][user]
        record.append(season.get_record())
        seed.append(season.place)
        playoffs.append("YES" if season.made_playoffs else "NO")
        if season.made_playoffs:
            col_color.append('#c6efce')
        else:
            col_color.append('#ffc7ce')
        playoff_results.append(season.playoff_result)
        if season.playoff_result == 1:
            playoff_result_color.append('#FFD700')
        elif season.playoff_result == 2:
            playoff_result_color.append('#C0C0C0')
        elif season.playoff_result == 3:
            playoff_result_color.append('#CD7F32')
        else:
            playoff_result_color.append(col_color[-1])
    data.append(record)
    data.append(seed)
    data.append(playoffs)
    data.append(playoff_results)
    for i in range(len(data) - 1):
        coloring.append(col_color)
    coloring.append(playoff_result_color)


    fig, ax = plt.subplots(1, 1, figsize=(1.9 * len(column_labels), 0.5 * len(row_labels) * 1.2))
    df = pd.DataFrame(data, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    plt.draw()

    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     loc="center",
                     cellLoc='center',
                     rowLoc='center',
                     colLoc='center')
    ax.set_title(
        f"{sleeper.league['name']} {sleeper.league['season']} {all_potential_seasons[user][user].name}'s "
        f"all potential seasons ({sleeper.scoring_format_name})")  # 800
    plt.tight_layout()
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    table.scale(1, 2)

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])

    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/potential_season/"
                f"{all_potential_seasons[user][user].name}_potential_seasons", bbox_inches='tight')
    fig.clf()
    plt.close()

def generate_season_report():
    return

def generate_user_statistics_report(sleeper: SleeperLeague, season, season_stats):
    logger.info("Generating season statistics for all users")
    start = time.time()
    column_labels = [user.name for user in season.values()]
    row_labels = ["Points Scored", "Points Against", "Overall Accuracy", "Opponent Accuracy", "Average Score",
                  "Std Dev", "Highest Score", "Lowest Score", "Weeks Thrown", "Total Touchdowns"]
    data = []

    for user in season.values():
        row = []
        stats = season_stats[user.user_id]
        row.append(round(user.points_earned, 2))
        row.append(round(user.points_against, 2))
        row.append(f'{stats.overallAccuracy}%')
        row.append(f'{stats.opponentAccuracy}%')
        row.append(stats.averageScore)
        row.append(stats.averageScoreStdDeviation)

        highestScoreWeekResult = 'W'
        if user.matchups[stats.highestScoreWeek - 1].result == 1:
            highestScoreWeekResult = 'W'
        elif user.matchups[stats.highestScoreWeek - 1].result == -1:
            highestScoreWeekResult = 'L'
        else:
            highestScoreWeekResult = 'T'

        lowestScoreWeekResult = 'L'
        if user.matchups[stats.lowestScoreWeek - 1].result == 1:
            lowestScoreWeekResult = 'W'
        elif user.matchups[stats.lowestScoreWeek - 1].result == -1:
            lowestScoreWeekResult = 'L'
        else:
            lowestScoreWeekResult = 'T'

        row.append(f'{stats.highestScore} ({highestScoreWeekResult}) (Week {stats.highestScoreWeek})')
        row.append(f'{stats.lowestScore} ({lowestScoreWeekResult}) (Week {stats.lowestScoreWeek})')
        row.append(stats.numberWeeksThrown)
        row.append(int(stats.totalTouchdowns))
        data.append(row)

    new_data = pivot_data(data)
    fig, ax = plt.subplots(1, 1, figsize=(1.9 * len(column_labels), 0.5 * (len(row_labels)) * 1.2))
    df = pd.DataFrame(new_data, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     loc="center",
                     cellLoc='center',
                     rowLoc='center',
                     colLoc='center')
    ax.set_title(
        f"{sleeper.league['name']} {sleeper.league['season']} Statistics ({sleeper.scoring_format_name})")  # 800

    table.auto_set_font_size(False)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    table.set_fontsize(11)

    table.scale(1, 2.25)
    plt.draw()
    plt.tight_layout()

    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/"
                f"{sleeper.league['name']}_{sleeper.league['season']}_statistics",
                bbox_inches='tight')
    fig.clf()
    plt.close()
    logger.info(f"Done [{time.time() - start}]")
    return

def generate_player_all_week_rankings(sleeper, all_weeks):
    num_weeks = min(sleeper.league['settings']['last_scored_leg'] + 1, sleeper.league['settings']['playoff_week_start'])
    logger.info(f"Generating player ranking reports for week 1 - week {min(num_weeks - 1, sleeper.league['settings']['playoff_week_start'] - 1)}")
    start = time.time()

    for i in range(1, num_weeks):
        generate_player_week_rankings(sleeper, all_weeks, i)
    logger.info(f"Done [{time.time() - start}]")


def generate_player_week_rankings(sleeper: SleeperLeague, all_weeks, week):
    logger.debug(f"Generating weekly ranking report for week {week}")

    column_labels = [user.name for user in all_weeks.values()]
    row_labels = []
    user_result = []
    data = []
    coloring = []
    #Get the number of position players in the league
    for position in sleeper.league['roster_positions']:
        if position != 'BN':
            row_labels.append(position)
    row_labels.append("RESULT")

    #if id is 0, that slot was left empty. Corrolate the roster_positions dict value to the index of the 0 and that is
    #the roster spot that was left empty

    #Generate the position rank for the week given the current scoring system
    for user in all_weeks.values():
        row = []
        match_lineup = user.matchups[week - 1].actual_lineup
        for i in range(len(match_lineup)):
            player = match_lineup[i]
            player_score = 0.0
            #when a player has a value of 0, it means the slot was left empty and se should set the ranking to 999. We
            #can determine the position by finding out what index the 0 was at and corrolate it to the possible rosters.
            #have to check if multiple slots were left open as well
            if player == '0':
                indicies = [j for j, p in enumerate(match_lineup) if p == player]
                for i in indicies:
                    player_position = sleeper.league['roster_positions'][i]
                    player_ranking = 999
                    row.append(f'{player_position} {player_ranking } (0.0)')
            else:
                player_position = sleeper.allPlayers[player]['fantasy_positions'][0]
                try:
                    player_ranking = sleeper.player_weekly_rankings[week][player_position].index(player)
                    player_score = [score for _, score in enumerate(user.matchups[week - 1].starter_stats) if player == score.player_id][0].points_scored
                except ValueError:
                    player_ranking = 998
                row.append(f'{player_position} {player_ranking + 1} ({round(player_score, 2)})')

        if user.matchups[week - 1].result == 1:
            user_result.append(f'WIN ({round(user.matchups[week - 1].actual_score, 2)})')
        elif user.matchups[week - 1].result == -1:
            user_result.append(f'LOSS ({round(user.matchups[week - 1].actual_score, 2)})')
        else:
            user_result.append(f'TIE ({round(user.matchups[week - 1].actual_score, 2)})')
        data.append(row)

    #pivot the data and get the cell coloring
    data = pivot_data(data)
    for position_row in data:
        coloring.append(get_ranking_colors(position_row))

    data.append(user_result)
    result_colors = []
    for result in user_result:
        if result.startswith('WIN'):
            result_colors.append(Color('green').hex)
        elif result.startswith('LOSS'):
            result_colors.append(Color('red').hex)
        else:
            result_colors.append(Color('yellow').hex)
    coloring.append(result_colors)

    fig, ax = plt.subplots(1, 1, figsize=(1.7 * len(column_labels), .4 * len(row_labels) * 1.2))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(data, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # plotting data
    table = ax.table(cellText=df.values,
                        colLabels=df.columns,
                        rowLabels=row_labels,
                        rowColours=["#57b56a"] * len(row_labels),
                        colColours=["#c9673c"] * len(column_labels),
                        # colWidths=[0.1] * len(column_labels),
                        loc="center",
                        cellLoc='center',
                        rowLoc='center',
                        colLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    plt.draw()
    plt.tight_layout()

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])
            cell.set_alpha(0.5)

    ax.set_title(f"{sleeper.league['name']} {sleeper.league['season']} Player Rankings Week {week} "
                 f"({sleeper.scoring_format_name})") #0.7350

    # plt.title(f"{sleeper.league['name']} {sleeper.league['season']} Player Rankings Week {week} "
    #           f"({sleeper.scoring_format_name})") #0.7350
    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/week_rank/week_{week}_ranking_report"
                , bbox_inches='tight')

    plt.close(fig)
    plt.close()

def generate_users_draft_reports(sleeper: SleeperLeague, drafted_players):
    logger.info(f"Generating draft report for all users")
    start = time.time()
    for user in drafted_players.keys():
        generate_user_draft_report(sleeper, drafted_players, user)
    logger.info(f"Done [{time.time() - start}]")

def generate_user_draft_report(sleeper: SleeperLeague, drafted_players, user):
    logger.debug(f"Generating draft report for {sleeper.get_all_users()[user]['display_name']}")
    column_labels = ["Name", "Pick #", "Position", "Draft Position Rank", "Actual Position Rank", "Rank Difference",
                     "Games Played", "Points per Game"]
    row_labels = []
    data = []
    coloring = []
    draft_position = 0

    for drafted_player in drafted_players[user]:
        if drafted_player.is_keeper:
            row_labels.append("KEEPER")
        else:
            round_pick = drafted_player.round
            row_labels.append(f'Round {round_pick}')
        row = [drafted_player.name, drafted_player.pick_number, drafted_player.position, drafted_player.drafted_as,
                     drafted_player.position_rank, drafted_player.drafted_as - drafted_player.position_rank,
                     drafted_player.games_played, drafted_player.ppg]
        data.append(row)

        coloring.append(get_draft_colors(row, drafted_player))

    fig, ax = plt.subplots(1, 1, figsize=(1.4 * len(column_labels), 0.4 * len(row_labels) * 1.2))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(data, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # plotting data
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     # colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center',
                     rowLoc='center',
                     colLoc='center')

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])
            cell.set_alpha(0.5)

    table.auto_set_font_size(False)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    table.set_fontsize(9)
    table.scale(1, 2)
    plt.draw()
    plt.tight_layout()

    ax.set_title(
        f"{sleeper.get_all_users()[user]['display_name']} {sleeper.league['season']} Draft Report (Draft Position "
        f"{drafted_players[user][0].draft_position})")

    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/draft/"
                f"{sleeper.get_all_users()[user]['display_name']}_draft_report", bbox_inches='tight')

    plt.close(fig)
    plt.close()

def generate_all_users_top_10_player_report(sleeper: SleeperLeague, season):
    logger.info(f"Generating top 10 players report for all users")
    start = time.time()

    for user_season in season.values():
        generate_user_top_10_player_report(sleeper, user_season)

    logger.info(f"Done [{time.time() - start}]")

def generate_user_top_10_player_report(sleeper: SleeperLeague, user_season):
    logger.debug(f"Generating top 10 players report for {sleeper.get_all_users()[user_season.user_id]['display_name']}")
    top_10_players = user_season.get_top_players_for_user(10)
    column_labels = ["Name", "Rank", "Games Played", "Points Scored", "Points Per Game", "Point Share"]
    row_labels = [i + 1 for i in range(len(top_10_players))]
    data = []
    for player in top_10_players:
        row = []
        row.append(player.name)
        row.append(f'{player.fantasy_positions[0]} {player.position_ranking}')
        row.append(player.games_played)
        row.append(player.points_scored)
        row.append(player.ppg)
        row.append(f'{round((player.points_scored / user_season.points_earned) * 100, 2)}%')

        data.append(row)

    fig, ax = plt.subplots(1, 1, figsize=(1.4 * len(column_labels), 0.4 * len(row_labels) * 1.2))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(data, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # plotting data
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     # colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center',
                     rowLoc='center',
                     colLoc='center')

    table.auto_set_font_size(False)
    table.auto_set_column_width(col=list(range(len(df.columns))))
    table.set_fontsize(9)
    table.scale(1, 2)
    plt.draw()
    plt.tight_layout()

    ax.set_title(
        f"{sleeper.get_all_users()[user_season.user_id]['display_name']} {sleeper.league['season']} Top 10 Regular Season Players")

    plt.savefig(f"reports/{sleeper.league['name']}/{sleeper.league['season']}/top_10/"
                f"{sleeper.get_all_users()[user_season.user_id]['display_name']}_top_10", bbox_inches='tight')

    plt.close(fig)
    plt.close()

def get_cell_coloring(winner, col_length):
    colors = []
    color_set_1 = ['#c6efce'] * (col_length // 2)
    color_set_2 = ['#ffc7ce'] * (col_length // 2)
    if winner == 1:
        colors.extend(color_set_1)
        colors.extend(color_set_2)
    elif winner == 2:
        colors.extend(color_set_2)
        colors.extend(color_set_1)
    else:
        colors.extend(color_set_2)
        colors.extend(color_set_2)
    return colors

def get_ranking_colors(row):
    row_colors = [r for r in row]
    sorted_ranks = [k.split(' ')[1] for k in sorted(row, key=lambda curr: int(curr.split(' ')[1]))]
    first = Color('Green')
    last = Color('Red')
    colors = list(first.range_to(last, len(row)))
    for i in range(len(sorted_ranks)):
        indicies = [j for j, y in enumerate(row) if y.split(' ')[1] == sorted_ranks[i]]
        for ind in indicies:
            if not row_colors[ind].startswith('#'):
                row_colors[ind] = colors[i].hex

    return row_colors

def get_draft_colors(row, drafted_player):
    first = Color('Green')
    last = Color('Red')
    colors = list(last.range_to(first, 11))
    rank_difference = drafted_player.drafted_as - drafted_player.position_rank
    color_step = rank_difference // 4
    if rank_difference < 0:
        color_step = max(color_step, -5)
    else:
        color_step = min(color_step, 5)

    row_colors = [colors[(len(colors) // 2) + color_step].hex] * len(row)
    return row_colors


#Thrown Week? | Start/Sit Accuracy | Max Points | Acual Points | Team 1 | Team 2 | Actual Points | Max Points | Start/Sit Accuracy | Thrown Week?
def format_matchup(p, o, all_weeks, week):
    player = all_weeks[p].matchups[week - 1]
    opponent = all_weeks[o].matchups[week - 1]

    team_1_name = player.user.upper()
    team_1_score = player.actual_score
    team_1_best_score = player.max_score
    team_1_accuracy = round((team_1_score / team_1_best_score) * 100, 2)
    team_1_throw = player.thrown_week

    team_2_name = opponent.user.upper()
    team_2_score = opponent.actual_score
    team_2_best_score = opponent.max_score
    team_2_accuracy = round((team_2_score / team_2_best_score) * 100, 2)
    team_2_throw = opponent.thrown_week

    winner = 0
    if player.week > 1:
        team_1_name = f"{team_1_name} ({all_weeks[p].matchups[week - 2].place})"
        team_2_name = f"{team_2_name} ({all_weeks[o].matchups[week - 2].place})"

    #if team 1 lost, set the winner
    if team_1_score < team_2_score:
        winner = 2
    #if team 2 lost, set the winner
    elif team_2_score < team_1_score:
        winner = 1

    return ([team_1_throw, str(team_1_accuracy) + "%", team_1_best_score, team_1_score, team_1_name,
             team_2_name, team_2_score, team_2_best_score, str(team_2_accuracy) + "%", team_2_throw], winner)


def create_or_clear_folder(folder_dir):
    os.makedirs(f'{os.path.join(os.getcwd(), f"{folder_dir}")}', exist_ok=True)

    for f in os.listdir(folder_dir):
        os.remove(os.path.join(folder_dir, f))

def pivot_data(data):
    new_data = []
    for i in range(len(data[0])):
        new_data.append([])
        for j in range(len(data)):
            new_data[i].append(data[j][i])
    return new_data