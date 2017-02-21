#Standard
import threading

#Hydra
from hydra.logging_setup import logger

class stoppableThread(threading.Thread):
    def __init__(self, targetFunction, interval, threadName):
        self.targetFunction = targetFunction
        self.interval = interval
        self.threadName = threadName
        self.stopEvent = threading.Event()
        self.threadOBJ = threading.Thread(target=self.tgt, name=self.threadName)
        self.threadOBJ.deamon = True
        self.threadOBJ.start()

    def tgt(self):
        while not self.stopEvent.is_set():
            self.targetFunction()
            self.stopEvent.wait(self.interval)

    def terminate(self):
        logger.debug("Killing %s", self.threadName)
        self.stopEvent.set()

    def restart(self):
        logger.debug("Restarting %s", self.threadName)
        self.stopEvent = threading.Event()
        self.threadOBJ = threading.Thread(target=self.tgt, name=self.threadName)
        self.threadOBJ.deamon = True
        self.threadOBJ.start()
