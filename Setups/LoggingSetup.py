"""Sets up a global logger instance for use in other modules."""
#Standard
import os
import logging
import logging.handlers
from sys import argv

#Hydra
from Constants import BASELOGDIR

#Originally By : David Gladstein
#Taken from Cogswell's Project Hydra

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

if argv[0]:
    appname = argv[0].split('\\')[-1]
    appname = os.path.splitext(appname)[0]
else:
    appname = "interpreter_output"

if not os.path.isdir(BASELOGDIR):
    os.makedirs(BASELOGDIR)

logfileName = os.path.join(BASELOGDIR, appname + '.txt')

complexFormatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                      "%(pathname)s line %(lineno)s\n"
                                      "%(asctime)s\n")

simpleFormatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                      "%(asctime)s\n")

#Console Logger
h1 = logging.StreamHandler()
h1.setLevel(logging.DEBUG)
h1.setFormatter(complexFormatter)
logger.addHandler(h1)

#File Logger
h2 = logging.handlers.TimedRotatingFileHandler(logfileName, when='midnight')
h2.setLevel(logging.INFO)
h2.setFormatter(simpleFormatter)
logger.addHandler(h2)


#'application' code
if __name__ == '__main__':
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
