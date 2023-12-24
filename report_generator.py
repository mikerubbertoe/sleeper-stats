from multiprocessing.pool import ThreadPool

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import time
import logging
import multiprocessing as mp

from logging.config import fileConfig
from model.SleeperLeague import SleeperLeague
from model.Week import Week
from model.Season import Season, get_weekly_rankings, get_record_up_to_week

fileConfig('logging_config.ini')
logger = logging.getLogger()
mplstyle.use('fast')

#matplotlib is not thread safe and the majority of the time that is spent in these functions (which is the majority of the program)
#is spent in matplotlib. Theres really isnt a way around this that I have been able to think of so as of right now I cant
#think of a way to speed this up :(
#multiprocessing is being a bitch
def generate_all_week_reports(sleeper, all_weeks):
    num_weeks = min(sleeper.league.get_league()['settings']['leg'],sleeper.league.get_league()['settings']['playoff_week_start'])
    logger.info(f"Generating weekly reports for week 1 - week {num_weeks - 1}")
    start = time.time()
    args = [(sleeper, all_weeks, i) for i in range(1, num_weeks)]
    # processes = [mp.Process(target=generate_week_report, args=(sleeper, all_weeks, i)) for i in range(1, num_weeks)]
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join()

    # pool1 = mp.Pool(processes=14)
    # pool1.starmap(generate_week_report, args)
    # pool1.close()
    # pool1.join()

    for i in range(1,  num_weeks):
        generate_week_report(sleeper, all_weeks, i)
    logger.info(f"Done [{time.time() - start}]")
    time.sleep(0.1)

def generate_week_report(sleeper: SleeperLeague, all_weeks, week):
    logger.debug(f"Generating weekly report for week {week}")
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Acual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]
    row_labels = ["Matchup 1", "Matchup 2", "Matchup 3", "Matchup 4", "Matchup 5"]
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

    fig, ax = plt.subplots(2, 1, figsize=(1.4 * len(column_labels), 1 * len(week_results) * 1.6))
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
                     colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    ax[0].set_title(f"{sleeper.league.get_league()['name']} {sleeper.league.get_league()['season']} Week {week} (SCORING FORMAT)", y=0.870)
    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])


    column_labels = ["Team", "Record", "Rank", "Points Scored"]
    data = []
    seeding = get_weekly_rankings(all_weeks, week)
    records = get_record_up_to_week(all_weeks, week)
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
        row = [user.name, records[user.user_id], new_rank, round(user.points_earned, 2)]
        data.append(row)

    df = pd.DataFrame(data, columns=column_labels)
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

    plt.savefig(f"reports/week/week_{week}_report",
                bbox_inches='tight')

    plt.close(fig)
    plt.close('all')

def generate_all_user_report(sleeper: SleeperLeague, all_weeks):
    logger.info("Generating season reports for all users")
    start = time.time()
    args = [(sleeper, all_weeks, user) for user in all_weeks.keys()]
    pool1 = mp.Pool(processes=10)
    pool1.starmap(generate_week_report, args)
    pool1.close()
    pool1.join()
    # for user_id in all_weeks.keys():
    #     generate_user_report(sleeper, all_weeks, user_id)
    logger.info(f"Done [{time.time() - start}]")

