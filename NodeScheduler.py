import datetime
import threading

#TODO:Fix all of this

isStarted = 0
startTime = datetime.datetime(2015, 11, 13, 18, 30, 00)
endTime = datetime.datetime(2015, 12, 13, 20, 00, 00)

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

if __name__ == "__main__":
    mainLoop()
