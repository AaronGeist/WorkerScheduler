# coding=utf-8
import random

__author__ = 'yzhou7'


class Scheduler:

    NUM_OF_WORKLOAD = 8
    # 其实是两天，但间隔为3
    MAX_REST_DAY = 3
    MAX_RETRY_TIME = 200

    def __init__(self, nameList, workLoad = NUM_OF_WORKLOAD, maxRestDay = MAX_REST_DAY):
        self.workers = nameList
        self.workLoad = int(workLoad)
        self.maxRestDay = int(maxRestDay) + 1
        pass

    def schedule(self, targetDays):

        targetDays = int(targetDays)

        randomFactor = self.maxRestDay * self.workLoad - len(self.workers)
        randomFactor = self.workLoad - randomFactor
        if randomFactor < 5:
            randomFactor = 5

        print "factor", randomFactor

        if (self.maxRestDay * self.workLoad) < len(self.workers):
            print "Cannot schedule worker"
            return dict()

        size = len(self.workers)

        resultDict = dict()
        currentDay = 1
        previousWorkerDay = [0] * size
        for i in range(0, targetDays):
            for j in range(0, self.workLoad):
                index = (j + i * self.workLoad) % size

                currentDayWorkerList = resultDict.get(currentDay, list())
                nextDayWorkerList = resultDict.get(currentDay + 1, list())

                if self.workers[index] in currentDayWorkerList:
                    minNextDay = currentDay + 1
                else:
                    minNextDay = currentDay

                previousDay = previousWorkerDay[index]
                maxNextDay = previousDay + self.maxRestDay
                if (maxNextDay < minNextDay):
                    print '########### worker', self.workers[
                        index], 'minNextDay: ', minNextDay, 'maxNextDay: ', maxNextDay
                    self.printSchedule(resultDict)
                    return dict()

                if len(nextDayWorkerList) >= (self.workLoad - randomFactor):
                    # has enough worker for next day
                    # print 'must select current'
                    selectedDay = minNextDay
                else:
                    selectedDay = random.randint(minNextDay, maxNextDay)
                previousWorkerDay[index] = selectedDay

                # print 'worker', self.workers[index], 'current', currentDay, 'min', minNextDay, 'max', maxNextDay, 'select', selectedDay
                selectedDayWorkerList = resultDict.get(selectedDay, list())
                selectedDayWorkerList.append(self.workers[index])
                resultDict[selectedDay] = selectedDayWorkerList

                if len(resultDict.get(currentDay, list())) >= self.workLoad:
                    currentDay += 1

        self.printSchedule(resultDict)
        # fill last several lines
        for (day, workerList) in resultDict.items():
            if len(workerList) == self.workLoad:
                continue
            else:
                print "refator", day
                targetDay = day - 1
                while len(workerList) != 0:
                    if targetDay > 0:
                        if resultDict.has_key(targetDay):
                            if len(resultDict[targetDay]) == self.workLoad:
                                # previous day is full, cannot move anymore
                                break
                            else:
                                resultDict[targetDay].append(workerList.pop())
                        else:
                            targetDay -= 1
                    # remove kv if no worker inside
                    if len(workerList) == 0:
                        resultDict.pop(day)

        self.printSchedule(resultDict)
        return resultDict

    def printSchedule(self, workerDict):
        for (day, idList) in workerDict.items():
            print str(day) + ": " + ", ".join(map(str, idList))

    def validateSchedule(self, workerDict):
        if workerDict:
            status = dict()
            for (currentDay, workerList) in workerDict.items():
                if len(workerList) > self.workLoad:
                    print "too many work load one day"
                    return False

                for workerId in workerList:
                    prevWorkDay = status.get(workerId, 0)
                    if (currentDay - prevWorkDay) > self.maxRestDay:
                        print '#####', workerId, ": previous is ", prevWorkDay, " but now is ", currentDay
                        return False
                    elif currentDay == prevWorkDay:
                        print '&&&&&', workerId, ": duplicated day ", prevWorkDay
                        return False
                        # else:
                        # print workerId, ": previous is ", prevWorkDay, " but now is ", currentDay
                    status[workerId] = currentDay
            print 'valid schedule'
            return True
        else:
            return False


if __name__ == "__main__":
    nameList = range(1, 24)
    count = 0
    s = Scheduler(nameList)
    while count < s.MAX_RETRY_TIME:
        count += 1
        print 'count', count
        data = s.schedule(15)
        if s.validateSchedule(data):
            # s.printSchedule(data)

            break
