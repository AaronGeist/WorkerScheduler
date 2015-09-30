# coding=utf-8
import random
from src.Data.WorkerStats import WorkerStats, ArrangedWorkDay

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKLOAD = 3
    MIN_WORK_DAY = 3
    MAX_WORK_DAY = 6
    MAX_RETRY_TIME = 20000
    # 保证基本公平，最多差值为delta*2
    MAX_DELTA_DAY = 1

    def __init__(self, workers, workload=NUM_OF_WORKLOAD, minWorkDay=MIN_WORK_DAY, maxWorkDay=MAX_WORK_DAY):
        self.workers = workers
        random.shuffle(self.workers)
        self.workload = int(workload)
        self.minWorkDay = int(minWorkDay)
        self.maxWorkDay = int(maxWorkDay)

    def schedule(self, targetDays):
        targetDays = int(targetDays)
        if len(self.workers) == self.workload:
            print 'worker number equals to workload, don\'t need to schedule at all'
            return False
        if self.minWorkDay > self.maxWorkDay:
            print 'min day > max day'
            return False
        if self.minWorkDay == self.maxWorkDay:
            if len(self.workers) < self.workload * 2:
                print 'min=max but workers < workload * 2, not enough worker to handle the workload'
                return False
            else:
                # 固定班次的话，则误差可能为固定连续出勤数
                self.MAX_DELTA_DAY = self.minWorkDay

        retryCnt = 0
        minDelta = self.MAX_WORK_DAY
        unBalancedResult = dict()
        while retryCnt < self.MAX_RETRY_TIME:
            retryCnt += 1
            result = self.doSchedule(targetDays)
            if self.validateSchedule(result):
                currentDelta = self.getMaxDelta(result, targetDays)
                if currentDelta <= self.MAX_DELTA_DAY:
                    print 'after', retryCnt, 'time\'s retry'
                    self.printSchedule(result)
                    print self.calculateWorkDayPerWorker(result)
                    return result
                else:
                    # 如果不够平均，则取目前最平均的排班返回
                    if minDelta > currentDelta:
                        unBalancedResult = result

        else:
            print 'fail to schedule after', self.MAX_RETRY_TIME, 'retries'
            self.printSchedule(result)
            print self.calculateWorkDayPerWorker(result)
            return unBalancedResult


    def doSchedule(self, targetDays):

        emptyResult = dict()

        targetDays = int(targetDays)

        workerNum = len(self.workers)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(targetDays * self.workload + workerNum - 1) / workerNum

        if self.minWorkDay > targetTotalWorkDay:
            print "最小连续工时大于平均工时，不能平均安排工时"
            return emptyResult

        firstTargetDate = 1

        # 字典格式为key=日期，value=list of worker
        targetCalendar = dict()

        # 结构为key=员工号，value=[剩余工作天数，[之前工作天数起始值]]
        workerStats = dict()
        for i in range(0, workerNum):
            workerStats[i] = WorkerStats(i, targetTotalWorkDay)

        stopFlag = False
        while not stopFlag:
            # 遍历每个worker，安排工作日期
            for index in range(0, workerNum):
                # 如果已经安排完所有工时，则跳过
                if workerStats[index].workDayLeft == 0:
                    continue

                # 在最大连续和最小连续之间随机选数
                randomWorkDay = random.randint(self.minWorkDay, self.maxWorkDay)

                # print "current worker", index, "current day", firstTargetDate, 'workday length', randomWorkDay

                # 找到最早的没有安排该员工工作，且没有满员的日期
                while firstTargetDate <= targetDays:
                    workerList = targetCalendar.get(firstTargetDate, list())
                    if len(workerList) == self.workload:
                        # 当前天已经满了，加1
                        firstTargetDate += 1
                        continue

                    # 该员工已经在这天安排了工作
                    if index in workerList:
                        # TODO 找到最早的没有安排该员工工作的日期
                        pass

                    break

                # 如果while循环到了末尾没成功,则退出（可能是因为不需要再安排了？）
                if firstTargetDate > targetDays:
                    # print "Cannot find empty day for worker", self.workers[index]
                    stopFlag = True
                    break

                # 开始日期已经找到，安排工作
                for i in range(0, randomWorkDay):
                    workerList = targetCalendar.get(firstTargetDate + i, list())
                    workerList.append(index)
                    targetCalendar[firstTargetDate + i] = workerList

                stats = workerStats.get(index)
                stats.workDayLeft -= randomWorkDay
                # TODO should use this data
                stats.arrangedWorkDay.append(ArrangedWorkDay(firstTargetDate, firstTargetDate + randomWorkDay))

            # 如果所有人的剩余工作天数都为0，则结束
            if sum(map(lambda x: x.workDayLeft, workerStats.values())) == 0:
                break

        # 去除超过targetDay的安排
        currentSize = len(targetCalendar)
        if currentSize > targetDays:
            for i in range(targetDays + 1, currentSize + 1):
                del targetCalendar[i]

        return targetCalendar

    def printSchedule(self, targetCalendar):
        for (day, workerIdList) in targetCalendar.items():
            print str(day) + ": " + ", ".join(map(str, map(lambda id: self.workers[id], workerIdList)))

    def validateSchedule(self, targetCalendar):
        if targetCalendar:
            workerStats = dict()
            for (currentDate, workerList) in targetCalendar.items():
                if len(workerList) != self.workload:
                    return False

                for worker in workerList:
                    stats = workerStats.get(worker, WorkerStats(worker, 0))

                    # print '1 current date', currentDate, 'worker', worker,'prevDate', stats.previousDate, 'accumulate',\
                    #             stats.accumulatedWorkDay

                    if currentDate == (stats.previousDate + 1) or stats.previousDate == -1:
                        # 连续两天上班或第一天上班
                        stats.accumulatedWorkDay += 1
                        if stats.accumulatedWorkDay > self.maxWorkDay:
                            # print "date", currentDate, "worker", worker, "exceed max work day", self.maxWorkDay
                            return False
                    else:
                        # 中间有休息
                        if stats.accumulatedWorkDay < self.minWorkDay and currentDate != 1:
                            return False
                        # 重置为1
                        stats.accumulatedWorkDay = 1

                    stats.totalWorkDay += 1
                    stats.previousDate = currentDate

                    workerStats[worker] = stats
            return True
        else:
            # 排班为空
            print 'empty calendar'
            return False

    def calculateWorkDayPerWorker(self, targetCalendar):
        if targetCalendar:
            workerDayPerWorker = dict()
            for (currentDate, workerIdList) in targetCalendar.items():
                for workerId in workerIdList:
                    totalDay = workerDayPerWorker.get(self.workers[workerId], 0)
                    totalDay += 1
                    workerDayPerWorker[self.workers[workerId]] = totalDay
            return workerDayPerWorker

        else:
            return dict()

    def getMaxDelta(self, targetCalendar, targetDays):
        workerDayPerWorker = self.calculateWorkDayPerWorker(targetCalendar)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(targetDays * self.workload + len(self.workers) - 1) / len(self.workers)
        result = filter(lambda (x, y): abs(y - targetTotalWorkDay) > self.MAX_DELTA_DAY, workerDayPerWorker.items())
        if len(result) == 0:
            # 已经达到要求
            return self.MAX_DELTA_DAY
        else:
            result.sort()
            return result.pop()



if __name__ == "__main__":
    # workerNum = 5
    # s = Scheduler(range(1, workerNum + 1))
    #
    # targetDays = 20
    # s.schedule(targetDays)

    workerNum = 7
    s = Scheduler(range(1, workerNum + 1), 4, 3, 5)

    targetDays = 30
    s.schedule(targetDays)

