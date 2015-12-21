#Standard
import datetime
import threading

#Hydra
from LoggingSetup import logger
import NodeUtils
import NodeSchedules

def mainLoop():
    #Need these in global so that they don't get reset every time the loop runs
    #These has to be a better way to do this...
    global isStarted
    global startTime
    global endTime
    global holidays

    now = datetime.datetime.now().replace(microsecond = 0)
    print "Current time:\t\t" + str(now)

    #If we're not started, check to see if we're in a condition to startup
    if isStarted == 0:
        #If it's a holiday, start it up!
        if datetime.date.today() in holidays:
            print "Today is a holiday!"
            startupEvent(now)
        #If not, check the curent time against the expected start time
        else:
            if startTime <= now:
                startupEvent(now)
            else:
                print "Waiting for start @:\t" + str(startTime) + "\n"

    #If we are started, check to see if we're in a condition to shutdown
    elif isStarted == 1:
        if endTime <= now:
            shutdownEvent(now)
        else:
            print "Waiting for end @:\t" + str(endTime) + "\n"


    interval = 5.0      #5 seconds for testing
    mainThread = threading.Timer(interval, mainLoop)
    mainThread.start()

def startupEvent(now):
    global isStarted
    global startTime
    isStarted = 1
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = startTime.time()
    startTime = datetime.datetime.combine(newDate, newTime)
    print "\n\nTriggering Startup Event\n\n"

def shutdownEvent(now):
    global isStarted
    global endTime
    isStarted = 0
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = endTime.time()
    endTime = datetime.datetime.combine(newDate, newTime)
    print "\n\nTriggering Shutdown Event\n\n"

def getSchedule(nodeOBJ):
    #Get isStarted via node status
    if nodeOBJ.status == "I" or nodeOBJ.status == "S":
        isStarted = 1
    else:
        isStarted = 0

    #Get the curent schedule for the node
    try:
        timeList = NodeSchedules.ScheduleDict[nodeOBJ.schedule]
    except KeyError:
        logger.error("Invalid Schedule, update node's DB entry with a valid schedule entry")
        logger.info("Setting node to manual control mode due to scheduling error")
        return None, None, 0
    #If the start time is not None then it is probably a legit schedule
    if timeList[0] != None:
        nodeSch = []
        nowDate = datetime.datetime.now().date()
        for time in timeList:
            nodeSch.append(datetime.datetime.combine(nowDate, time))

        #End time needs to be tomorrow since I don't think we'll need to stop nodes before midnight
        nodeSch[1] = nodeSch[1] + datetime.timedelta(days = 1)

    else:
        nodeSch = timeList

    #Return the three things we need to run our loop
    return nodeSch[0], nodeSch[1], isStarted


if __name__ == "__main__":
    isStarted = 0
    startTime, endTime, isStarted = getSchedule(NodeUtils.getThisNodeData())
    holidays = NodeSchedules.HolidayList
    if startTime != None:
        mainLoop()
    else:
        logger.info("Node schedule set to 0, in manual control mode.")
