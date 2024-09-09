import time

import PySimpleGUI as sg

import report_generator
import sleeper_playoffs
import sleeper_season
import sleeper_draft
from model.Stat import *
from model.SleeperLeague import SleeperLeague
from model.ScoringFormat import ScoringFormat
from requests.exceptions import HTTPError
from sleeper_wrapper import Drafts
import logging

logger = logging.getLogger()
def generate_columns(data: dict):
    layout = []
    column_1 = []
    column_2 = []
    keys = list(data.keys())
    names = list(data.values())
    middle = int(len(keys) / 2) if (len(keys) % 2) == 0 else int(len(keys) / 2) + 1
    for i in range(0, middle):
        stat_1 = names[i]
        key_1 = keys[i]
        col_1 = [sg.Text(stat_1, justification='r'), sg.Input(size=(10, 1), k=key_1)]
        column_1.append(col_1)

    for i in range(middle, len(keys)):
        stat_2 = names[i]
        key_2 = keys[i]
        col_2 = [sg.Text(stat_2, justification='r'), sg.Input(size=(10, 1), k=key_2)]
        column_2.append(col_2)
    if (len(keys) % 2) != 0:
        column_2.append([sg.Text('')])

        #input_col.append([sg.Input(size=(10,1))])
    layout += [[sg.Column(column_1, element_justification='r'), sg.Column(column_2, element_justification='r')]]
    #layout.append(input_col)
    return layout
def main():
    sleeper = None
    sg.theme('DarkAmber')  # Add a little color to your windows
    # All the stuff inside your window. This is the PSG magic code compactor...
    simple_choices = [[sg.Radio('Points per Reception (PPR)', "SimpleChoices", default=False, size=(70, 1), enable_events=True, k='PPR')],
                      [sg.Radio('0.5 points per Reception (HALF PPR)', "SimpleChoices", default=False, size=(70, 1), enable_events=True, k='HALF')],
                      [sg.Radio('Standard (STD)', "SimpleChoices", default=False, size=(70, 1), enable_events=True, k='STD')],
                      [sg.Radio('Points per First Down (PPFD)', "SimpleChoices", default=False, size=(70, 1), enable_events=True, k='PPFD')],
                      [sg.Radio('0.5 Points per Reception and 0.5 Points per First Down (HALF PPR + HALF PPFD)', "SimpleChoices", default=False, size=(70, 1), enable_events=True, k='HALF_PPFD')]]

    sub_tabs = [[sg.TabGroup([[
        sg.Tab('Passing', generate_columns(Passing_Stats)),
        sg.Tab('Rushing', generate_columns(Rushing_Stats)),
        sg.Tab('Receiving', generate_columns(Receiving_Stats)),
        sg.Tab('Kicking', generate_columns(Kicking_Stats)),
        sg.Tab('Defense', generate_columns(Defense_Stats)),
        sg.Tab('Special Teams', generate_columns(Special_Teams_Stats)),
        sg.Tab('Special Teams Players', generate_columns(Special_Teams_Player_Stats)),
        sg.Tab('IDP', generate_columns(IDP_Stats)),
        sg.Tab('Bonuses', generate_columns(Bonus_Stats)),
        sg.Tab('Misc', generate_columns(Misc_Stats)),
        sg.Tab('Punting', generate_columns(Punting_Stats))]],
        key='-TAB GROUP 2-', expand_x=True, expand_y=True)]]

    report_tab = [[sg.Checkbox('Season Statistics',  size=(20, 1), k='-SEASON_STATS-', default=True)],
                      [sg.Checkbox('Week Stats', size=(20, 1), k='-WEEK_STATS-', default=True)],
                      [sg.Checkbox('User Matchups', size=(20, 1), k='-USER_MATCHUPS-', default=True)],
                      [sg.Checkbox('Potential Seasons For Each User', size=(30, 1), k='-POTENTIAL_SEASONS-', default=True)],
                      [sg.Checkbox('Weekly Player Rankings', size=(20, 1), k='-WEEK_PLAYER_RANK-', default=True)],
                      [sg.Checkbox('Draft Report', size=(20, 1), k='-DRAFT_REPORT-', default=True)]]

    sg.set_options(font=("Arial Bold", 14))
    layout = [[sg.Text('Enter League ID:'), sg.Input(size=(20, 1), key='league_id'),
               sg.Button('Load League', key='load_league', enable_events=True),
               sg.ProgressBar(100, orientation='h', visible=False ,size=(20, 20), key='-PROGRESS BAR-')]]
    #layout += [[sg.Column([[sg.Text('Enter something on Row 1'), sg.InputText(), sg.Text('Enter something on Row 1'), sg.InputText()]], scrollable=True, size=(400, 400))]]

    sg.set_options(font=("Arial", 10))
    layout += [[sg.Checkbox('Wins Above Median', default=False, size=(70, 1), enable_events=True, k='-WINS ABOVE MEDIAN-')]]
    layout += [[sg.TabGroup([[sg.Tab('Standard Format', simple_choices), sg.Tab('Custom', sub_tabs),
                              sg.Tab('Report Options', report_tab)]], key='-TAB GROUP-', expand_x=True, expand_y=True)]]
    layout += [[sg.Button('Submit', k='submit', disabled=True ,enable_events=True)]]
    window = sg.Window('Control Panel', layout, True, grab_anywhere=True, resizable=True , finalize=True, keep_on_top=True)
    # Create the Window
    # Event Loop to process "events"
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event in ('load_league'):
            window['-PROGRESS BAR-'].update(visible=True, current_count=0, bar_color=(None, None))
            league_id = values['league_id']
            sleeper = SleeperLeague(league_id)
            if not isinstance(sleeper.league, HTTPError):
                clear_options(window)
                wins_above_median_active = True if sleeper.league['settings']['league_average_match'] == 1 else False
                window['-WINS ABOVE MEDIAN-'].update(wins_above_median_active)
                for k, v in sleeper.league['scoring_settings'].items():

                    window[k].update('')
                    window[k].update(v)
                window['-PROGRESS BAR-'].update(current_count=100, bar_color=('green', 'red'))
                window['submit'].update(disabled=False)
            else:
                window['-PROGRESS BAR-'].update(current_count=100, bar_color=('red', 'red'))
        elif event in ('PPR', 'HALF', 'STD', 'PPFD', 'HALF_PPFD'):
            scoring = ScoringFormat(event)
            for scoring_option in scoring.__dir__():
                if not scoring_option.startswith('__'):
                    window[scoring_option].update(scoring.__getattribute__(scoring_option))

        elif event in ('submit'):
            wins_above_median_active = values['-WINS ABOVE MEDIAN-']
            window['-PROGRESS BAR-'].update(visible=False)
            scoring_format = get_all_options(window)
            sleeper.update_scoring_settings(scoring_format)
            sleeper.wins_above_median_active = wins_above_median_active
            logger.info("Getting all matchup results")
            start = time.time()
            all_weeks_current_format = sleeper_season.get_all_matchup_results(sleeper, sleeper.scoring_format)
            all_potential_seasons_current_format = sleeper_season.caulculate_standings_for_all_schedules(sleeper,
                                                                                                         all_weeks_current_format)
            logger.info("All matchup results gathered [%s]", time.time() - start)
            logger.info("calculating player matchoff results")
            for user, seasons in all_potential_seasons_current_format.items():
                logger.info(
                    f"calculating playoff results for all potential seasons for user {seasons[user][user].name}")
                sleeper_playoffs.calculate_potential_playoffs_for_user(sleeper, seasons,
                                                                       sleeper.league['settings']['playoff_week_start'])

            logger.info("Calculating player statistics")
            user_statistics = sleeper_season.calculate_user_statistics(sleeper, all_weeks_current_format)
            report_generator.create_or_clear_folder(f"reports/{sleeper.league['name']}")
            if values['-SEASON_STATS-']:
                report_generator.generate_user_statistics_report(sleeper, all_weeks_current_format, user_statistics)
            if values['-WEEK_STATS-']:
                report_generator.generate_all_week_reports(sleeper, all_weeks_current_format)
            if values['-WEEK_PLAYER_RANK-']:
                report_generator.generate_player_all_week_rankings(sleeper, all_weeks_current_format)
            if values['-USER_MATCHUPS-']:
                report_generator.generate_all_user_report(sleeper, all_weeks_current_format)
            if values['-POTENTIAL_SEASONS-']:
                report_generator.generate_all_season_report(sleeper, all_potential_seasons_current_format)
            if values['-DRAFT_REPORT-']:
                drafted_players = sleeper_draft.draft_picks_by_user(sleeper.league['draft_id'])
                all_drafted_player_scores = sleeper_draft.sort_all_player_scores(sleeper)
                drafted_players = sleeper_draft.update_drafted_player_total_score(drafted_players, all_drafted_player_scores)
                drafted_players = sleeper_draft.update_drafted_player_position_rank(drafted_players, all_drafted_player_scores)
                report_generator.generate_users_draft_reports(sleeper, drafted_players)
    window.close()

