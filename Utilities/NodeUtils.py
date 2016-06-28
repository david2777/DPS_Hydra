"""Useful utilities to get info on or modify nodes listed on the database."""
#Standard
import datetime

#Third Party
from MySQLdb import Error as sqlerror

#Hydra
from Constants import TIMEDICT, TIMEDICT_REV, DAYDICT, EVENTDICT
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *

def simplifyScheduleData(qtDataList):
    """Take data from the QTableWidget, simplifty it for storage in the DB"""
    if not qtDataList:
        return None
    simpleDataList = []
    firstAction = None
    for eventItem in qtDataList:
        eventList = eventItem.split(":")
        time = TIMEDICT[int(eventList[1])]
        simpleDataList.append("{0}-{1}-{2}".format(eventList[0], time, eventList[2]))
        if not firstAction:
            firstAction = eventList[2]
        lastAction = eventList[2]

    if firstAction == lastAction:
        simpleDataList.pop(0)

    return simpleDataList

def makeScheduleReadable(simpleDataList):
    """Returns a more human readable list of schedule actions given an decoded
    schedule data list"""
    if not simpleDataList:
        return []
    readableDataList = []
    for eventItem in simpleDataList:
        eventList = eventItem.split("-")
        day = DAYDICT[int(eventList[0])]
        action = EVENTDICT[int(eventList[2])]
        readableDataList.append("{0} @ {1} do {2}".format(day, eventList[1], action))

    return readableDataList

def expandScheduleData(dbData):
    """Take schedule dbData from the dbDatabase and encode it for application to
    the QTableWidget on load"""
    if not dbData:
        return None
    expandedDataList = []
    dbData = dbData.split(",")
    if len(dbData) < 2:
        return None
    for eventItem in dbData:
        eventList = eventItem.split("-")
        time = TIMEDICT_REV[eventList[1]]
        expandedDataList.append("{0}:{1}:{2}".format(eventList[0], time, eventList[2]))

    if int(expandedDataList[0].split(":")[0]) != 0 and int(expandedDataList[1].split(":")[0]) != 0:
        expandedDataList = [("0:0:{0}".format(int(expandedDataList[-1].split(":")[2])))] + expandedDataList

    return expandedDataList

def findNextEvent(now, dbData):
    """Take the current datetime and the decoded schedule data from the DB and
    find the next scheduling event"""
    nowDate = now.date()
    nowDayOfWeek = now.isoweekday()
    nowTime = now.time()

    dataList = dbData.split(",")
    if len(dataList) < 2:
        return None

    dataDict = {}
    for actionItem in dataList:
        actionItemList = actionItem.split("-")
        timeList = actionItemList[1].split(":")
        myTime = datetime.time(int(timeList[0]), int(timeList[1]))
        try:
            dataDict[int(actionItemList[0])] += [[myTime, int(actionItemList[2])]]
        except KeyError:
            dataDict[int(actionItemList[0])] =[[myTime, int(actionItemList[2])]]

    todaySchedule, newDayOfWeek = findSchedule(nowDayOfWeek, dataDict)
    if not todaySchedule:
        return None

    sched = None
    logger.info(todaySchedule)
    for todayTime in todaySchedule:
        if todayTime[0] > nowTime:
            sched = todayTime

    if not sched:
        newDayOfWeek += 1
        todaySchedule, newDayOfWeek = findSchedule(newDayOfWeek, dataDict)
        #logger.info(newDayOfWeek)
        #logger.info(todaySchedule)
        sched = todaySchedule[0]

    if not sched:
        logger.error("Could not find schedule")

    logger.info([newDayOfWeek] + sched)

    return [newDayOfWeek] + sched

def findSchedule(tempDayOfWeek, dataDict):
    """Take and ISOWeekday and a dictionary from within findNextEvent and finds
    the next event durring the given ISOWeekday and in the dataDict"""
    todaySchedule = None
    loopCount = 0
    while not todaySchedule and loopCount < 9:
        if tempDayOfWeek in dataDict.keys():
            todaySchedule = dataDict[tempDayOfWeek]
        else:
            tempDayOfWeek += 1 if tempDayOfWeek < 6 else -6
        loopCount += 1

    if loopCount > 8:
        logger.error("Can't find next event!")

    return todaySchedule, tempDayOfWeek

def calcuateSleepTime(now, dbData):
    """Takes the current datetime and the decoded schedule data from the DB
    and finds the time to sleep until the next event"""
    nowDate = now.date()
    nowDayOfWeek = now.isoweekday()
    nowTime = now.time()

    nextEvent = findNextEvent(now, dbData)

    if nowDayOfWeek <= nextEvent[0]:
        nextTime = datetime.datetime.combine(nowDate, nextEvent[1])
        sleepyTime = (nextTime - now).total_seconds()
        sleepyTime += 86400 * (nextEvent[0] - nowDayOfWeek)
    else:
        #next week
        nextTime = datetime.datetime.combine(nowDate, nextEvent[1])
        sleepyTime = (nextTime - now).total_seconds()
        sleepyTime += (86400 * (7 - nowDayOfWeek))
        sleepyTime += (86400 * nextEvent[0])

    #These are reversed as they're going to be the oposite of the status after the event
    if nextEvent[2] == 1:
        status = OFFLINE
    else:
        status = READY

    return sleepyTime, status

def calcuateSleepTimeFromNode(nodeName):
    """A convience function that does calcuateSleepTime given a host name"""
    [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (nodeName,))
    return calcuateSleepTime(datetime.datetime.now().replace(microsecond = 0), thisNode.weekSchedule)

def getThisNodeData():
    """Returns the current node's info from the DB, None if not found in the DB."""
    try:
        [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (Utils.myHostName(),))
    except ValueError:
        thisNode = None
    return thisNode

def onlineNode(node):
    """Sets a node to be online given it's node object"""
    if node.status == IDLE:
        return
    elif node.status == OFFLINE:
        node.status = IDLE
    elif node.status == PENDING and node.task_id:
        node.status = STARTED
    with transaction() as t:
        node.update(t)

def offlineNode(node):
    """Sets a node to be offline given it's node object"""
    if node.status == OFFLINE:
            return
    elif node.task_id:
        node.status = PENDING
    else:
        node.status = OFFLINE
    with transaction() as t:
            node.update(t)
