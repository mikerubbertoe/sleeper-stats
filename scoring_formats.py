from enum import Enum

class ScoringFomart(Enum):
    PPR = 'pts_ppr'
    HALF_PPR = 'pts_half_ppr'
    STD = 'pts_std'
    PPFD = 'pts_std'
    CUSTOM = 'custom'