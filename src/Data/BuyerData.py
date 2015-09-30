__author__ = 'yzhou7'

class BuyerData:

    buyerId = 0
    buyerName = ""
    # dict{date1 : {score11, score12}, date2 : {score21, score22}}
    buyerScore = dict()

    def __init__(self, buyerId, buyerName, buyerScore):
        self.buyerId = buyerId
        self.buyerName = buyerName
        self.buyerScore = buyerScore

    def addScore(self, date, score):
        scoresForOneDay = self.buyerScore.get(date, list())
        scoresForOneDay.append(score)
        self.buyerScore[date] = scoresForOneDay

    def addScores(self, date, scores):
        scoresForOneDay = self.buyerScore.get(date, list())
        scoresForOneDay.extend(scores)
        self.buyerScore[date] = scoresForOneDay

    def removeScore(self, date, index):
        scoresForOneDay = self.buyerScore.get(date, list())
        if index > (len(scoresForOneDay) - 1)\
                or index < 0:
            return False
        del scoresForOneDay[index]
        return True

    def toStringList(self):
        result = list()

        for date in self.buyerScore.keys():
            print self.buyerScore[date]
            result.append([self.buyerId,
                           self.buyerName,
                           " ".join(map(str, self.buyerScore[date])),
                          str(sum(map(int, self.buyerScore[date])))])

        return result


if __name__=="__main__":
    data = BuyerData(0, "test", dict())
    print data.buyerId
    print data.buyerName
    print data.buyerScore

    data.addScore("123", 100)
    print data.buyerScore

    data.addScore("123", 200)
    print data.buyerScore

    data.removeScore("123", 2)
    print data.buyerScore

    data.removeScore("123", -1)
    print data.buyerScore

    data.removeScore("123", 1)
    print data.buyerScore

    data.removeScore("", 0)
    print data.buyerScore

    data.addScores("", [])
    print data.buyerScore

    data.addScores("", [100, 200, 300])
    print data.buyerScore

    print "start to String"
    print data.toStringList()