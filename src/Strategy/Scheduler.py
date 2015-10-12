# coding=utf-8
from copy import copy
import math
from random import randint
from wx.core import wx

from src.Data.Week import Week
from src.Data.WorkerStats import WorkerStats
from src.Data.ScheduleResult import ScheduleResult

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKER_REQUIRED_PER_DAY = 3
    MIN_REST_DAY = 1
    MAX_REST_DAY = 3
    # 最大连续工作天数，可选
    MAX_WORK_DAY = 7
    MAX_RETRY_TIME = 1000
    # 保证基本公平，最多差值为delta*2
    MAX_DELTA_DAY = 1

    def __init__(self, workers, workerNumRequired=NUM_OF_WORKER_REQUIRED_PER_DAY, maxRestDay=MAX_REST_DAY):
        self.workerList = workers
        # random.shuffle(self.workerList)
        self.totalWorkerNum = len(self.workerList)
        self.workerNumRequired = int(workerNumRequired)
        self.minRestDay = self.MIN_REST_DAY
        self.maxRestDay = int(maxRestDay)
        self.dailyRestWorkerNum = self.totalWorkerNum - self.workerNumRequired

    def schedule(self, totalScheduleDays):
        scheduleResult = ScheduleResult()
        totalScheduleDays = int(totalScheduleDays)
        if totalScheduleDays % 7 != 0:
            print('totalScheduleDays % 7 != 0')
            scheduleResult.message = u'排班周期必须为7的倍数'
            return scheduleResult
        if self.totalWorkerNum < self.workerNumRequired:
            print('worker number less than workload, cannot schedule')
            scheduleResult.message = u'总员工人数小于每天休息人数，无法排班'
            return scheduleResult
        if self.totalWorkerNum == self.workerNumRequired:
            print('worker number equals to workload, don\'t need to schedule at all')
            scheduleResult.message = u'总员工人数等于每天休息人数，无需排班'
            return scheduleResult
        if self.minRestDay > self.maxRestDay:
            print('min day > max day')
            scheduleResult.message = u'最小连续休息天数大于最大连续休息天数，无法排班'
            return scheduleResult
        try:
            [restCalendar, workStats] = self.doSchedule(totalScheduleDays)
            if not self.validateSchedule(restCalendar):
                scheduleResult.message = u'没有找到符合条件的排班方案，请调整参数'
            else:
                scheduleResult.restCalendar = restCalendar
                scheduleResult.workCalendar = self.getWorkCalendar(restCalendar)
                scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(scheduleResult.workCalendar)
                scheduleResult.message = u'排班成功'
        except:
            scheduleResult.message = u'遇到未知错误，没有找到符合条件的排班方案，请调整参数'

        return scheduleResult

                # if self.minRestDay == self.maxRestDay:
                #     if self.totalWorkerNum < self.workerNumRequired * 2:
                #         print('min=max but workers < workload * 2, not enough worker to handle the workload')
                #         scheduleResult.message = u'最大最小连续休息数相等且总员工数小于每天休息人数的两倍，人手不足'
                #         return scheduleResult
                #     else:
                #         # 固定班次的话，则误差可能为固定连续休息数
                #         self.MAX_DELTA_DAY = self.minRestDay
                # # 这种情况包含了上一种情况
                # if self.totalWorkerNum < self.workerNumRequired * 2:
                #     if self.maxRestDay < self.minRestDay * 2:
                #         print('min * 2 > max while workers < workload * 2, not enough worker to handle the workload')
                #         scheduleResult.message = u'总员工数小于每天休息人数的两倍，且最大连续休息天数小于最小连续休息天数的两倍，人手不足'
                #         return scheduleResult

                # # 平均工时每人（天）,向上取整
                # targetTotalWorkDay = int(totalScheduleDays * self.workerNumRequired + self.totalWorkerNum - 1) / self.totalWorkerNum
                # # 平均每人休息天数
                #
                # if self.minRestDay > targetTotalWorkDay:
                #     scheduleResult.message = u'最小连续工时大于平均工时，不能平均安排工时'
                #     return scheduleResult
                #
                # retryCnt = 0
                # minDelta = 99999
                # unBalancedResult = dict()
                # while retryCnt < self.MAX_RETRY_TIME:
                #     retryCnt += 1
                #     [resultCalendar, workStats] = self.doSchedule(totalScheduleDays)
                #     # self.printSchedule(resultCalendar)
                #     if self.validateSchedule(resultCalendar):
                #         currentDelta = self.getMaxDelta(resultCalendar, totalScheduleDays)
                #         if currentDelta <= self.MAX_DELTA_DAY:
                #             print('after', retryCnt, 'time\'s retry')
                #             self.printSchedule(resultCalendar)
                #             scheduleResult.message = u'排班成功且工时较为平均'
                #             scheduleResult.workCalendar = resultCalendar
                #             scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(resultCalendar)
                #             scheduleResult.restCalendar = self.getRestCalendar(resultCalendar)
                #             # scheduleResult.workStats = workStats
                #             return scheduleResult
                #         else:
                #             # 如果不够平均，则取目前最平均的排班返回
                #             print('minDelta', minDelta, 'current', currentDelta)
                #             if minDelta > currentDelta:
                #                 unBalancedResult = resultCalendar
                #                 unBalancedWorkStats = workStats
                #                 minDelta = currentDelta
                #
                # print('fail to schedule after', self.MAX_RETRY_TIME, 'retries')
                # if unBalancedResult:
                #     # print('before rebalance'
                #     # print('delta', self.getMaxDelta(unBalancedResult, targetDays)
                #     # print(self.calculateWorkDayPerWorker(unBalancedResult)
                #     # self.printSchedule(unBalancedResult)
                #     newUnBalancedResult = self.rebalance(unBalancedResult, unBalancedWorkStats)
                #     # print('revalidate', self.validateSchedule(newUnBalancedResult)
                #     # print('after rebalance'
                #     # print('new delta', self.getMaxDelta(newUnBalancedResult, targetDays)
                #     # print(self.calculateWorkDayPerWorker(newUnBalancedResult)
                #     # self.printSchedule(newUnBalancedResult)
                #     if (self.validateSchedule(newUnBalancedResult)):
                #         scheduleResult.message = u'排班成功但没有找到工时最平均方案'
                #         scheduleResult.workCalendar = newUnBalancedResult
                #         scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(newUnBalancedResult)
                #         scheduleResult.restCalendar = self.getRestCalendar(newUnBalancedResult)
                #         # scheduleResult.workStats = unBalancedWorkStats
                #     else:
                #         scheduleResult.message = u'尝试重新平衡化工时失败，如果不满意请重试'
                #         scheduleResult.workCalendar = unBalancedResult
                #         scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(unBalancedResult)
                #         scheduleResult.restCalendar = self.getRestCalendar(unBalancedResult)
                #         # scheduleResult.workStats = unBalancedWorkStats
                # else:
                #     print('empty unbalanceResult')
                #     scheduleResult.message = u'没有找到符合条件的排班方案，请调整参数'
                # return scheduleResult

    # 每周最大连续休息天数（只限于周内）
    # 最大连续工作不超过7天（可选）
    # 保持在周末休息的天数平均
    # 连续工作，连续休息
    def doSchedule(self, totalScheduleDays):

        totalScheduleDays = int(totalScheduleDays)
        print('totalScheduleDays', totalScheduleDays)
        totalWeekNum = math.ceil(totalScheduleDays / 7)
        print('totalWeekNum', totalWeekNum)
        restFactor = float(self.totalWorkerNum - self.workerNumRequired) / self.totalWorkerNum
        print('restFactor', restFactor)
        # 平均每人每周休息天数，向上取整
        averageWeeklyRestDay = int(math.ceil(float(7) * restFactor))
        print('averageWeeklyRestDay', averageWeeklyRestDay)
        # # 平均每人每周可以休息的周末天数，向上取整（取值范围是1-2）
        # averageWeeklyWeekend = max(1, int(math.ceil(float(2) * restFactor)))
        # print('averageWeeklyWeekend', averageWeeklyWeekend)

        # 周期内每人总休假天数(休完为止）
        totalRestDayNum = math.ceil(totalWeekNum * 7 * restFactor)
        print('totalRestDayNum', totalRestDayNum)

        # 周期内每人总周末休假数
        totalWeekendDayNum = math.ceil(totalWeekNum * 2 * restFactor)
        print('totalWeekendDayNum', totalWeekendDayNum)

        print('>>>>>>> finish init')

        # 字典格式为key=日期，value=list of rest worker
        restCalendar = dict()
        for date in range(1, totalScheduleDays + 1):
            restCalendar[date] = list()
        # 结构为key=员工号，value=[剩余工作天数，[之前工作天数起始值]]
        overallWorkerStats = dict()
        for index in range(self.totalWorkerNum):
            overallWorkerStats[index] = WorkerStats(index, totalRestDayNum, totalWeekendDayNum)

        # 周末休息天数的缺口
        weekendNotEnoughNum = totalWeekendDayNum * self.totalWorkerNum - totalWeekNum * 2 * (
            self.totalWorkerNum - self.workerNumRequired)
        print('weekendNotEnoughNum', weekendNotEnoughNum)
        assert weekendNotEnoughNum >= 0
        weekendRandomList = self.workerList[:]
        assert weekendNotEnoughNum < len(weekendRandomList)
        # 乱序后取出前N名员工，每个人减1
        # random.shuffle(weekendRandomList)
        print(weekendRandomList)
        for i in range(weekendNotEnoughNum):
            overallWorkerStats[weekendRandomList[i]].restWeekendLeftNum -= 1

        for (k, v) in overallWorkerStats.items():
            print('worker', k, 'restWeekendLeftNum', v.restWeekendLeftNum)

        # 总休息天数的缺口
        restDayNotEnoughNum = totalRestDayNum * self.totalWorkerNum - totalWeekNum * 7 * (
            self.totalWorkerNum - self.workerNumRequired)
        print('restDayNotEnoughNum', restDayNotEnoughNum)
        assert restDayNotEnoughNum >= 0
        workdayRandomList = self.workerList[:]
        assert restDayNotEnoughNum <= len(workdayRandomList)
        # random.shuffle(workdayRandomList)
        # 乱序后取出前N名员工，每个人减1
        print(workdayRandomList)
        for i in range(restDayNotEnoughNum):
            overallWorkerStats[workdayRandomList[i]].restDayLeftNum -= 1
        for (k, v) in overallWorkerStats.items():
            print('worker', k, 'restDayLeftNum', v.restDayLeftNum)

        # 首先安排周末休息人员
        currentWorkerIndex = 0
        for weekNum in range(totalWeekNum):
            week = Week(weekNum * 7 + 1)

            fullWeekend = False
            cycle = 0
            while not fullWeekend:
                # 如果多余几个空格没法填满，则找到被减少休息天的前N个人填补
                if cycle > self.dailyRestWorkerNum * 3:
                    for i in weekendRandomList:
                        if self.isArrangable(i, week.sunday, restCalendar, overallWorkerStats, self.dailyRestWorkerNum):
                            self.arrange(i, week.sunday, restCalendar, overallWorkerStats)
                        elif self.isArrangable(i, week.saturday, restCalendar, overallWorkerStats,
                                               self.dailyRestWorkerNum):
                            self.arrange(i, week.saturday, restCalendar, overallWorkerStats)

                if self.isArrangable(currentWorkerIndex, week.sunday, restCalendar, overallWorkerStats,
                                     self.dailyRestWorkerNum) \
                        and overallWorkerStats[currentWorkerIndex].restWeekendLeftNum > 0:
                    self.arrange(currentWorkerIndex, week.sunday, restCalendar, overallWorkerStats)
                if self.isArrangable(currentWorkerIndex, week.saturday, restCalendar, overallWorkerStats,
                                     self.dailyRestWorkerNum) \
                        and overallWorkerStats[currentWorkerIndex].restWeekendLeftNum > 0:
                    self.arrange(currentWorkerIndex, week.saturday, restCalendar, overallWorkerStats)

                currentWorkerIndex = (currentWorkerIndex + 1) % self.totalWorkerNum

                if len(restCalendar[week.saturday]) == self.dailyRestWorkerNum \
                        and len(restCalendar[week.sunday]) == self.dailyRestWorkerNum:
                    fullWeekend = True
                else:
                    cycle += 1

        print('>>>>>>>>>>>>>>> arranged rest day is:')
        for (k, v) in overallWorkerStats.items():
            print('worker', k, 'arranged rest day', v.arrangedRestDay)
        for (k, v) in overallWorkerStats.items():
            print('worker', k, 'restDayLeftNum', v.restDayLeftNum)

        for weekNum in range(totalWeekNum):
            print(">>>>>>>>>>>> scheduling week No." + str(weekNum))

            weeklyWorkerStats = dict()
            for index in range(self.totalWorkerNum):
                weeklyWorkerStats[index] = WorkerStats(index, min(overallWorkerStats[index].restDayLeftNum,
                                                                  averageWeeklyRestDay), -1)

            week = Week(weekNum * 7 + 1)
            sundayArrange = restCalendar[week.sunday]
            saturdayArrange = restCalendar[week.saturday]
            for workerIndex in sundayArrange:
                weeklyWorkerStats[workerIndex].restDayLeftNum -= 1
                weeklyWorkerStats[workerIndex].previousRestEndDate = week.sunday
                weeklyWorkerStats[workerIndex].accumulatedRestDayNum += 1
            for workerIndex in saturdayArrange:
                weeklyWorkerStats[workerIndex].restDayLeftNum -= 1
                weeklyWorkerStats[workerIndex].previousRestEndDate = week.saturday
                weeklyWorkerStats[workerIndex].accumulatedRestDayNum += 1

                if workerIndex not in sundayArrange and weeklyWorkerStats[workerIndex].restDayLeftNum > 0:
                    # 如果周六安排了,周日没安排，并且有剩余休息，则优先安排周五
                    self.arrange(workerIndex, week.friday, restCalendar, weeklyWorkerStats)

            # 正式开始排工作日
            weekendWorkerList = list(set(sundayArrange + saturdayArrange))
            print('weekendWorkerList', weekendWorkerList)
            fullWeek = False
            while not fullWeek:
                workerList = range(self.totalWorkerNum)
                workerList = list(filter(lambda x: x not in weekendWorkerList, workerList))
                workerList += weekendWorkerList
                for workerIndex in workerList:
                    currentDate = week.friday
                    while weeklyWorkerStats[workerIndex].restDayLeftNum > 0 and currentDate >= week.monday:
                        if self.isArrangable(workerIndex, currentDate, restCalendar, weeklyWorkerStats,
                                             self.dailyRestWorkerNum) \
                                and weeklyWorkerStats[workerIndex].restDayLeftNum > 0:
                            self.arrange(workerIndex, currentDate, restCalendar, weeklyWorkerStats)

                        # currentDate -= random.randint(1, 2)
                        currentDate -= 1

                    if currentDate <= week.monday - 1:
                        fullWeek = True

            # weekendWorkerList = list(set(sundayArrange + saturdayArrange))
            # print('weekendWorkerList', weekendWorkerList)
            # fullWeek = False
            # currentDate = week.friday
            # while not fullWeek:
            #     workerList = range(self.totalWorkerNum)
            #     workerList = list(filter(lambda x: x not in weekendWorkerList, workerList))
            #     workerList += weekendWorkerList
            #     for workerIndex in workerList:
            #         randomRestNum = randint(2, self.maxRestDay)
            #         for d in range(max(1, currentDate - randomRestNum + 1), currentDate + 1).__reversed__():
            #             if self.isArrangable(workerIndex, d, restCalendar, weeklyWorkerStats,
            #                                  self.dailyRestWorkerNum) \
            #                     and weeklyWorkerStats[workerIndex].restDayLeftNum > 0:
            #                 self.arrange(workerIndex, d, restCalendar, weeklyWorkerStats)
            #             else:
            #                 break
            #
            #     if len(restCalendar[currentDate]) == self.dailyRestWorkerNum:
            #         currentDate -= 1
            #
            #     if currentDate < week.monday:
            #         break


            self.formatCalendar(restCalendar)

            workerIndexLeft = list()
            for index in range(self.totalWorkerNum):
                print('worker', index, 'weekRestDayLeftNum', weeklyWorkerStats[index].restDayLeftNum)
                # FIXME 只选取有剩余的
                # if weeklyWorkerStats[index].restDayLeftNum > 0:
                #     workerIndexLeft.append([index, weeklyWorkerStats[index].restDayLeftNum])
                # 选取所有可能
                workerIndexLeft.append([index, weeklyWorkerStats[index].restDayLeftNum])
            # 根据未安排天数降序排列
            workerIndexLeft = sorted(workerIndexLeft, key=lambda d: d[1], reverse=True)
            workerIndexLeft = list(map(lambda x: x[0], workerIndexLeft))

            for date in range(week.monday, week.sunday + 1):
                if len(restCalendar[date]) < self.dailyRestWorkerNum:

                    diffWorkerNum = self.dailyRestWorkerNum - len(restCalendar[date])
                    # 在周一到周日之间寻找可以替换的日期
                    for firstDate in range(week.monday, week.sunday + 1):
                        if firstDate == date:
                            continue
                        diffWorkerIndex = restCalendar[firstDate]
                        diffWorkerIndex = list(filter(lambda x: x not in restCalendar[date], diffWorkerIndex))
                        if len(diffWorkerIndex) < diffWorkerNum:
                            continue
                        diffWorkerIndex = list(filter(
                            lambda x: self.maxRestNumIfReplaced(x, firstDate, date, restCalendar) <= self.maxRestDay,
                            diffWorkerIndex))
                        if len(diffWorkerIndex) < diffWorkerNum:
                            continue

                        workerIndexSource = list(filter(lambda x: x not in restCalendar[firstDate], workerIndexLeft))
                        if len(workerIndexSource) < diffWorkerNum:
                            continue
                        workerIndexSource = list(filter(
                            lambda x: self.maxRestNumIfReplaced(x, -999, firstDate, restCalendar) <= self.maxRestDay,
                            workerIndexSource))
                        if len(workerIndexSource) < diffWorkerNum:
                            continue
                        break

                    assert len(diffWorkerIndex) >= diffWorkerNum
                    assert len(workerIndexSource) >= diffWorkerNum
                    workerIndexSource = workerIndexSource[0:diffWorkerNum]
                    diffWorkerIndex = diffWorkerIndex[0: diffWorkerNum]
                    print('date', date, 'firstDate', firstDate, 'diffWorkerIndex', diffWorkerIndex, 'workerIndexSource',
                          workerIndexSource)
                    restCalendar[firstDate] = list(
                        filter(lambda x: x not in diffWorkerIndex, restCalendar[firstDate]))
                    restCalendar[date] += diffWorkerIndex
                    restCalendar[firstDate] += workerIndexSource
                    workerIndexLeft = list(filter(lambda x: x not in workerIndexSource, workerIndexLeft))

        print(">>>>>>>>>>>>>>> final arrangement is: ")
        self.formatCalendar(restCalendar)

        # assert self.validateSchedule(restCalendar) == True
        # print(self.getMaxDelta(restCalendar, totalScheduleDays))
        return [restCalendar, overallWorkerStats]

    def isArrangable(self, workerIndex, date, calendar, workStats, dailyRestNum):
        # 1. id 不在当前天
        # 2. 当前天未排满
        # 3. 未达到最大连休天数（和之前休息不连续，或者连续但小于最大连休天数
        # if workerIndex not in calendar[date] \
        #         and len(calendar[date]) < dailyRestNum \
        #         and (workStats[workerIndex].previousRestEndDate != date + 1 or
        #                      workStats[workerIndex].accumulatedRestDayNum < self.maxRestDay):
        try:
            if workerIndex not in calendar[date]:
                if len(calendar[date]) < dailyRestNum:
                    if (workStats[workerIndex].previousRestEndDate != date + 1 or
                                 workStats[workerIndex].accumulatedRestDayNum < self.maxRestDay):
                        return True
        except:
            wx.MessageBox("exception: date" + str(date))

        return False

    def maxRestNumIfReplaced(self, workerIndex, sourceDate, destDate, calendar):
        length = 1
        previous = destDate - 1
        while previous % 7 != 0 and previous != sourceDate:
            if workerIndex in calendar.get(previous, list()):
                length += 1
            else:
                break
            previous -= 1
        next = destDate + 1
        while next % 7 != 1 and next != sourceDate:
            if workerIndex in calendar.get(next, list()):
                length += 1
            else:
                break
            next += 1
        return length

    def arrange(self, workerIndex, date, calendar, workStats):
        dataArrange = calendar.get(date, list())
        dataArrange.append(workerIndex)
        calendar[date] = dataArrange
        workStats[workerIndex].arrangedRestDay.append(date)
        workStats[workerIndex].restDayLeftNum = max(0, workStats[workerIndex].restDayLeftNum - 1)
        if Week.isWeekend(date):
            workStats[workerIndex].restWeekendLeftNum = max(0, workStats[workerIndex].restWeekendLeftNum - 1)
        if workStats[workerIndex].previousRestEndDate == date + 1:
            workStats[workerIndex].accumulatedRestDayNum += 1
        else:
            workStats[workerIndex].accumulatedRestDayNum = 1
        workStats[workerIndex].previousRestEndDate = date

        return True

    def formatCalendar(self, restCalendar):
        calendar = copy(restCalendar)
        calendar = sorted(calendar.items(), key=lambda d: d[0])
        for index in range(len(calendar)):
            print('date', str(calendar[index][0]), calendar[index][1])
            if index % 7 == 6:
                print('-------------------------')

    def validateSchedule(self, calendar):
        if calendar:
            totalWeekNum = math.ceil(len(calendar.values()) / 7)

            for weekNum in range(totalWeekNum):
                print(">>>>>>>>>>>> validating week No." + str(weekNum))

                week = Week(weekNum * 7 + 1)
                weeklyWorkStats = dict()
                for date in range(week.monday, week.sunday + 1):
                    workerIndexList = list(set(calendar[date]))
                    if len(workerIndexList) != self.dailyRestWorkerNum:
                        print('date', date, ' has duplicated workers')
                        return False

                    for workerIndex in workerIndexList:
                        stats = weeklyWorkStats.get(workerIndex, WorkerStats(workerIndex, 0, 0))

                        if date == (stats.previousRestEndDate + 1) or stats.previousRestEndDate == -1:
                            # 连续两天休息或第一天休息
                            stats.accumulatedRestDayNum += 1
                            if stats.accumulatedRestDayNum > self.maxRestDay:
                                print("date", date, "worker", workerIndex, "exceed max rest day", self.maxRestDay)
                                return False
                        else:
                            stats.accumulatedRestDayNum = 1

                        stats.previousRestEndDate = date

                        weeklyWorkStats[workerIndex] = stats
            return True
        else:
            # 排班为空
            print('empty calendar')
            return False

    def calculateWorkDayPerWorker(self, calendar):
        if calendar:
            workerDayPerWorker = dict()
            for (currentDate, workerIdList) in calendar.items():
                for workerId in workerIdList:
                    totalDay = workerDayPerWorker.get(workerId, 0)
                    totalDay += 1
                    workerDayPerWorker[workerId] = totalDay
            return workerDayPerWorker
        else:
            return dict()

    def getMaxDelta(self, calendar, totalScheduleDays):
        workerDayPerWorker = self.calculateWorkDayPerWorker(calendar)

        totalWeekNum = math.ceil(totalScheduleDays / 7)
        # 周期内每人总休假天数(休完为止）
        totalRestDayNum = math.ceil(
            float(totalWeekNum) * 7 * (self.totalWorkerNum - self.workerNumRequired) / self.totalWorkerNum)

        tempResult = list()
        for (key, value) in workerDayPerWorker.items():
            if abs(value - totalRestDayNum) > self.MAX_DELTA_DAY:
                tempResult.append((key, value))
        result = list(map(lambda x: (x[0], abs(x[1] - totalRestDayNum)), tempResult))
        print('delta', result)
        if len(result) == 0:
            # 已经达到要求
            return self.MAX_DELTA_DAY
        else:
            result = sorted(result, key=lambda x: x[1])
            return result[-1][1]

    def getWorkCalendar(self, calendar):
        restCalendar = dict()
        for (day, workIdList) in calendar.items():
            restCalendar[day] = list(range(self.totalWorkerNum))
            for workId in workIdList:
                if workId in restCalendar[day]:
                    restCalendar[day].remove(workId)
        return restCalendar


