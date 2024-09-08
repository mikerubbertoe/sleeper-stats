import sys

class SeasonStats:
    def __init__(self):
        self.overallAccuracy = 0.0
        self.opponentAccuracy = 0.0
        self.averageScore = 0.0
        self.medianScore = 0.0
        self.averageScoreStdDeviation = 0.0
        self.numberWeeksThrown = 0
        self.highestScore = 0.0
        self.highestScoreWeek = 0
        self.lowestScore = sys.float_info.max
        self.lowestScoreWeek = 0
        self.largestGapToOpponent = 0.0
        self.smallestGapToOpponent = 0.0