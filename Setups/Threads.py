"""Some generic Threads all together in one happy file"""
#Standard
import threading
import time

#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra
from Setups.LoggingSetup import logger

class stoppableThread(threading.Thread):
    def __init__(self, targetFunction, interval, tName):
        self.targetFunction = targetFunction
        self.interval = interval
        self.tName = tName
        self.stopEvent = threading.Event()
        threading.Thread.__init__(self, target = self.tgt)

    def tgt(self):
        while not self.stopEvent.is_set():
            self.targetFunction()
            self.stopEvent.wait(self.interval)

    def terminate(self):
        logger.info("Killing {0} Thread...".format(self.tName))
        self.stopEvent.set()

class workerSignalThread(QThread):
    def __init__(self, target, interval):
        QThread.__init__(self)
        self.target = target
        self.interval = interval

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            #logger.info("Running...")
            self.emit(SIGNAL(self.target))
            time.sleep(self.interval)
