"""Useful utilities to get info on or modify nodes listed on the database."""
#Standard
import datetime

#Hydra
from Constants import TIMEDICT, TIMEDICT_REV
from hydra.logging_setup import logger
import hydra.hydra_sql as sql

def simplify_schedule_data(qtDataList):
    """Take data from the QTableWidget, simplifty it for storage in the DB"""
    if not qtDataList:
        return None
    simpleDataList = []
    firstAction = None
    for eventItem in qtDataList:
        eventList = eventItem.split(":")
        #Conver the schedule table UI index to a real time
        time = TIMEDICT[int(eventList[1])]
        simpleDataList.append("{0}-{1}-{2}".format(eventList[0], time, eventList[2]))
        if not firstAction:
            firstAction = eventList[2]
        lastAction = eventList[2]

    if firstAction == lastAction:
        simpleDataList.pop(0)

    return simpleDataList

def expand_schedule_data(dbData):
    """Take schedule data from the database and encode it for application to
    the QTableWidget schedule UI"""
    if not dbData:
        return None
    expandedDataList = []
    dbData = dbData.split(",")
    if len(dbData) < 2:
        return None
    for eventItem in dbData:
        eventList = eventItem.split("-")
        #Convert the time to a schdule table UI index
        time = TIMEDICT_REV[eventList[1]]
        expandedDataList.append("{0}:{1}:{2}".format(eventList[0], time, eventList[2]))

    #If the schdule doesn't have data for the start of the week (Midnight Sunday
    #   Morning) make up a schedule item continuing the action from the last
    #   schdule item of the week.
    if int(expandedDataList[0].split(":")[0]) != 0 and int(expandedDataList[1].split(":")[0]) != 0:
        expandedDataList = [("0:0:{0}".format(int(expandedDataList[-1].split(":")[2])))] + expandedDataList

    return expandedDataList

def find_schedule(dayOfWeek, dataDict):
    """Take and ISOWeekday and a dictionary from within find_next_event and finds
    the next event during the given ISOWeekday and in the dataDict."""
    schedule = None
    i = 0
    while not schedule and i < 9:
        #Check if day of week is the the dataDict
        if dayOfWeek in dataDict.keys():
            schedule = dataDict[dayOfWeek]
        #If not add one to dayOfWeek unless day of week is 6 (Saturday),
        #   then reset to 0 (Sunday)
        else:
            if dayOfWeek < 6:
                dayOfWeek += 1
            else:
                dayOfWeek = 0
        #Finally, increase counter
        i += 1

    if i > 8:
        logger.error("Can't find next event!")

    return schedule, dayOfWeek

def find_next_event(now, dbData):
    """Take the current datetime and the decoded schedule data from the DB and
    find the next scheduling event"""
    nowDayOfWeek = now.isoweekday()
    nowTime = now.time()

    dataList = dbData.split(",")
    if len(dataList) < 2:
        return None

    dataDict = {}
    for actionItem in dataList:
        actionItemList = actionItem.split("-")
        dayOfWeek = int(actionItemList[0])
        action = int(actionItemList[2])
        timeList = [int(t) for t in actionItemList[1].split(":")]
        timeObject = datetime.time(timeList[0], timeList[1])
        try:
            dataDict[dayOfWeek] += [[timeObject, action]]
        except KeyError:
            dataDict[dayOfWeek] = [[timeObject, action]]

    #scheule is a nested list like [[time, action], [time,action]]
    todaySchedule, newDayOfWeek = find_schedule(nowDayOfWeek, dataDict)
    if not todaySchedule:
        return None

    sched = None
    #Check each schedule item's activation time, if one of them is after now
    #   then this schedule will work for today
    for schedItem in todaySchedule:
        if schedItem[0] > nowTime:
            logger.debug("Schedule Found: %s", sched)
            sched = schedItem

    #If not then the next schdule item is probably on a date later in the week.
    #Iterate the day of week and look again.
    if not sched:
        newDayOfWeek += 1
        todaySchedule, newDayOfWeek = find_schedule(newDayOfWeek, dataDict)
        sched = todaySchedule[0]

    if not sched:
        logger.error("Could not find schedule")
        return None

    return [newDayOfWeek] + sched

def calcuate_sleep_time(now, dbData):
    """Takes the current datetime and the decoded schedule data from the DB
    and finds the time to sleep until the next event"""
    nextEvent = find_next_event(now, dbData)

    if not nextEvent or nextEvent[-1] is None:
        return None, None

    nowDate = now.date()
    nowDayOfWeek = now.isoweekday()

    if nowDayOfWeek <= nextEvent[0]:
        #Next event is in this week
        nextTime = datetime.datetime.combine(nowDate, nextEvent[1])
        sleepyTime = (nextTime - now).total_seconds()
        sleepyTime += 86400 * (nextEvent[0] - nowDayOfWeek)
    else:
        #Next event is next week
        nextTime = datetime.datetime.combine(nowDate, nextEvent[1])
        sleepyTime = (nextTime - now).total_seconds()
        sleepyTime += (86400 * (7 - nowDayOfWeek))
        sleepyTime += (86400 * nextEvent[0])

    #These are reversed as they're going to be the oposite of the status after the event
    if nextEvent[2] == 1:
        status = sql.OFFLINE
    else:
        status = sql.READY

    return sleepyTime, status

def calcuate_sleep_time_from_node(nodeID):
    """A convience function that does calcuate_sleep_time given a host name"""
    thisNode = sql.hydra_rendernode.fetch("WHERE id = %s", (nodeID,),
                                        cols=["week_schedule"])
    nowDateTime = datetime.datetime.now().replace(microsecond=0)
    return calcuate_sleep_time(nowDateTime, thisNode.week_schedule)
