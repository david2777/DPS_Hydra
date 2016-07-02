"""Sets up a global logger instance for use in other modules."""
#Standard
import os
import logging
import logging.handlers
import sys

#Hydra
from Constants import BASELOGDIR

#Originally By : David Gladstein
#Taken from Cogswell's Project Hydra

logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

if sys.argv[0]:
    appname = sys.argv[0].split('\\')[-1]
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

#Open Console Logger if Console exsits, else redirect stderr to stdout
try:
    if sys.stdout.isatty():
        h1 = logging.StreamHandler()
        h1.setLevel(logging.DEBUG)
        h1.setFormatter(complexFormatter)
        logger.addHandler(h1)
except AttributeError:
    sys.stderr = sys.stdout

#Always log to file but only INFO and above
h2 = logging.handlers.TimedRotatingFileHandler(logfileName, when='midnight',
                                                backupCount = 7)
h2.setLevel(logging.INFO)
h2.setFormatter(complexFormatter)
logger.addHandler(h2)


#'application' code
if __name__ == '__main__':
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
