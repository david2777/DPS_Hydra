"""Treaded functions that were too annoying to kill when running RenderNodeMain
as a serivce (via RenderNodeService). It is much easier to run these as a 
subprocess and kill them upon shutdown rather than trying to get the threads 
to notice the shutdown signal."""
#Standard
import threading
import datetime

#Hydra
from LoggingSetup import logger
import NodeUtils
from RenderNodeMain import heartbeat 
import NodeScheduler

if __name__ == "__main__":
    logger.info("Starting Render Node Externals")
    try:
        pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
        pulseThread.start()
        logger.info("Pulse Thread Started!")
    except Exception as e:
        logger.error(e)
        raise
    
    try:
        startTime, endTime, isStarted = NodeScheduler.getSchedule(NodeUtils.getThisNodeData())
        if startTime:
            holidayData = NodeScheduler.hydra_holidays.fetch()
            holidays = []
            for holiday in holidayData:
                holidaySplit = holiday.date.split(",")
                holidaySplit = [int(d) for d in holidaySplit]
                holidays.append(datetime.date(holidaySplit[0], holidaySplit[1], holidaySplit[2]))
            schedThread = threading.Thread(target = NodeScheduler.schedThread, name = "scheduler", args = (60, startTime, endTime, isStarted, holidays))
            schedThread.start()
            logger.info("Scheduler Thread Started!")
        else:
            logger.info("Running node in manual mode...")
    except Exception as e:
        logger.error(e)
        raise
