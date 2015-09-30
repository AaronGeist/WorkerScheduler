__author__ = 'yzhou7'

class ScoreCalculation:

    THRESHOLD_SUM_SCORE = 10000
    HIGH_BOUNS_RATE = 0.15
    LOW_BOUNS_RATE = 0.1

    @staticmethod
    def calculateBouns(scoreSum):
        if scoreSum >= ScoreCalculation.THRESHOLD_SUM_SCORE:
            return scoreSum * ScoreCalculation.HIGH_BOUNS_RATE
        else:
            return scoreSum * ScoreCalculation.LOW_BOUNS_RATE

    @staticmethod
    def calculateTotal(scores):
        scoreSum = sum(map(int, scores))
        return scoreSum + ScoreCalculation.calculateBouns(scoreSum)
