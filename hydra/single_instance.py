#Standard
import os
import sys

#Hydra
from hydra.logging_setup import logger
from Constants import BASEDIR

#Fix pylint issues from importing based on platform and catch-all exception handling
#pylint: disable=W0703,E1101,E0602,E0401

class InstanceLock(object):
    def __init__(self, name):
        self.locked = False
        self.name = name
        self.tempFilePath = os.path.join(BASEDIR, "{}.lock".format(self.name))
        self.tempFilePath = os.path.abspath(self.tempFilePath)
        logger.info("Temp File: %s", self.tempFilePath)

        #Windows
        if sys.platform.startswith("win"):
            try:
                if os.path.exists(self.tempFilePath):
                    os.unlink(self.tempFilePath)
                    logger.debug("Unlink %s", self.tempFilePath)
                self.tempFile = os.open(self.tempFilePath, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.locked = True
            except Exception as e:
                if e.errno == 13:
                    logger.error("Another Instance of %s is already running!", self.name)
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
                logger.error("Another Instance of %s is already running", self.name)

    def isLocked(self):
        return self.locked

    def remove(self):
        if not self.locked:
            return

        if sys.platform.startswith("win"):
            if hasattr(self, "tempFile"):
                try:
                    os.close(self.tempFile)
                    os.unlink(self.tempFilePath)
                except Exception as e:
                    logger.error(e)
            else:
                logger.warning("No temp file found for %s", self.name)
        else:
            try:
                fnctl.lockf(self.tempFile, fcntl.LOCK_UN)
                if os.path.isfile(self.tempFilePath):
                    os.unlink(self.tempFilePath)
            except Exception as e:
                logger.error(e)
