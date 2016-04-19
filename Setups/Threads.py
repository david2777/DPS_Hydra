"""Some generic Threads all together in one happy file"""
#Standard
import threading
import time

#QT
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra
from Setups.LoggingSetup import logger

class stoppableThread(threading.Thread):
    def __init__(self, targetFunction, interval, tName):
        self.targetFunction = targetFunction
        self.interval = interval
        self.tName = tName
        self._flag = False
        self.stop = threading.Event()
        threading.Thread.__init__(self, target = self.tgt)

    def tgt(self):
        try:
            while (not self.stop.wait(1)):
                self._flag = True
                self.targetFunction()
                self.stop.wait(self.interval)
        finally:
            self._flag = False

    def terminate(self):
        logger.info("Killing {0} Thread...".format(self.tName))
        self.stop.set()

class workerSignalThread(QThread):
    def __init__(self, target, interval):
        QThread.__init__(self)
        self.target = target
        self.interval = interval
        logger.info("INIT")

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            #logger.info("Running...")
            self.emit(SIGNAL(self.target))
            time.sleep(self.interval)