#
#
# def rebalance(self, targetCalendar, workStats):
#     workerDayPerWorker = self.calculateWorkDayPerWorker(targetCalendar)
#     targetDays = len(targetCalendar)
#     # 平均工时每人（天）,向上取整
#     targetTotalWorkDay = int(targetDays * self.workerNumRequired + self.totalWorkerNum - 1) / self.totalWorkerNum
#
#     newWorkerDayPerWorker = sorted(workerDayPerWorker.items(), key=lambda d: d[1])
#
#     size = len(workerDayPerWorker)
#     for index in range(0, size):
#         if newWorkerDayPerWorker[index][1] >= targetTotalWorkDay:
#             break
#         targetWorkerId = newWorkerDayPerWorker[index][0]
#         iterateOnlyArrangedWorkDay = workStats[targetWorkerId].arrangedWorkDay[:]
#         for arrangedWorkDay in iterateOnlyArrangedWorkDay:
#             startDate = arrangedWorkDay.startDate
#             endDate = arrangedWorkDay.endDate
#
#             if startDate != 1:
#                 # 不是第一天，在前一天寻找可以替换的
#                 for workerId in targetCalendar.get(startDate - 1, list()):
#                     if not self.isValidateToReplace(startDate, endDate, targetTotalWorkDay, workerId,
#                                                     targetWorkerId,
#                                                     targetCalendar, workerDayPerWorker, True):
#                         break
#
#                     # 搜索目标员工的起止休息日期
#                     for innerPair in workStats[workerId].arrangedWorkDay:
#                         if innerPair.endDate - innerPair.startDate < self.minRestDay:
#                             # 缩短后小于最小连续天数
#                             continue
#                         targetStartDate = startDate - 1
#                         newInnerPair = innerPair
#                         doReplace = False
#                         if workerId not in targetCalendar.get(startDate, list()) \
#                                 and targetStartDate == innerPair.endDate:
#                             # 结束日期为源员工的起始日期减1，即两者相邻
#                             newInnerPair.endDate -= 1
#                             doReplace = True
#                         elif workerId in targetCalendar.get(startDate - 1,
#                                                             list()) and workerId not in targetCalendar.get(
#                                     startDate - 2, list()) \
#                                 and targetStartDate == innerPair.startDate:
#                             newInnerPair.startDate += 1
#                             doReplace = True
#                         if doReplace:
#                             self.doReplace(targetCalendar, workerId, targetWorkerId, workerDayPerWorker, workStats,
#                                            innerPair, newInnerPair, startDate, endDate, targetStartDate, endDate,
#                                            True)
#                             startDate = targetStartDate
#                             break
#             if endDate != targetDays:
#                 # 不是最后一天，在后一天寻找可以替换的
#                 for workerId in targetCalendar.get(endDate + 1, list()):
#                     if not self.isValidateToReplace(startDate, endDate, targetTotalWorkDay, workerId,
#                                                     targetWorkerId,
#                                                     targetCalendar, workerDayPerWorker, False):
#                         break
#
#                     # 搜索目标员工的起止休息日期
#                     for innerPair in workStats[workerId].arrangedWorkDay:
#                         if innerPair.endDate - innerPair.startDate < self.minRestDay:
#                             continue
#                         targetEndDate = endDate + 1
#                         newInnerPair = innerPair
#                         doReplace = False
#
#                         if workerId not in targetCalendar.get(endDate, list()) \
#                                 and targetEndDate == innerPair.startDate:
#                             newInnerPair.startDate += 1
#                             doReplace = True
#                         elif workerId in targetCalendar.get(endDate + 1,
#                                                             list()) and workerId not in targetCalendar.get(
#                                     endDate + 2, list()) \
#                                 and targetEndDate == innerPair.endDate:
#                             newInnerPair.endDate -= 1
#                             doReplace = True
#
#                         if doReplace:
#                             self.doReplace(targetCalendar, workerId, targetWorkerId, workerDayPerWorker, workStats,
#                                            innerPair, newInnerPair, startDate, endDate, startDate, targetEndDate,
#                                            False)
#                             endDate = targetEndDate
#                             break
#
#     return targetCalendar
#
#
# def isValidateToReplace(self, startDate, endDate, targetTotalWorkDay, workerId, targetWorkerId, targetCalendar,
#                         workerDayPerWorker, replaceStart):
#     if endDate - startDate + 2 > self.maxRestDay:
#         # 不能增大，否则大于最大连续天数
#         return False
#     if replaceStart:
#         targetDate = startDate - 1
#         siblingTargetDate = startDate - 2
#     else:
#         targetDate = endDate + 1
#         siblingTargetDate = endDate + 2
#     if targetWorkerId in targetCalendar.get(targetDate, list()):
#         # 放止同一天出现同一个员工
#         return False
#     if targetWorkerId in targetCalendar.get(siblingTargetDate, list()):
#         # 不要把两个连续休息连接成一个（或者继续检查连成一个后是否超最大）
#         return False
#     if workerDayPerWorker[workerId] < targetTotalWorkDay:
#         # 要被减少天数的员工工时不高于平均工时
#         return False
#
#     return True
#
#
# def doReplace(self, targetCalendar, workerId, targetWorkerId, workerDayPerWorker, workStats, innerPair,
#               newInnerPair, startDate, endDate, newStartDate, newEndDate, replaceStart):
#     if replaceStart:
#         targetDate = newStartDate
#     else:
#         targetDate = newEndDate
#     targetCalendar[targetDate].remove(workerId)
#     targetCalendar[targetDate].append(targetWorkerId)
#     workerDayPerWorker[workerId] = workerDayPerWorker[workerId] - 1
#     workerDayPerWorker[targetWorkerId] = workerDayPerWorker[targetWorkerId] + 1
#     workStats[workerId].arrangedWorkDay.remove(innerPair)
#     workStats[workerId].arrangedWorkDay.append(newInnerPair)
#     for day in workStats[workerId].arrangedWorkDay:
#         if day.startDate == startDate and day.endDate == endDate:
#             workStats[workerId].arrangedWorkDay.remove(day)
#             break
#     workStats[targetWorkerId].arrangedWorkDay.append(
#         ArrangedWorkDay(newStartDate, newStartDate))


if __name__ == "__main__":
    workerNum = 14
    targetDays = 28

    # for x in range(10, 20):
    #     for i in range(math.ceil(float(x) / 3) + 1, x - 2):
    #         for j in range(3, 7):
    #             for h in [14, 21, 28, 35, 42, 49, 56, 63]:
    #                 print("#############", x, i, j, h)
    #                 s = Scheduler(list(range(x)), i, j)
    #                 s.doSchedule(h)

    for i in range(5, 6):
        for j in range(3, 4):
            print("#############", i, j)
            s = Scheduler(list(range(workerNum)), i, j)
            s.doSchedule(targetDays)

    print("finished!!!!!!!!!!!!")
