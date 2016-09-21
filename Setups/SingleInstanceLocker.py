#Standard
import os
import sys

#Hydra
from Setups.LoggingSetup import logger
from Constants import BASEDIR

class InstanceLock:
    def __init__(self, name):
        self.locked = False
        self.name = name
        self.tempFilePath = os.path.join(BASEDIR, "{}.lock".format(self.name))
        self.tempFilePath =  os.path.abspath(self.tempFilePath)
        logger.info("Temp File: {}".format(self.tempFilePath))

        #Windows
        if sys.platform == "win32":
            try:
                if os.path.exists(self.tempFilePath):
                    os.unlink(self.tempFilePath)
                    logger.debug("Unlink {}".format(self.tempFilePath))
                self.tempFile = os.open(self.tempFilePath, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.locked = True
            except Exception as e:
                if e.errno == 13:
                    logger.error("Another Instance of {} is already running!".format(self.name))
                else:
                    logger.error(e)
        #Linux
        else:
            import fcntl
            self.tempFile = open(self.tempFilePath, "w")
            self.tempFile.flush()
            try:
                fcntl.lockf(self.tempFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.locked = True
            except IOError:
                logger.error("Another Instance of {} is already running".format(self.name))

    def isLocked(self):
        return self.locked

    def remove(self):
        if not self.locked:
            return

        if sys.platform == "win32":
            if hasattr(self, "tempFile"):
                try:
                    os.close(self.tempFile)
                    os.unlink(self.tempFilePath)
                except Exception as e:
                    logger.error(e)
            else:
                logger.warning("No temp file found for {}".format(self.name))
        else:
            try:
                fnctl.lockf(self.tempFile, fcntl.LOCK_UN)
                if os.path.isfile(self.tempFilePath):
                    os.unlink(self.tempFilePath)
            except Exception as e:
                logger.error(e)
