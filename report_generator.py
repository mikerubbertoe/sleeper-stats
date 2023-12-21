import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

from logging.config import fileConfig
from model.SleeperLeague import SleeperLeague
from model.Week import Week

fileConfig('logging_config.ini')
logger = logging.getLogger()

def generate_week_report(sleeper: SleeperLeague, all_weeks, week):
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Acual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]
    row_labels = ["Matchup 1", "Matchup 2", "Matchup 3", "Matchup 4", "Matchup 5"]
    matchup_gathered = set()
    week_results = []
    coloring = []

    for user in all_weeks.keys():
        if user not in matchup_gathered:
            player = all_weeks[user].matchups[week - 1]
            opponent = all_weeks[all_weeks[user].matchups[week - 1].opponent].matchups[week - 1]
            matchup_gathered.add(user)
            matchup_gathered.add(all_weeks[user].matchups[week - 1].opponent)
            formatted_match, winner = format_matchup(player, opponent)
            week_results.append(formatted_match)

            coloring.append(get_cell_coloring(winner, len(column_labels)))

    fig, ax = plt.subplots(1, 1, figsize=(1.4 * len(column_labels), .8 * len(week_results)))
    # creating a 2-dimensional dataframe out of the given data
    df = pd.DataFrame(week_results, columns=column_labels)

    ax.axis('tight')  # turns off the axis lines and labels
    ax.axis('off')  # changes x and y axis limits such that all data is shown

    # plotting data
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     rowLabels=row_labels,
                     rowColours=["#57b56a"] * len(row_labels),
                     colColours=["#c9673c"] * len(column_labels),
                     colWidths=[0.1] * len(column_labels),
                     loc="center",
                     cellLoc='center')

    ax.set_title(f"{sleeper.league.get_league()['name']} {sleeper.league.get_league()['season']} Week {week} (SCORING FORMAT)", y=0.830)
    plt.tight_layout()
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    #plt.subplots_adjust(left=0.2, bottom=0.1)
    table.scale(1, 2)

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])

    plt.show()

def generate_user_report(sleeper: SleeperLeague, all_weeks, user):
    column_labels = ["Thrown Week?", "Start/Sit Accuracy", "Max Points", "Acual Points", "Team 1", "Team 2",
                     "Actual Points", "Max Points", "Start/Sit Accuracy", "Thrown Week?"]
    row_labels = [f"Week {i}" for i in range(1, len(all_weeks[user].matchups) + 1)]
    week_results = []
    coloring = []

    for matchup in all_weeks[user].matchups:
        week = matchup.week
        opponent = all_weeks[all_weeks[user].matchups[week - 1].opponent].matchups[week - 1]
        formatted_match, winner = format_matchup(matchup, opponent)
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
    # plt.subplots_adjust(left=0.2, bottom=0.1)
    table.scale(1, 2)

    cellDict = table.get_celld()
    for key, cell in cellDict.items():
        row, col = key
        if row > 0 and col >= 0:
            cell.set_facecolor(coloring[row - 1][col])

    plt.show()
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
def format_matchup(player: Week, opponent: Week):
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
