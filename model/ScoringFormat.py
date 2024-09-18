import logging
from logging.config import fileConfig

logger = logging.getLogger()

class ScoringFormat:
    #defaults to STD PPR scoring
    def __init__(self, scoring_format=None, new_rules=None):
        scoring = None
        if scoring_format == 'PPR':
            logger.info("Using PPR scoring format")
            scoring = get_scoring_map()
        elif scoring_format == 'STD':
            logger.info("Using STD scoring format")
            scoring = get_std_scoring()
        elif scoring_format == 'HALF':
            logger.info("Using HALF PPR scoring format")
            scoring = get_half_ppr_scoring()
        elif scoring_format == 'PPFD':
            logger.info("Using Points Per First Down scoring format")
            scoring = get_ppfd_scoring()
        elif scoring_format == 'HALF_PPFD':
            logger.info("Using Half Points Per First Down scoring format")
            scoring = get_half_ppr_half_ppfd_scoring()
        elif new_rules is None and scoring_format is None:
            logger.warning("NO CUSTOM SCORING FORMAT FOUND. DEFAULTING TO PPR")
            scoring = get_scoring_map()

        if new_rules:
            logger.info("Adding custom scoring format")
            scoring = get_scoring_map()
            for k, v in new_rules.items():
                scoring[k] = v

        for k, v in scoring.items():
            setattr(self, k, v)

def get_scoring_map():
    scoring = dict()
    scoring['rec_yd'] = 0.1
    scoring['rec'] = 1.0
    scoring['rec_fd'] = 0.0
    scoring['rec_td'] = 6.0
    scoring['rec_2pt'] = 2.0
    scoring['rush_yd'] = 0.1
    scoring['rush_fd'] = 0.0
    scoring['rush_td'] = 6.0
    scoring['rush_2pt'] = 2.0
    scoring['pass_yd'] = 0.04
    scoring['pass_td'] = 4.0
    scoring['pass_2pt'] = 2.0
    scoring['pass_int'] = -1.0
    scoring['fum'] = 0.0
    scoring['fum_lost'] = -2.0
    scoring['st_td'] = 6.0
    scoring['fum_rec_td'] = 6.0
    scoring['blk_kick'] = 2.0
    scoring['safe'] = 2.0
    scoring['sack'] = 1.0
    scoring['def_td'] = 6.0
    scoring['def_st_td'] = 6.0
    scoring['def_st_fum_rec'] = 1.0
    scoring['st_fum_rec'] = 1.0
    scoring['fum_rec'] = 2.0
    scoring['int'] = 2.0
    scoring['ff'] = 1.0
    scoring['fgm_50p'] = 5.0
    scoring['fgm_40_49'] = 4.0
    scoring['fgm_30_39'] = 3.0
    scoring['fgm_20_29'] = 3.0
    scoring['fgm_0_19'] = 3.0
    scoring['xpm'] = 1.0
    scoring['fgmiss'] = -1.0
    scoring['xpmiss'] = -1.0
    scoring['pts_allow_35p'] = -4.0
    scoring['pts_allow_28_34'] = -1.0
    scoring['pts_allow_21_27'] = 0.0
    scoring['pts_allow_14_20'] = 1.0
    scoring['pts_allow_1_6'] = 7.0
    scoring['pts_allow_0'] = 10.0

    return scoring

def get_std_scoring():
    scoring = get_scoring_map()
    scoring['rec'] = 0.0
    return scoring

def get_half_ppr_scoring():
    scoring = get_scoring_map()
    scoring['rec'] = 0.5
    return scoring

def get_ppfd_scoring():
    scoring = get_std_scoring()
    scoring['rec_fd'] = 1.0
    scoring['rush_fd'] = 1.0
    return scoring

def get_half_ppr_half_ppfd_scoring():
    scoring = get_scoring_map()
    scoring['rec'] = 0.5
    scoring['rec_fd'] = 0.5
    scoring['rush_fd'] = 0.5
    return scoring

def get_custom_scoring(new_rules):
    scoring = get_scoring_map()
    for k, v in new_rules.items():
        scoring[k] = v
    return scoring

def get_player_score(player, week_stats, scoring_format: ScoringFormat):
    score = 0
    stats = None
    try:
        stats = week_stats[player]
    except KeyError:
        return 0

    for scoring_option in scoring_format.__dir__():
        if not scoring_option.startswith('__'):
            score += (stats.get(scoring_option, 0)) * scoring_format.__getattribute__(scoring_option)

    return score

ScoringFormat()