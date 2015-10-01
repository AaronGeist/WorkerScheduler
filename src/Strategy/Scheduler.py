# coding=utf-8
import random
from src.Data.WorkerStats import WorkerStats, ArrangedWorkDay
from src.Data.ScheduleResult import ScheduleResult

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKLOAD = 3
    MIN_WORK_DAY = 3
    MAX_WORK_DAY = 6
    MAX_RETRY_TIME = 10000
    # 保证基本公平，最多差值为delta*2
    MAX_DELTA_DAY = 1

    def __init__(self, workers, workload=NUM_OF_WORKLOAD, minWorkDay=MIN_WORK_DAY, maxWorkDay=MAX_WORK_DAY):
        self.workers = workers
        random.shuffle(self.workers)
        self.workload = int(workload)
        self.minWorkDay = int(minWorkDay)
        self.maxWorkDay = int(maxWorkDay)

    def schedule(self, targetDays):
        scheduleResult = ScheduleResult()
        targetDays = int(targetDays)
        if len(self.workers) == self.workload:
            print 'worker number equals to workload, don\'t need to schedule at all'
            scheduleResult.message = '总员工人数等于每天出勤人数，无需排班'
            return scheduleResult
        if self.minWorkDay > self.maxWorkDay:
            print 'min day > max day'
            scheduleResult.message = '最小连续出勤天数大于最大连续出勤天数，无法排班'
            return scheduleResult
        if self.minWorkDay == self.maxWorkDay:
            if len(self.workers) < self.workload * 2:
                print 'min=max but workers < workload * 2, not enough worker to handle the workload'
                scheduleResult.message = '最大最小连续出勤数相等且总员工数小于每天出勤人数的两倍，人手不足'
                return scheduleResult
            else:
                # 固定班次的话，则误差可能为固定连续出勤数
                self.MAX_DELTA_DAY = self.minWorkDay
        # 这种情况包含了上一种情况
        if len(self.workers) < self.workload * 2:
            if self.maxWorkDay < self.minWorkDay * 2:
                print 'min * 2 > max while workers < workload * 2, not enough worker to handle the workload'
                scheduleResult.message = '总员工数小于每天出勤人数的两倍，且最大连续出勤天数小于最小连续出勤天数的两倍，人手不足'
                return scheduleResult

        workerNum = len(self.workers)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(targetDays * self.workload + workerNum - 1) / workerNum

        if self.minWorkDay > targetTotalWorkDay:
            scheduleResult.message = '最小连续工时大于平均工时，不能平均安排工时'
            return scheduleResult

        retryCnt = 0
        minDelta = 99999
        unBalancedResult = dict()
        while retryCnt < self.MAX_RETRY_TIME:
            retryCnt += 1
            resultCalendar = self.doSchedule(targetDays)
            if self.validateSchedule(resultCalendar):
                currentDelta = self.getMaxDelta(resultCalendar, targetDays)
                if currentDelta <= self.MAX_DELTA_DAY:
                    print 'after', retryCnt, 'time\'s retry'

                    self.printSchedule(resultCalendar)
                    scheduleResult.message = '排班成功且工时较为平均'
                    scheduleResult.workCalendar = resultCalendar
                    scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(resultCalendar)
                    scheduleResult.restCalendar = self.getRestCalendar(resultCalendar)
                    return scheduleResult
                else:
                    # 如果不够平均，则取目前最平均的排班返回
                    if minDelta > currentDelta:
                        unBalancedResult = resultCalendar


        print 'fail to schedule after', self.MAX_RETRY_TIME, 'retries'
        self.printSchedule(unBalancedResult)
        if unBalancedResult:
            scheduleResult.message = '排班成功但没有找到工时最平均方案'
            scheduleResult.workCalendar = unBalancedResult
            scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(unBalancedResult)
            scheduleResult.restCalendar = self.getRestCalendar(resultCalendar)
        else:
            scheduleResult.message = '没有找到符合条件的排班方案，请调整参数'
        return scheduleResult


    def doSchedule(self, targetDays):

        targetDays = int(targetDays)

        workerNum = len(self.workers)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(targetDays * self.workload + workerNum - 1) / workerNum

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
                if workerStats[index].workDayLeft <= 0:
                    # 如果已经安排完所有工时，则跳过
                    continue
                elif workerStats[index].workDayLeft < self.minWorkDay:
                    # 寻找第一个未安排的日期
                    firstEmptyDate = firstTargetDate
                    # print 'current', firstTargetDate, 'finding empty date for worker', index, 'day left', workerStats[index].workDayLeft
                    while firstEmptyDate <= targetDays:
                        if len(targetCalendar.get(firstEmptyDate, list())) == 0:
                            # print 'empty date found', firstEmptyDate
                            break
                        else:
                            firstEmptyDate += 1

                    # 如果剩下的空余天数足够安排，则安排，否则照常规逻辑
                    if targetDays - firstEmptyDate >= workerStats[index].workDayLeft:
                        for i in range(0, workerStats[index].workDayLeft):
                            workerList = list()
                            workerList.append(index)
                            targetCalendar[firstEmptyDate + i] = workerList
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
                        # # 寻找第一个未安排的日期
                        # firstEmptyDate = firstTargetDate
                        # # print 'current', firstTargetDate, 'finding empty date for worker', index, 'day left', workerStats[index].workDayLeft
                        # while firstEmptyDate <= targetDays:
                        #     if len(targetCalendar.get(firstEmptyDate, list())) == 0:
                        #         # print 'empty date found', firstEmptyDate
                        #         break
                        #     else:
                        #         firstEmptyDate += 1
                        #
                        # if targetDays == firstEmptyDate:
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
                stats.workDayLeft = max(0, stats.workDayLeft - randomWorkDay)
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
                workerList = list(set(workerList))
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
                    totalDay = workerDayPerWorker.get(workerId, 0)
                    totalDay += 1
                    workerDayPerWorker[workerId] = totalDay
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
            sorted(result, key=lambda x: x[1])
            return result[0][1]

    def getRestCalendar(self, targetCalendar):
        restCalendar = dict()
        for (day, workIdList) in targetCalendar.items():
            restCalendar[day] = range(0, len(self.workers))
            for workId in workIdList:
                if workId in restCalendar[day]:
                    restCalendar[day].remove(workId)
        return restCalendar



if __name__ == "__main__":
    # workerNum = 5
    # s = Scheduler(range(1, workerNum + 1))
    #
    # targetDays = 20
    # s.schedule(targetDays)

    workerNum = 20
    s = Scheduler(range(1, workerNum + 1), 12, 3, 6)

    targetDays = 30
    s.schedule(targetDays)

