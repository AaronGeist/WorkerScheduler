# coding=utf-8
import logging
import random
import math
import sys

from src.Data.WorkerStats import WorkerStats
from src.Data.ScheduleResult import ScheduleResult

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKLOAD = 3
    MAX_WORK_DAY = 3
    MAX_REST_DAY = 4
    # 最小天数是内部固定值，用来保证“连续工作连续休息”
    MIN_WORK_DAY = 2

    MIN_REST_DAY = 3
    MAX_RETRY_TIME = 1000

    # 保证基本公平，最多差值为delta*2
    # TODO 根据周期长度调整
    MAX_DELTA_DAY = 1

    def __init__(self, workers, dailyRequiredWorkerNum=NUM_OF_WORKLOAD, maxRestDay=MAX_REST_DAY,
                 maxWorkDay=MAX_WORK_DAY, isShuffle=False, logLevel=logging.WARNING):
        self.workers = workers[:]
        self.workerNum = len(self.workers)
        if isShuffle:
            random.shuffle(self.workers)
        self.dailyRequiredWorkerNum = int(dailyRequiredWorkerNum)
        self.maxRestDay = int(maxRestDay)
        self.maxWorkDay = int(maxWorkDay)
        logging.basicConfig(stream=sys.stderr, level=logLevel)

    def schedule(self, totalDayNum):
        scheduleResult = ScheduleResult()
        totalDayNum = int(totalDayNum)
        if self.workerNum < self.dailyRequiredWorkerNum:
            print('worker number less than workload, cannot schedule')
            scheduleResult.message = u'总员工人数小于每天出勤人数，无法排班'
            return scheduleResult
        if self.workerNum == self.dailyRequiredWorkerNum:
            print('worker number equals to workload, don\'t need to schedule at all')
            scheduleResult.message = u'总员工人数等于每天出勤人数，无需排班'
            return scheduleResult
        if self.MIN_WORK_DAY > self.maxWorkDay:
            print('min day > max day')
            scheduleResult.message = u'最大连续出勤天数设置无法保证连续出勤'
            return scheduleResult
        if self.MIN_WORK_DAY == self.maxWorkDay:
            if self.workerNum < self.dailyRequiredWorkerNum * 2:
                print('min=max but workers < workload * 2, not enough worker to handle the workload')
                scheduleResult.message = u'最大最小连续出勤数相等且总员工数小于每天出勤人数的两倍，人手不足'
                return scheduleResult
            else:
                # 固定班次的话，则误差可能为固定连续出勤数
                self.MAX_DELTA_DAY = self.MIN_WORK_DAY
        # 这种情况包含了上一种情况
        if self.workerNum < self.dailyRequiredWorkerNum * 2:
            if self.maxWorkDay < self.MIN_WORK_DAY * 2:
                print('min * 2 > max while workers < workload * 2, not enough worker to handle the workload')
                scheduleResult.message = u'总员工数小于每天出勤人数的两倍，且最大连续出勤天数小于最小连续出勤天数的两倍，人手不足'
                return scheduleResult
        workerNum = self.workerNum
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = int(totalDayNum * self.dailyRequiredWorkerNum + workerNum - 1) / workerNum

        if self.MIN_WORK_DAY > targetTotalWorkDay:
            scheduleResult.message = u'最小连续工时大于平均工时，不能平均安排工时'
            return scheduleResult

        retryCnt = 0
        minDelta = 99999
        unBalancedResult = dict()
        while retryCnt < self.MAX_RETRY_TIME:
            retryCnt += 1
            [resultCalendar, workStats] = self.doSchedule(totalDayNum)
            if self.validateSchedule(resultCalendar):
                currentDelta = self.getMaxDelta(resultCalendar, totalDayNum)
                if currentDelta <= self.MAX_DELTA_DAY:
                    logging.debug('after %d time\'s retry', retryCnt)
                    scheduleResult.message = u'排班成功且工时较为平均'
                    scheduleResult.workCalendar = resultCalendar
                    scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(resultCalendar)
                    scheduleResult.restCalendar = self.getRestCalendar(resultCalendar)
                    return scheduleResult
                else:
                    # 如果不够平均，则取目前最平均的排班返回
                    logging.debug('minDelta %d current %d', minDelta, currentDelta)
                    if minDelta > currentDelta:
                        unBalancedResult = resultCalendar
                        minDelta = currentDelta

        logging.debug('Cannot meet min delta requirement after %d retries', self.MAX_RETRY_TIME)

        if unBalancedResult:
            scheduleResult.message = u'排班成功但没有找到工时最平均方案'
            scheduleResult.workCalendar = unBalancedResult
            scheduleResult.personalTotalWorkDay = self.calculateWorkDayPerWorker(unBalancedResult)
            scheduleResult.restCalendar = self.getRestCalendar(unBalancedResult)
            self.printFormatedCalendar(unBalancedResult)
            logging.debug(self.getMaxDelta(unBalancedResult, totalDayNum))
        else:
            logging.debug('empty unbalanceResult')
            scheduleResult.message = u'没有找到符合条件的排班方案，建议调整参数'

        return scheduleResult

    def doSchedule(self, totalDayNum):

        totalDayNum = int(totalDayNum)

        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = math.ceil(float(totalDayNum) * self.dailyRequiredWorkerNum / self.workerNum)
        logging.debug('targetTotalWorkDay %d', targetTotalWorkDay)

        # 字典格式为key=日期，value=list of worker
        targetCalendar = dict()
        for i in range(1, totalDayNum + 1):
            targetCalendar[i] = list()

        # 结构为key=员工号，value=剩余工作天数，[之前工作天数起始值]
        workerStats = dict()
        for i in range(0, self.workerNum):
            workerStats[i] = WorkerStats(targetTotalWorkDay)

        # 分析哪些员工平均情况下不能轮到最后一轮
        estimatedWorkDayEachPersonPerDay = float(self.maxWorkDay + self.MIN_WORK_DAY) / 2
        estimatedRound = float(self.dailyRequiredWorkerNum * totalDayNum) / (
            estimatedWorkDayEachPersonPerDay * self.workerNum)
        # 这个id之后的员工可能不能轮到最后一轮分配
        maxWorkerIdCoverAllRound = int(math.floor(self.workerNum * (estimatedRound - math.floor(estimatedRound))))

        while True:
            # 上一轮的平均剩余工时
            workDayLeftList = list(map(lambda stats: stats.workDayLeft, workerStats.values()))
            avgWorkDayLeft = float(sum(workDayLeftList)) / len(workDayLeftList)
            # 遍历每个worker，安排工作日期
            for index in range(0, self.workerNum):
                if workerStats[index].workDayLeft <= 0:
                    # 如果已经安排完所有工时或已经安排到最后一天，则跳过
                    continue

                targetDate = self.findTargetDate(totalDayNum, targetCalendar, index, workerStats.get(index))

                # 如果while循环到了末尾没成功,则退出（可能是因为不需要再安排了？）
                if targetDate > totalDayNum:
                    logging.debug('worker %d quit', index)
                    workerStats[index].workDayLeft = 0
                    break

                randomWorkDay = self.generateRandomWorkDayLength(index, maxWorkerIdCoverAllRound, workerStats,
                                                                 avgWorkDayLeft, totalDayNum, targetDate,
                                                                 targetCalendar)

                logging.debug('worker %d targetDate %d length %d, previousDate %d accumulateDay %d leftday %d', index,
                              targetDate, randomWorkDay, workerStats[index].previousWorkDate,
                              workerStats[index].accumulatedWorkDay, workerStats[index].workDayLeft)
                # 开始日期已经找到，安排工作
                for i in range(0, randomWorkDay):
                    workerList = targetCalendar.get(targetDate + i, list())
                    workerList.append(index)
                    targetCalendar[targetDate + i] = workerList

                stats = workerStats.get(index)
                stats.workDayLeft = max(0, stats.workDayLeft - randomWorkDay)
                # stats.arrangedWorkDay.append(
                #     ArrangedWorkDay(targetDate, min(targetDate + randomWorkDay - 1, totalDayNum)))

                newEndDate = min(targetDate + randomWorkDay - 1, totalDayNum)
                if targetDate == stats.previousWorkDate + 1:
                    stats.accumulatedWorkDay += randomWorkDay
                    previousStartDate = stats.endDateMap[stats.previousWorkDate]
                    stats.startDateMap[previousStartDate] = newEndDate
                    del stats.endDateMap[stats.previousWorkDate]
                    stats.endDateMap[newEndDate] = previousStartDate
                else:
                    stats.accumulatedWorkDay = randomWorkDay
                    stats.startDateMap[targetDate] = newEndDate
                    stats.endDateMap[newEndDate] = targetDate
                stats.previousWorkDate = newEndDate

                # 提前安排好最后一天+最大连休天数后的那一天，保证最大连休天数被满足
                preArrangeWorkDate = stats.previousWorkDate + self.maxRestDay + 1
                if preArrangeWorkDate <= totalDayNum and stats.workDayLeft > 0:
                    targetCalendar[preArrangeWorkDate].append(index)
                    stats.preArrangedWorkDate = preArrangeWorkDate
                else:
                    stats.preArrangedWorkDate = totalDayNum + 1

            # 如果所有人的剩余工作天数都为0，则结束
            if sum(list(map(lambda x: x.workDayLeft, workerStats.values()))) == 0:
                break

        self.fillEmptyDate(targetCalendar, workerStats)

        return [targetCalendar, workerStats]

    def findTargetDate(self, totalDayNum, targetCalendar, index, stats):

        # 如果之前已经占位，则先移除
        if stats.preArrangedWorkDate <= totalDayNum and index in targetCalendar[stats.preArrangedWorkDate]:
            targetCalendar[stats.preArrangedWorkDate].remove(index)

        # 优先安排连续工作
        if stats.previousWorkDate != -1 \
                and len(targetCalendar[min(stats.previousWorkDate + 1, totalDayNum)]) < self.dailyRequiredWorkerNum \
                and stats.accumulatedWorkDay < self.maxWorkDay:
            return stats.previousWorkDate + 1

        targetDate = 1 if stats.previousWorkDate == -1 else stats.previousWorkDate + self.MIN_REST_DAY + 1
        # 已经安排到末尾了，安排剩余天数
        if targetDate >= totalDayNum and stats.accumulatedWorkDay < self.maxWorkDay:
            targetDate = stats.previousWorkDate
        # 找到最早的没有安排该员工工作，且没有满员的日期
        while targetDate <= min(stats.preArrangedWorkDate, totalDayNum):
            # 找到没有满员的日期
            workerList = targetCalendar.get(targetDate, list())
            if len(workerList) == self.dailyRequiredWorkerNum or index in targetCalendar[targetDate]:
                # 当前天已经满了，加1
                targetDate += 1
                logging.debug(str(targetCalendar[targetDate - 1]))
                continue

            # 验证安排这一天不会导致超过最大连休天数
            if stats.previousWorkDate != -1 and targetDate - stats.previousWorkDate - 1 > self.maxRestDay:
                logging.error("findTargetDate(): worker %d date %d exceed max rest day %d", index, targetDate, self.maxRestDay)
                return totalDayNum + 1

            break

        # FIXME 有了这个随机数，会导致中间空缺
        # 加入随机元素，在最早可以安排的日期和最晚可以安排的日期之间取随机数
        # if targetDate < min(stats.preArrangedWorkDate, totalDayNum) and stats.previousWorkDate != -1:
        #     targetDate = random.randint(targetDate, min(stats.preArrangedWorkDate, totalDayNum))

        return targetDate

    def generateRandomWorkDayLength(self, targetWorkerIndex, maxWorkerIdCoverAllRound, workerStats, avgWorkDayLeft,
                                    totalDayNum, targetDate, calendar):

        if targetDate == workerStats[targetWorkerIndex].previousWorkDate + 1:
            # 如果是直接接着之前工作日继续工作
            maxWorkDayLength = self.maxWorkDay - workerStats[targetWorkerIndex].accumulatedWorkDay
            minWorkDayLength = 1
        else:
            maxWorkDayLength = self.maxWorkDay
            minWorkDayLength = self.MIN_WORK_DAY

        # 寻找能够安排的最晚日期
        date = targetDate
        # 时间范围只有targetDate这一天了
        logging.debug(calendar[targetDate])
        if targetDate == min(targetDate + self.maxWorkDay + 1, totalDayNum + 1) - 1 \
                and len(calendar[targetDate]) < self.dailyRequiredWorkerNum:
            maxWorkDayLength = 1
        else:
            for date in range(targetDate, min(targetDate + self.maxWorkDay + 1, totalDayNum + 1)):
                if len(calendar[date]) >= self.dailyRequiredWorkerNum:
                    break
            maxWorkDayLength = min(maxWorkDayLength, (date - 1) - targetDate + 1)

        # 在最大连续和最小连续之间随机选数
        if maxWorkDayLength > minWorkDayLength:
            randomWorkDay = random.randint(minWorkDayLength, maxWorkDayLength)
        else:
            randomWorkDay = maxWorkDayLength

        # 优化随机数，如果预测到该员工不能轮到最后一轮，则适当增加
        if targetWorkerIndex > maxWorkerIdCoverAllRound and int(
                        (minWorkDayLength + maxWorkDayLength) / 2) < maxWorkDayLength:
            randomWorkDay = random.randint(int((minWorkDayLength + maxWorkDayLength) / 2), maxWorkDayLength)

        # 优化随机数，如果当前员工剩余天数与上一轮结束后的剩余天数平均值有偏差，则适当修正
        workDayLeft = workerStats[targetWorkerIndex].workDayLeft
        delta = int(avgWorkDayLeft - workDayLeft)
        if abs(delta) >= 2:
            # 差值大于2时才修正
            randomWorkDay -= delta
            if randomWorkDay > maxWorkDayLength:
                randomWorkDay = maxWorkDayLength
            elif randomWorkDay < minWorkDayLength:
                randomWorkDay = minWorkDayLength

        # 如果到末尾了，且连续天数小于最大连续天数，则一起安排了
        if totalDayNum - targetDate + 1 <= randomWorkDay:
            randomWorkDay = totalDayNum - targetDate + 1

        # 保证不会超出剩余工作天数太多
        randomWorkDay = min(randomWorkDay, workerStats[targetWorkerIndex].workDayLeft)
        return randomWorkDay

    def fillEmptyDate(self, targetCalendar, workerStats):
        totalDayNum = len(targetCalendar.keys())

        for date in range(1, totalDayNum + 1):
            if len(targetCalendar[date]) < self.dailyRequiredWorkerNum:
                for workerIndex in targetCalendar.get(date - 1, list()):
                    if workerIndex not in targetCalendar[date] \
                            and workerIndex not in targetCalendar.get(date + 1, list()) \
                            and date - 1 - workerStats[workerIndex].endDateMap[date - 1] + 1 < self.maxWorkDay:
                        # logging.debug("after date %d could arrange worker %d arranged %d", date, workerIndex,
                        #               date - 1 - workerStats[workerIndex].endDateMap[date - 1] + 1)
                        targetCalendar[date].append(workerIndex)
                        newStartDate = workerStats[workerIndex].endDateMap[date - 1]
                        del workerStats[workerIndex].endDateMap[date - 1]
                        newEndDate = date
                        workerStats[workerIndex].endDateMap[newEndDate] = newStartDate
                        workerStats[workerIndex].startDateMap[newEndDate] = newEndDate
                        if len(targetCalendar[date]) == self.dailyRequiredWorkerNum:
                            break

            if len(targetCalendar[date]) < self.dailyRequiredWorkerNum:
                for workerIndex in targetCalendar.get(date + 1, list()):
                    if workerIndex not in targetCalendar[date] \
                            and workerIndex not in targetCalendar.get(date - 1, list()) \
                            and workerStats[workerIndex].startDateMap[date + 1] - (date + 1) + 1 < self.maxWorkDay:
                        # logging.debug("before date %d could arrange worker %d arranged %d", date, workerIndex,
                        #               workerStats[workerIndex].startDateMap[date + 1] - (date + 1) + 1)
                        targetCalendar[date].append(workerIndex)
                        newEndDate = workerStats[workerIndex].startDateMap[date + 1]
                        del workerStats[workerIndex].startDateMap[date + 1]
                        newStartDate = date
                        workerStats[workerIndex].startDateMap[newEndDate] = newStartDate
                        workerStats[workerIndex].endDateMap[newEndDate] = newEndDate
                        if len(targetCalendar[date]) == self.dailyRequiredWorkerNum:
                            break
            if len(targetCalendar[date]) < self.dailyRequiredWorkerNum:
                for workerIndex in range(0, self.workerNum):
                    if workerIndex not in targetCalendar.get(date + 1, list()) \
                            and workerIndex not in targetCalendar.get(date - 1, list()) \
                            and workerIndex not in targetCalendar.get(date, list()):
                        # logging.debug("insert date %d worker %d", date, workerIndex)
                        targetCalendar[date].append(workerIndex)
                        workerStats[workerIndex].startDateMap[date] = date
                        workerStats[workerIndex].endDateMap[date] = date
                    if len(targetCalendar[date]) == self.dailyRequiredWorkerNum:
                        break

    def printFormatedCalendar(self, calendar):
        for (date, workerIdList) in calendar.items():
            logging.debug('DAY ' + (str(date) if date >= 10 else '0' + str(date)) + " : " + ", ".join(list(list(
                map(lambda id: str(self.workers[id]) if self.workers[id] >= 10 else '0' + str(self.workers[id]),
                    workerIdList)))))

    def validateSchedule(self, targetCalendar):
        if targetCalendar:
            workerStats = dict()
            for (currentDate, workerList) in targetCalendar.items():
                workerList = list(set(workerList))
                if len(workerList) != self.dailyRequiredWorkerNum:
                    logging.info('date %d has duplicated worker', currentDate)
                    return False

                for worker in workerList:
                    stats = workerStats.get(worker, WorkerStats(0))

                    if currentDate == (stats.previousWorkDate + 1) or stats.previousWorkDate == -1:
                        # 连续两天上班或第一天上班
                        stats.accumulatedWorkDay += 1
                        if stats.accumulatedWorkDay > self.maxWorkDay:
                            logging.info("date %d worker %d exceed max work day %d", currentDate, worker,
                                            self.maxWorkDay)
                            return False
                    else:
                        # 中间有休息
                        # if stats.accumulatedWorkDay < self.MIN_WORK_DAY and currentDate != 1:
                        #     logging.warning('date %d worker %d doesn\'t meet minWorkDay %d', stats.previousWorkDate,
                        #                     worker,
                        #                     self.MIN_WORK_DAY)
                        #     return False
                        restLength = currentDate - stats.previousWorkDate - 1
                        if restLength > self.maxRestDay:
                            logging.info('date %d worker %d exceed maxRestDay %d', currentDate, worker,
                                            self.maxRestDay)
                            return False
                        # elif restLength < self.MIN_REST_DAY:
                        #     logging.warning('date %d worker %d not meet minRestDay %d', currentDate, worker,
                        #                     self.MIN_REST_DAY)
                        #     return False
                        # 重置为1
                        stats.accumulatedWorkDay = 1

                    stats.previousWorkDate = currentDate

                    workerStats[worker] = stats
            return True
        else:
            # 排班为空
            logging.info('empty calendar')
            return False

    @staticmethod
    def calculateWorkDayPerWorker(targetCalendar):
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
        logging.debug(workerDayPerWorker)
        # 平均工时每人（天）,向上取整
        targetTotalWorkDay = math.ceil(float(targetDays) * self.dailyRequiredWorkerNum / self.workerNum)
        # result = list(filter(lambda x, y: abs(y - targetTotalWorkDay) > self.MAX_DELTA_DAY, workerDayPerWorker.items()))
        tempResult = list()
        for (key, value) in workerDayPerWorker.items():
            if abs(value - targetTotalWorkDay) > self.MAX_DELTA_DAY:
                tempResult.append((key, value))
        result = list(map(lambda x: (x[0], abs(x[1] - targetTotalWorkDay)), tempResult))
        if len(result) == 0:
            # 已经达到要求
            return self.MAX_DELTA_DAY
        else:
            result = sorted(result, key=lambda x: x[1])
            logging.debug(str(result))
            return result[-1][1]

    def getRestCalendar(self, targetCalendar):
        restCalendar = dict()
        for (day, workIdList) in targetCalendar.items():
            restCalendar[day] = list(range(self.workerNum))
            for workId in workIdList:
                if workId in restCalendar[day]:
                    restCalendar[day].remove(workId)
        return restCalendar

    @staticmethod
    def getWorkDayForEachWorker(targetCalendar, workers):
        workdayDict = dict()
        for index in list(range(len(workers))):
            workdayDict[index] = list()
        for (day, workIdList) in targetCalendar.items():
            for workId in workIdList:
                workdayDict[workId].append(day)

        return workdayDict