def generate_user_report(sleeper: SleeperLeague, all_weeks, user):
    logger.debug(f"Generating season report for user {all_weeks[user].name}")
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Actual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]
    row_labels = [f"Week {i}" for i in range(1, len(all_weeks[user].matchups) + 1)]
    week_results = []
    coloring = []

    for matchup in all_weeks[user].matchups:
        week = matchup.week
        opponent = all_weeks[user].matchups[week - 1].opponent
        formatted_match, winner = format_matchup(user, opponent, all_weeks, week)
        week_results.append(formatted_match)
        coloring.append(get_cell_coloring(winner, len(column_labels)))

    fig, ax = plt.subplots(1, 1, figsize=(1.4 * len(column_labels), .8 * len(week_results)))
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
                     colWidths=[0.1] * 10,
                     loc="center",
                     cellLoc='center')
    ax.set_title(f"{sleeper.league.get_league()['name']} {sleeper.league.get_league()['season']} {all_weeks[user].name}'s Season (SCORING FORMAT)", y=0.800) #800
    plt.tight_layout()
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

    start = time.time()
    plt.savefig(f"reports/user/{all_weeks[user].name}_all_matchups_report",
                bbox_inches='tight')
    logger.debug(f"{time.time() - start}")
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
    #num_weeks = min(sleeper.league.get_league()['settings']['leg'], sleeper.league.get_league()['settings']['playoff_week_start'])
    #row_labels = [f"Week {i}" for i in range(1, num_weeks)]
    row_labels =['Record', 'Seed', 'Playoffs made?']
    data = []
    record = []
    seed = []
    playoffs = []
    coloring = []
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
    data.append(record)
    data.append(seed)
    data.append(playoffs)
    for i in range(len(data)):
        coloring.append(col_color)


    fig, ax = plt.subplots(1, 1, figsize=(1.9 * len(column_labels), 1.2 * len(data)))
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
                     colWidths=[0.1] * 10,
                     loc="center",
                     cellLoc='center',
                     rowLoc='center',
                     colLoc='center')
    ax.set_title(
        f"{sleeper.league.get_league()['name']} {sleeper.league.get_league()['season']} {all_potential_seasons[user][user].name}'s all potential seasons (SCORING FORMAT)",
        y=0.800)  # 800
    plt.tight_layout()
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    table.scale(1, 2)

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])

    start = time.time()
    plt.savefig(f"reports/potential_seasons/{all_potential_seasons[user][user].name}_potential_seasons", bbox_inches='tight')
    logger.debug(f"{time.time() - start}")
    fig.clf()
    plt.close()

def generate_season_report():
    return

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

#Thrown Week? | Start/Sit Accuracy | Max Points | Acual Points | Team 1 | Team 2 | Actual Points | Max Points | Start/Sit Accuracy | Thrown Week?
def format_matchup(p, o, all_weeks, week):
    player = all_weeks[p].matchups[week - 1]
    opponent = all_weeks[o].matchups[week - 1]

    team_1_name = player.user.upper()
    team_1_score = player.actual_score
    team_1_best_score = player.max_score
    team_1_accuracy = round((team_1_score / team_1_best_score) * 100, 2)
    team_1_throw = ""

    team_2_name = opponent.user.upper()
    team_2_score = opponent.actual_score
    team_2_best_score = opponent.max_score
    team_2_accuracy = round((team_2_score / team_2_best_score) * 100, 2)
    team_2_throw = ""

    winner = 0
    if player.week > 1:
        team_1_name = f"{team_1_name} ({all_weeks[p].matchups[week - 2].place})"
        team_2_name = f"{team_2_name} ({all_weeks[o].matchups[week - 2].place})"

    #if team 1 lost, see if they threw
    if team_1_score < team_2_score:
        if team_1_best_score > team_2_score:
            team_1_throw = "YES"
        else:
            team_1_throw = "NO"
        winner = 2
    #if team 2 lost, see if they threw
    elif team_2_score < team_1_score:
        if team_2_best_score > team_1_score:
            team_2_throw = "YES"
        else:
            team_2_throw = "NO"
        winner = 1

    #If they tied, see if either team threw
    else:
        if team_1_best_score > team_2_score:
            team_1_throw = "YES"
        else:
            team_1_throw = "NO"
        if team_2_best_score > team_1_score:
            team_2_throw = "YES"
        else:
            team_2_throw = "NO"

    return ([team_1_throw, str(team_1_accuracy) + "%", team_1_best_score, team_1_score, team_1_name, team_2_name, team_2_score, team_2_best_score, str(team_2_accuracy) + "%", team_2_throw], winner)
