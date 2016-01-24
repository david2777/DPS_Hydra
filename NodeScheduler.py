#Standard
import datetime
import threading
import time

#Hydra
from LoggingSetup import logger
import NodeUtils
from MySQLSetup import hydra_schedules, hydra_holidays

def schedThread(interval):
    #Do the stuff
    startTime, endTime, isStarted = getSchedule(NodeUtils.getThisNodeData())
    holidayData = hydra_holidays.fetch()
    holidays = []
    for holiday in holidayData:
        holidaySplit = holiday.date.split(",")
        holidaySplit = [int(d) for d in holidaySplit]
        holidays.append(datetime.date(holidaySplit[0], holidaySplit[1], holidaySplit[2]))
        
    
    if startTime == None:
        return
    
    while True:
        now = datetime.datetime.now().replace(microsecond = 0)
        print "Current time:\t\t" + str(now)

        #If we're not started, check to see if we're in a condition to startup
        if not isStarted:
            #If it's a holiday, start it up!
            if datetime.date.today() in holidays:
                print "Today is a holiday!"
                isStarted, startTime = startupEvent(now, isStarted, startTime)
            #If not, check the curent time against the expected start time
            else:
                if startTime <= now:
                    isStarted, startTime = startupEvent(now, isStarted, startTime)
                else:
                    print "Waiting for start @:\t" + str(startTime) + "\n"

        #If we are started, check to see if we're in a condition to shutdown
        elif isStarted:
            if endTime <= now:
                isStarted, endTime = shutdownEvent(now. isStarted, endTime)
            else:
                print "Waiting for end @:\t" + str(endTime) + "\n"
                
        time.sleep(interval)
        
def startupEvent(now, isStarted, startTime):
    isStarted = True
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = startTime.time()
    startTime = datetime.datetime.combine(newDate, newTime)
    print "\n\nTriggering Startup Event\n\n"
    return isStarted, startTime

def shutdownEvent(now, isStarted, endTime):
    isStarted = False
    newDate = now.date() + datetime.timedelta(days = 1)
    newTime = endTime.time()
    endTime = datetime.datetime.combine(newDate, newTime)
    print "\n\nTriggering Shutdown Event\n\n"
    return isStarted, endTime

def getSchedule(nodeOBJ):
    #Get isStarted via node status
    logger.info("Getting Schedule")
    if nodeOBJ.status == "I" or nodeOBJ.status == "S":
        isStarted = True
    else:
        isStarted = False

    #Get the curent schedule for the node
    now = datetime.datetime.now()
    nodeSch = [None, None]

    [timeData] = hydra_schedules.fetch("WHERE id = '{0}'".format(nodeOBJ.schedule))
    sTimeData = timeData.startTime.split(",")
    sTimeData = [int(t) for t in sTimeData]
    startTime = datetime.time(sTimeData[0], sTimeData[1], sTimeData[2])
    
    eTimeData = timeData.endTime.split(",")
    eTimeData = [int(t) for t in eTimeData]
    endTime = datetime.time(eTimeData[0], eTimeData[1], eTimeData[2])

    if startTime != None:
        timeList = [startTime, endTime]
        nodeSch = []
        nowDate = now.date()
        for time in timeList:
            nodeSch.append(datetime.datetime.combine(nowDate, time))

        #Add one day to end time
        #This is assuming the the start time is before midnight and the end time is after midnight
        nodeSch[1] = nodeSch[1] + datetime.timedelta(days = 1)

    #Return the three things we need to run our loop
    return nodeSch[0], nodeSch[1], isStarted


if __name__ == "__main__":
    schedThread = threading.Thread(target = schedThread, name = "schedThread", args = (5,))
    schedThread.start()