def clear_options(window):
    all_stats = list(Passing_Stats.keys())
    all_stats.extend(list(Rushing_Stats.keys()))
    all_stats.extend(list(Receiving_Stats.keys()))
    all_stats.extend(list(Kicking_Stats.keys()))
    all_stats.extend(list(Defense_Stats.keys()))
    all_stats.extend(list(Special_Teams_Stats.keys()))
    all_stats.extend(list(Special_Teams_Player_Stats.keys()))
    all_stats.extend(list(IDP_Stats.keys()))
    all_stats.extend(list(Bonus_Stats.keys()))
    all_stats.extend(list(Misc_Stats.keys()))
    all_stats.extend(list(Punting_Stats.keys()))

    for key in all_stats:
        window[key].update('')

def get_all_options(window):
    all_stats = list(Passing_Stats.keys())
    all_stats.extend(list(Rushing_Stats.keys()))
    all_stats.extend(list(Receiving_Stats.keys()))
    all_stats.extend(list(Kicking_Stats.keys()))
    all_stats.extend(list(Defense_Stats.keys()))
    all_stats.extend(list(Special_Teams_Stats.keys()))
    all_stats.extend(list(Special_Teams_Player_Stats.keys()))
    all_stats.extend(list(IDP_Stats.keys()))
    all_stats.extend(list(Bonus_Stats.keys()))
    all_stats.extend(list(Misc_Stats.keys()))
    all_stats.extend(list(Punting_Stats.keys()))

    scoring_format= dict()
    for key in all_stats:
        try:
            scoring_format[key] = float(window[key].DefaultText)
        except ValueError:
            continue
    return scoring_format

main()
