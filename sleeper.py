import logging
import time
from logging.config import fileConfig

import sleeper_season
from model.ScoringFormat import ScoringFormat

import sleeper_playoffs
import report_generator

from model.SleeperLeague import SleeperLeague

fileConfig('logging_config.ini')
logger = logging.getLogger()

# def generate_all_reports():
#
# def generate_week_reports():
#
# def generate_potential_season_reports():

def main():
    logger.info("Starting")
    master_timer = time.time()
    start = time.time()
    sleeper = SleeperLeague(917999692448034816)
    logger.info("Connected to sleeper API [%s]", time.time() - start)

    #sleeper.scoring_format = ScoringFormat('HALF PPFD')

    # new_rules = {'fgm_50p': 0.0,
    #              'fgm_40_49': 0.0,
    #              'fgm_30_39': 0.0,
    #              'fgm_20_29': 0.0,
    #              'fgm_0_19': 0.0,
    #              'xpm': 0.0,
    #              'fgmiss': 0.0,
    #              'xpmiss': 0.0,
    #              'fgm_yds_over_30': 0.0
    #              }
    #
    # sleeper.update_scoring_settings(new_rules)
    logger.info("Getting all matchup results")


    regular_season_length = min(sleeper.league['settings']['leg'], sleeper.league['settings']['playoff_week_start'])
    all_weeks_current_format = sleeper_season.get_all_matchup_results(sleeper, sleeper.scoring_format)
    all_potential_seasons_current_format = sleeper_season.caulculate_standings_for_all_schedules(sleeper, all_weeks_current_format)
    logger.info("All matchup results gathered [%s]", time.time() - start)

    logger.info("calculating player matchoff results")
    for user, seasons in all_potential_seasons_current_format.items():
        logger.info(f"calculating playoff results for all potential seasons for user {seasons[user][user].name}")
        sleeper_playoffs.calculate_potential_playoffs_for_user(sleeper, seasons, sleeper.league['settings']['playoff_week_start'])

    report_generator.generate_all_week_reports(sleeper, all_weeks_current_format)
    report_generator.generate_all_user_report(sleeper, all_weeks_current_format)
    report_generator.generate_all_season_report(sleeper, all_potential_seasons_current_format)
    logger.info("Done [%s]", time.time() - master_timer)

if __name__ == '__main__':
    main()