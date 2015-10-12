__author__ = 'yzhou7'


class Week:
    def __init__(self, firstDate):
        self.monday = firstDate
        self.tuesday = firstDate + 1
        self.wednesday = firstDate + 2
        self.thrusday = firstDate + 3
        self.friday = firstDate + 4
        self.saturday = firstDate + 5
        self.sunday = firstDate + 6

    @staticmethod
    def isWeekend(date):
        return date % 7 == 6 or date % 7 == 0


if __name__ == '__main__':
    assert Week.isWeekend(5) == False
    assert Week.isWeekend(6) == True
    assert Week.isWeekend(7) == True
    assert Week.isWeekend(8) == False
