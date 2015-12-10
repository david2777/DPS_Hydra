import datetime
import threading

#TODO:Fix all of this

isStarted = 0

def mainLoop():
    startTime = datetime.time(23, 59, 00)   #Need to set this for testing
    endTime = datetime.time(23, 58, 15)     #Need to set this for testing
    
    #Run the loop on the interval set above
    #TODO:Better way to do this?
    threading.Timer(interval, mainLoop).start()
    
    now = datetime.datetime.now().time().replace(microsecond = 0)
    print "Current time:\t\t" + str(now)
    
    global isStarted
            
    if isStarted == 0:
        print "Waiting for start @:\t" + str(startTime) + "\n"
        if startTime <= now:
            isStarted = 1
            print "\n\nTriggering Startup Event\n\n"
            
    elif isStarted == 1:
        print "Waiting for end @:\t" + str(endTime) + "\n"
        if endTime <= now:
            isStarted = 0
            print "\n\nTriggering Shutdown Event\n\n"

if __name__ == "__main__":
    interval = 5.0    #5 seconds for testing
    mainThread = threading.Timer(interval, mainLoop)
    mainThread.start()
