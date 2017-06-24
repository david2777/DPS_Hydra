#Standard
import threading

#Hydra
from hydra.logging_setup import logger

class stoppableThread(threading.Thread):
    def __init__(self, targetFunction, interval, threadName, delayedRun=False):
        self.targetFunction = targetFunction
        self.interval = interval
        self.threadName = threadName
        self.delayedRun = delayedRun
        self.status = False

    def tgt(self):
        if self.delayedRun:
            self.stopEvent.wait(self.interval)
        while not self.stopEvent.is_set():
            self.targetFunction()
            self.stopEvent.wait(self.interval)

    def start(self):
        if not self.status:
            logger.debug("Starting %s", self.threadName)
            self.status = True
            self.stopEvent = threading.Event()
            self.threadOBJ = threading.Thread(target=self.tgt, name=self.threadName)
            self.threadOBJ.deamon = True
            self.threadOBJ.start()
        else:
            logger.warning("Could not start %s because it is already running", self.threadName)

    def terminate(self):
        if self.status:
            logger.debug("Killing %s", self.threadName)
            self.status = False
            self.stopEvent.set()
        else:
            logger.warning("Could not kill %s because it is not running", self.threadName)
