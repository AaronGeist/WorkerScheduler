# coding=utf-8
import random
from src.Data.WorkerStats import WorkerStats, ArrangedWorkDay

__author__ = 'yzhou7'


class Scheduler:
    NUM_OF_WORKLOAD = 3
    MIN_WORK_DAY = 3
    MAX_WORK_DAY = 6
    MAX_RETRY_TIME = 200

    def __init__(self, nameList, workload=NUM_OF_WORKLOAD, minWorkDay=MIN_WORK_DAY, maxWorkDay=MAX_WORK_DAY):
        self.workers = nameList
        self.workload = int(workload)
        self.minWorkDay = int(minWorkDay)
        self.maxWorkDay = int(maxWorkDay)
        pass

    def schedule(self, targetDays):

        emptyResult = dict()

        targetDays = int(targetDays)

        workerNum = len(self.workers)
        # 平均工时每人（天）
        targetTotalWorkDay = targetDays * workerNum / self.workload

        if self.minWorkDay > targetTotalWorkDay:
            print "最小连续工时大于平均工时，不能平均安排工时"
            return emptyResult

        firstTargetDate = 1

        # 当所有人的剩余工时为0时循环结束
        workDayLeft = [targetTotalWorkDay] * workerNum

        # 字典格式为key=日期，value=list of worker
        targetCalendar = dict()

        # 结构为key=员工号，value=[剩余工作天数，[之前工作天数起始值]]
        workerStats = dict()
        for worker in self.workers:
            workerStats[worker] = WorkerStats(targetTotalWorkDay)

        previousWorkerDay = [0] * workerNum

        while True:
            # 遍历每个worker，安排工作日期
            for index in range(0, workerNum):
                # 如果已经安排完所有工时，则跳过
                if workerStats[self.workers[index]].workDayLeft == 0:
                    continue

                # 在最大连续和最小连续之间随机选数
                randomWorkDay = random.randint(self.minWorkDay, self.maxWorkDay)

                print "current worker", index, "current day", firstTargetDate, 'workday length', randomWorkDay

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
                    print "Cannot find empty day for worker", self.workers[index]
                    self.printSchedule(targetCalendar)
                    return emptyResult

                # 开始日期已经找到，安排工作
                for i in range(0, randomWorkDay):
                    workerList = targetCalendar.get(firstTargetDate + i, list())
                    workerList.append(self.workers[index])
                    targetCalendar[firstTargetDate + i] = workerList

                stats = workerStats.get(self.workers[index])
                stats.workDayLeft -= randomWorkDay
                # TODO should use this data
                stats.arrangedWorkDay.append(ArrangedWorkDay(firstTargetDate, firstTargetDate + randomWorkDay))

            # 如果所有人的剩余工作天数都为0，则结束
            if sum(map(lambda x: x.workDayLeft, workerStats.values())) == 0:
                break

        self.printSchedule(targetCalendar)
        return targetCalendar

    def printSchedule(self, targetCalendar):
        for (day, idList) in targetCalendar.items():
            print str(day) + ": " + ", ".join(map(str, idList))

    def validateSchedule(self, targetCalendar):
        if targetCalendar:
            workerStats =


if __name__ == "__main__":
    nameList = range(1, 6)
    count = 0
    s = Scheduler(nameList)

    data = s.schedule(20)
    # if s.validateSchedule(data):
    # s.printSchedule(data)

    # break
