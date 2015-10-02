# coding=utf-8
import random
from src.Data.WorkerStats import WorkerStats, ArrangedWorkDay
from src.Data.ScheduleResult import ScheduleResult

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKLOAD = 3
    MIN_WORK_DAY = 3
    MAX_WORK_DAY = 6
    MAX_RETRY_TIME = 200
    # 保证基本公平，最多差值为delta*2
    MAX_DELTA_DAY = 1

    def __init__(self, workers, workload=NUM_OF_WORKLOAD, minWorkDay=MIN_WORK_DAY, maxWorkDay=MAX_WORK_DAY):
        self.workers = workers
        # TODO make it random
        # random.shuffle(self.workers)
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
            [resultCalendar, workStats] = self.doSchedule(targetDays)
            if self.validateSchedule(resultCalendar):
                currentDelta = self.getMaxDelta(resultCalendar, targetDays)
                if currentDelta <= self.MAX_DELTA_DAY:
                    print 'after', retryCnt, 'time\'s retry'

                    self.printSchedule(resultCalendar)
                    scheduleResult.message = '排班成功且工时较为平均'
                    scheduleResult.workCalendar = resultCalendar
                    scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(resultCalendar)
                    scheduleResult.restCalendar = self.getRestCalendar(resultCalendar)
                    # scheduleResult.workStats = workStats
                    return scheduleResult
                else:
                    # 如果不够平均，则取目前最平均的排班返回
                    if minDelta > currentDelta:
                        unBalancedResult = resultCalendar
                        unBalancedWorkStats = workStats

        print 'fail to schedule after', self.MAX_RETRY_TIME, 'retries'
        if unBalancedResult:
            print 'before rebalance'
            print self.calculateWorkDayPerWorker(unBalancedResult)
            self.printSchedule(unBalancedResult)
            newUnBalancedResult = self.rebalance(unBalancedResult, unBalancedWorkStats)
            print 'revalidate', self.validateSchedule(newUnBalancedResult)
            print 'after rebalance'
            print self.calculateWorkDayPerWorker(newUnBalancedResult)
            self.printSchedule(newUnBalancedResult)
            # if (self.validateSchedule(newUnBalancedResult)):
            #     scheduleResult.message = '排班成功但没有找到工时最平均方案'
            #     scheduleResult.workCalendar = newUnBalancedResult
            #     scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(newUnBalancedResult)
            #     scheduleResult.restCalendar = self.getRestCalendar(newUnBalancedResult)
            #     # scheduleResult.workStats = unBalancedWorkStats
            # else:
            #     scheduleResult.message = '尝试重新平衡化工时失败，如果不满意请重试'
            #     scheduleResult.workCalendar = unBalancedResult
            #     scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(unBalancedResult)
            #     scheduleResult.restCalendar = self.getRestCalendar(unBalancedResult)
            #     # scheduleResult.workStats = unBalancedWorkStats
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

                # 如果到末尾了，且连续天数小于最大连续天数，则一起安排了
                if targetDays - firstTargetDate + 1 <= self.maxWorkDay:
                    randomWorkDay = targetDays - firstTargetDate + 1

                # 开始日期已经找到，安排工作
                for i in range(0, randomWorkDay):
                    workerList = targetCalendar.get(firstTargetDate + i, list())
                    workerList.append(index)
                    targetCalendar[firstTargetDate + i] = workerList

                stats = workerStats.get(index)
                stats.workDayLeft = max(0, stats.workDayLeft - randomWorkDay)
                stats.arrangedWorkDay.append(
                    ArrangedWorkDay(firstTargetDate, min(firstTargetDate + randomWorkDay - 1, targetDays)))

            # 如果所有人的剩余工作天数都为0，则结束
            if sum(map(lambda x: x.workDayLeft, workerStats.values())) == 0:
                break

        # 去除超过targetDay的安排
        currentSize = len(targetCalendar)
        if currentSize > targetDays:
            for i in range(targetDays + 1, currentSize + 1):
                del targetCalendar[i]

        return [targetCalendar, workerStats]

    def printSchedule(self, targetCalendar):
        for (day, workerIdList) in targetCalendar.items():
            print str(day) + ": " + ", ".join(map(str, map(lambda id: self.workers[id], workerIdList)))

    def validateSchedule(self, targetCalendar):
        if targetCalendar:
            workerStats = dict()
            for (currentDate, workerList) in targetCalendar.items():
                workerList = list(set(workerList))
                if len(workerList) != self.workload:
                    print 'date', currentDate, 'is not full'
                    return False

                for worker in workerList:
                    stats = workerStats.get(worker, WorkerStats(worker, 0))

                    if currentDate == (stats.previousDate + 1) or stats.previousDate == -1:
                        # 连续两天上班或第一天上班
                        stats.accumulatedWorkDay += 1
                        if stats.accumulatedWorkDay > self.maxWorkDay:
                            print "date", currentDate, "worker", worker, "exceed max work day", self.maxWorkDay
                            return False
                    else:
                        # 中间有休息
                        if stats.accumulatedWorkDay < self.minWorkDay and currentDate != 1:
                            print 'date', stats.previousDate, 'worker', worker, 'doesn\'t meet minWorkDay', self.minWorkDay
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

    def rebalance(self, targetCalendar, workStats):

        workerDayPerWorker = self.calculateWorkDayPerWorker(targetCalendar)
        targetDays = len(targetCalendar)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(targetDays * self.workload + len(self.workers) - 1) / len(self.workers)

        newWorkerDayPerWorker = sorted(workerDayPerWorker.iteritems(), key=lambda d: d[1])

        size = len(workerDayPerWorker)
        for index in range(0, size):
            if newWorkerDayPerWorker[index][1] >= targetTotalWorkDay:
                break
            targetWorkerId = newWorkerDayPerWorker[index][0]
            iterateOnlyArrangedWorkDay = workStats[targetWorkerId].arrangedWorkDay[:]
            for arrangedWorkDay in iterateOnlyArrangedWorkDay:
                startDate = arrangedWorkDay.startDate
                endDate = arrangedWorkDay.endDate
                print 'start analysis worker', targetWorkerId, 'from', startDate, 'to', endDate

                # 在前一天寻找可以替换的，换成自己
                if startDate != 1:
                    for workerId in targetCalendar.get(startDate - 1, list()):
                        # 不能增大，否则大于最大连续
                        if endDate - startDate + 2 > self.maxWorkDay:
                            break
                        if targetWorkerId in targetCalendar.get(startDate - 1, list()):
                            # 放止重复替换
                            break
                        if workerDayPerWorker[workerId] > targetTotalWorkDay + 1:
                            # 不要把两个连续出勤连接成一个（或者继续检查连成一个后是否超最大）
                            if targetWorkerId not in targetCalendar.get(startDate - 2, list()):
                                if workerId not in targetCalendar.get(startDate, list()):
                                    for innerPair in workStats[workerId].arrangedWorkDay:
                                        targetStartDate = startDate - 1
                                        if targetStartDate == innerPair.endDate:
                                            # 防止缩短后小于最小连续天数
                                            if innerPair.endDate - innerPair.startDate < self.minWorkDay:
                                                continue
                                            print 'start', startDate, 'end', endDate
                                            print 'inner start', innerPair.startDate, 'end', innerPair.endDate
                                            targetCalendar[targetStartDate].remove(workerId)
                                            targetCalendar[targetStartDate].append(targetWorkerId)
                                            workerDayPerWorker[workerId] = workerDayPerWorker[workerId] - 1
                                            workerDayPerWorker[targetWorkerId] = workerDayPerWorker[targetWorkerId] + 1
                                            newInnerPair = innerPair
                                            newInnerPair.endDate -= 1
                                            workStats[workerId].arrangedWorkDay.remove(innerPair)
                                            workStats[workerId].arrangedWorkDay.append(newInnerPair)
                                            for day in workStats[workerId].arrangedWorkDay:
                                                if day.startDate == startDate and day.endDate:
                                                    workStats[workerId].arrangedWorkDay.remove(day)
                                                    break
                                            workStats[targetWorkerId].arrangedWorkDay.append(ArrangedWorkDay(targetStartDate, endDate))

                                            print 'targetStartDate1', targetStartDate, 'old id', self.workers[
                                                workerId], 'new id', self.workers[targetWorkerId]
                                            startDate = targetStartDate
                                            break
                                elif workerId in targetCalendar.get(startDate - 1,
                                                                    list()) and workerId not in targetCalendar.get(
                                            startDate - 2, list()):
                                    # 和当前id并存，并比当前ID早一天开始
                                    for innerPair in workStats[workerId].arrangedWorkDay:
                                        targetStartDate = startDate - 1
                                        if targetStartDate == innerPair.startDate:
                                            if innerPair.endDate - innerPair.startDate < self.minWorkDay:
                                                continue
                                            print 'start', startDate, 'end', endDate
                                            print 'inner start', innerPair.startDate, 'end', innerPair.endDate
                                            targetCalendar[targetStartDate].remove(workerId)
                                            targetCalendar[targetStartDate].append(targetWorkerId)
                                            workerDayPerWorker[workerId] = workerDayPerWorker[workerId] - 1
                                            workerDayPerWorker[targetWorkerId] = workerDayPerWorker[targetWorkerId] + 1
                                            newInnerPair = innerPair
                                            newInnerPair.startDate += 1
                                            workStats[workerId].arrangedWorkDay.remove(innerPair)
                                            workStats[workerId].arrangedWorkDay.append(newInnerPair)
                                            newArrangedWorkDay = arrangedWorkDay
                                            newArrangedWorkDay.startDate = targetStartDate
                                            for day in workStats[workerId].arrangedWorkDay:
                                                if day.startDate == startDate and day.endDate:
                                                    workStats[workerId].arrangedWorkDay.remove(day)
                                                    break
                                            workStats[targetWorkerId].arrangedWorkDay.append(ArrangedWorkDay(targetStartDate, endDate))

                                            print 'targetStartDate2', endDate + 1, 'old id', self.workers[
                                                workerId], 'new id', self.workers[targetWorkerId]
                                            startDate = targetStartDate
                                            break

                # 在后一天寻找可以替换的
                if endDate != targetDays:
                    for workerId in targetCalendar.get(endDate + 1, list()):
                        # 不能增大，否则大于最大连续
                        if endDate - startDate + 2 > self.maxWorkDay:
                            break
                        if targetWorkerId in targetCalendar.get(endDate + 1, list()):
                            # 放止重复替换
                            break
                        if workerDayPerWorker[workerId] > targetTotalWorkDay + 1:
                            # 不要把两个连续出勤连接成一个（或者继续检查连成一个后是否超最大）
                            if targetWorkerId not in targetCalendar.get(endDate + 2, list()):
                                if workerId not in targetCalendar.get(endDate, list()):
                                    for innerPair in workStats[workerId].arrangedWorkDay:
                                        targetEndDate = endDate + 1
                                        if targetEndDate == innerPair.startDate:
                                            if innerPair.endDate - innerPair.startDate < self.minWorkDay:
                                                continue
                                            print 'start', startDate, 'end', endDate
                                            print 'inner start', innerPair.startDate, 'end', innerPair.endDate
                                            targetCalendar[targetEndDate].remove(workerId)
                                            targetCalendar[targetEndDate].append(targetWorkerId)
                                            workerDayPerWorker[workerId] = workerDayPerWorker[workerId] - 1
                                            workerDayPerWorker[targetWorkerId] = workerDayPerWorker[targetWorkerId] + 1
                                            newInnerPair = innerPair
                                            newInnerPair.startDate += 1
                                            workStats[workerId].arrangedWorkDay.remove(innerPair)
                                            workStats[workerId].arrangedWorkDay.append(newInnerPair)
                                            for day in workStats[workerId].arrangedWorkDay:
                                                if day.startDate == startDate and day.endDate:
                                                    workStats[workerId].arrangedWorkDay.remove(day)
                                                    break
                                            workStats[targetWorkerId].arrangedWorkDay.append(ArrangedWorkDay(startDate, targetEndDate))
                                            print 'targetEndDate1', targetEndDate, 'old id', self.workers[
                                                workerId], 'new id', self.workers[targetWorkerId]
                                            endDate = targetEndDate
                                            break
                                elif workerId in targetCalendar.get(endDate + 1,
                                                                    list()) and workerId not in targetCalendar.get(
                                            endDate + 2, list()):
                                    # 和当前id并存，并比当前ID多一天
                                    for innerPair in workStats[workerId].arrangedWorkDay:
                                        targetEndDate = endDate + 1
                                        if targetEndDate == innerPair.endDate:
                                            if innerPair.endDate - innerPair.startDate < self.minWorkDay:
                                                continue
                                            print 'start', startDate, 'end', endDate
                                            print 'inner start', innerPair.startDate, 'end', innerPair.endDate
                                            targetCalendar[targetEndDate].remove(workerId)
                                            targetCalendar[targetEndDate].append(targetWorkerId)
                                            workerDayPerWorker[workerId] = workerDayPerWorker[workerId] - 1
                                            workerDayPerWorker[targetWorkerId] = workerDayPerWorker[targetWorkerId] + 1
                                            newInnerPair = innerPair
                                            newInnerPair.endDate -= 1
                                            workStats[workerId].arrangedWorkDay.remove(innerPair)
                                            workStats[workerId].arrangedWorkDay.append(newInnerPair)
                                            for day in workStats[workerId].arrangedWorkDay:
                                                if day.startDate == startDate and day.endDate:
                                                    workStats[workerId].arrangedWorkDay.remove(day)
                                                    break
                                            workStats[targetWorkerId].arrangedWorkDay.append(ArrangedWorkDay(startDate, targetEndDate))
                                            print 'targetEndDate2', endDate + 1, 'old id', self.workers[
                                                workerId], 'new id', self.workers[targetWorkerId]
                                            endDate = targetEndDate
                                            break

        return targetCalendar


if __name__ == "__main__":
    # workerNum = 5
    # s = Scheduler(range(1, workerNum + 1))
    #
    # targetDays = 20
    # s.schedule(targetDays)

    workerNum = 20
    s = Scheduler(range(1, workerNum + 1), 12, 3, 7)

    targetDays = 30
    s.schedule(targetDays)
