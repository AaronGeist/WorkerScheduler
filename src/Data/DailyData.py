from src.Strategy.ScoreCalculation import ScoreCalculation

__author__ = 'yzhou7'

class DailyData:

    date = ''
    # key=userName, value=scoreList
    dailyScore = dict()

    def __init__(self, date, dailyScore):
        self.date = date
        self.dailyScore = dailyScore

    def addScore(self, userName, score):
        scoresForSingleUser = self.dailyScore.get(userName, list())
        scoresForSingleUser.append(score)
        self.dailyScore[userName] = scoresForSingleUser

    def addScores(self, userName, scores):
        scoresForSingleUser = self.dailyScore.get(userName, list())
        scoresForSingleUser.extend(scores)
        self.dailyScore[userName] = scoresForSingleUser

    def removeScore(self, userName, index):
        scoresForSingleUser = self.dailyScore.get(userName, list())
        if index > (len(scoresForSingleUser) - 1)\
                or index < 0:
            return False
        del scoresForSingleUser[index]
        return True

    def toStringList(self):
        result = list()
        for (userName, scoreList) in self.dailyScore.items():
            result.append([
                userName,
                " ".join(map(str, scoreList)),
                str(ScoreCalculation.calculateTotal(map(int, scoreList)))
            ])
        return result


if __name__=="__main__":
    data = DailyData("2015-01-01", dict())
    print data.date
    print data.dailyScore

    data.addScore("user1", 100)
    print data.dailyScore

    data.addScore("user1", 200)
    print data.dailyScore

    data.removeScore("user1", 2)
    print data.dailyScore

    data.removeScore("user1", -1)
    print data.dailyScore

    data.removeScore("user1", 1)
    print data.dailyScore

    data.removeScore("user2", 0)
    print data.dailyScore

    data.addScores("user2", [])
    print data.dailyScore

    data.addScores("user2", [100, 200, 300])
    print data.dailyScore

    print "start to String"
    print data.toStringList()