if __name__ == "__main__":
    # workerNum = 5
    # s = Scheduler(range(1, workerNum + 1))
    #
    # targetDays = 20
    # s.schedule(targetDays)

    workerNum = 20
    s = Scheduler(list(range(workerNum)), dailyRequiredWorkerNum=6, maxRestDay=6, maxWorkDay=3, isShuffle=True, logLevel=logging.DEBUG)

    targetDays = 63
    result = s.schedule(targetDays)

    workdayDict = Scheduler.getWorkDayForEachWorker(result.workCalendar, list(range(workerNum)))
    result1 = dict()
    for (workIndex, workDayList) in workdayDict.items():
        weeklyWorkDayList = list()
        week = 1
        startIndex = 0
        for dateIndex in range(len(workDayList)):
            if workDayList[dateIndex] > week * 7:
                weeklyWorkDayList.append(
                    list(map(lambda date: date % 7 if date % 7 != 0 else 7, workDayList[startIndex: dateIndex])))
                startIndex = dateIndex
                week += 1
        if startIndex < len(workDayList):
            weeklyWorkDayList.append(
                list(map(lambda date: date % 7 if date % 7 != 0 else 7, workDayList[startIndex: len(workDayList)])))
        result1[workIndex] = weeklyWorkDayList
    print(result1)

    # maxRestDay = 3
    # maxWorkDay = 6
    # for wNum in range(10, 20):
    #     for req in range(int(wNum / 3) + 1, wNum - 1):
    #         for dayLength in [28, 56, 84, 112]:
    #             s = Scheduler(list(range(wNum)), dailyRequiredWorkerNum=req, maxRestDay=maxRestDay,
    #                           maxWorkDay=maxWorkDay, logLevel=logging.ERROR)
    #             result = s.schedule(dayLength)
    #             if not s.validateSchedule(result.workCalendar):
    #                 print(">>>>> Failed totalDay %d workerNum %d required %d, maxRest %d maxWork %d", dayLength, wNum,
    #                       req, maxRestDay, maxWorkDay)
    #             else:
    #                 print("##### pass totalDay %d workerNum %d required %d, maxRest %d maxWork %d maxdelta %d",
    #                       dayLength, wNum, req, maxRestDay, maxWorkDay, s.getMaxDelta(result.workCalendar, dayLength))
