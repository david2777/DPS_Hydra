#Standard
import datetime
import threading

#Hydra
from LoggingSetup import logger
import NodeUtils
import NodeSchedules

def mainLoop():
    #Need these in global so that they don't get reset every time the loop runs
    global isStarted
    global startTime 
    global endTime
    
    now = datetime.datetime.now().replace(microsecond = 0)
    print "Current time:\t\t" + str(now)
            
    if isStarted == 0:
        print "Waiting for start @:\t" + str(startTime) + "\n"
        if startTime <= now:
            isStarted = 1
            newDate = now.date() + datetime.timedelta(days = 1)
            newTime = startTime.time()
            startTime = datetime.datetime.combine(newDate, newTime)
            print "\n\nTriggering Startup Event\n\n"
            
    elif isStarted == 1:
        print "Waiting for end @:\t" + str(endTime) + "\n"
        if endTime <= now:
            newDate = now.date() + datetime.timedelta(days = 1)
            newTime = endTime.time()
            endTime = datetime.datetime.combine(newDate, newTime)
            isStarted = 0
            print "\n\nTriggering Shutdown Event\n\n"
    
    
    interval = 5.0      #5 seconds for testing        
    mainThread = threading.Timer(interval, mainLoop)
    mainThread.start()
    
def getSchedule(nodeOBJ):
    if nodeOBJ.status == "I" or nodeOBJ.status == "S":
        isStarted = 1
    else:
        isStarted = 0
        
    nodeTimes = NodeSchedules.ScheduleDict[nodeOBJ.schedule]
    if nodeTimes[0] != None:
        nodeSch = []
        nowDate = datetime.datetime.now().date()
        for time in nodeTimes:
            nodeSch.append(datetime.datetime.combine(nowDate, time))
        
        if nodeSch[1] <= datetime.datetime.now():
            logger.debug("End time has passed, incrementing")
            for i in range(2):
                nodeSch[i] = nodeSch[i] + datetime.timedelta(days = 1)
        
    else:
        nodeSch = nodeTimes
        
    return nodeSch[0], nodeSch[1], isStarted


if __name__ == "__main__":
    isStarted = 0
    startTime, endTime, isStarted = getSchedule(NodeUtils.getThisNodeData())
    if startTime != None:
        mainLoop()
    else:
        logger.info("Node schedule set to 0, in manual control mode.")
