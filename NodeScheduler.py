"""Functions for the scheduler. The scheduler will online and offline nodes
at specific times of day. On limitation as of now is that it assumes
the shutdown time is tomorrow so if a node goes offline before startup and
comes online fater the startup time it will not startup until tomorrow."""
#Standard
import datetime
import time

#Hydra
from LoggingSetup import logger
import NodeUtils
from MySQLSetup import hydra_rendernode, hydra_holidays

def schedulerMain(startTime, endTime, isStarted, holidays):
    #Do the stuff
    if startTime == None:
        return

    now = datetime.datetime.now().replace(microsecond = 0)
    logger.info("Current time: {0}".format(str(now)))

    #If we're not started, check to see if we're in a condition to startup
    if not isStarted:
        #If it's a holiday, start it up!
        if datetime.date.today() in holidays:
            logger.info("Today is a holiday!")
            isStarted, startTime = startupEvent(now, isStarted, startTime)
        #If it's a weekend, start it up!
        elif datetime.date.today().isoweekday() in range(6, 8):
            logger.info("Today is a weekend!")
            isStarted, startTime = startupEvent(now, isStarted, startTime)
        #If not, check the curent time against the expected start time
        else:
            if startTime <= now:
                isStarted, startTime = startupEvent(now, isStarted, startTime)
            else:
                logger.info("Waiting for start @: {0}".format(startTime))

    #If we are started, check to see if we're in a condition to shutdown
    elif isStarted:
        if endTime <= now:
            isStarted, endTime = shutdownEvent(now, isStarted, endTime)
        else:
            logger.info("Waiting for end @: {0}".format(endTime))

    return startTime, endTime, isStarted, holidays

def startupEvent(now, isStarted, startTime):
    isStarted = True
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = startTime.time()
    startTime = datetime.datetime.combine(newDate, newTime)
    logger.info("Triggering Startup Event")
    return isStarted, startTime

def shutdownEvent(now, isStarted, endTime):
    isStarted = False
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = endTime.time()
    endTime = datetime.datetime.combine(newDate, newTime)
    logger.info("Triggering Shutdown Event")
    return isStarted, endTime

def getSchedule(nodeOBJ):
    #Get isStarted via node status
    logger.info("Getting Schedule")
    if not nodeOBJ.onlineTime or not nodeOBJ.offlineTime:
        return None, None, None

    if nodeOBJ.status == "I" or nodeOBJ.status == "S":
        isStarted = True
    else:
        isStarted = False

    #Get the curent schedule for the node
    now = datetime.datetime.now()

    sTimeData = nodeOBJ.onlineTime.split(",")
    sTimeData = [int(t) for t in sTimeData]
    startTime = datetime.time(sTimeData[0], sTimeData[1], sTimeData[2])

    eTimeData = nodeOBJ.offlineTime.split(",")
    eTimeData = [int(t) for t in eTimeData]
    endTime = datetime.time(eTimeData[0], eTimeData[1], eTimeData[2])


    nowDate = now.date()
    startDT = datetime.datetime.combine(nowDate, startTime)
    endDT = datetime.datetime.combine(nowDate, endTime)

    #Add one day to end time
    #This is assuming the the start time is before midnight and the end time is after midnight
    endDT += datetime.timedelta(days = 1)

    #Return the three things we need to run our loop
    return startDT, endDT, isStarted
