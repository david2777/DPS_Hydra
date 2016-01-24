#Standard
import threading

#Hydra
from LoggingSetup import logger
import Utils
from MySQLSetup import transaction
from RenderNodeMain import heartbeat 
from NodeScheduler import schedThread as scheduler

if __name__ == "__main__":
    logger.info("Starting Render Node Externals")
    try:
        pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
        pulseThread.start()
        logger.info("Pulse Thread Started!")
    except Exception, e:
        logger.error(e)
        traceback.print_exc(e, log)
        raise
    
    try:
        schedThread = threading.Thread(target = scheduler, name = "scheduler", args = (60,))
        schedThread.start()
        logger.info("Scheduler Thread Started!")
    except Exception, e:
        logger.error(e)
        traceback.print_exc(e, log)
        raise
