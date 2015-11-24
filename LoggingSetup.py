"""Sets up a global logger instance for use in other modules"""
#Standard
import logging                      # @UnusedImport
import logging.handlers
import os
from sys import argv

#Project Hydra
from Constants import BASELOGDIR

#Author: David Gladstein
#Taken from Cogswell's Project Hydra

#Global logger instance
logger = logging.getLogger()

#Log messages of all severities
logger.setLevel(logging.DEBUG)

if argv[0]:
    #Get the file name of the currently running process
    appname = argv[0].split('\\')[-1]
    
    #Discard the file extension
    appname = os.path.splitext(appname)[0]
else:
    appname = "interpreter_output"

if not os.path.isdir (BASELOGDIR):
    os.makedirs (BASELOGDIR)

#Set the log file path to BASELOGDIR\appname.txt
logfileName = os.path.join( BASELOGDIR, appname + '.txt')

for handler in [logging.StreamHandler(), logging.handlers.TimedRotatingFileHandler(logfileName, when='midnight' ),]:
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                  "%(pathname)s line %(lineno)s\n"
                                  "%(asctime)s\n")

    handler.setFormatter(formatter)
    logger.addHandler(handler)

#'application' code
if __name__ == '__main__':
        logger.debug('debug message')
        logger.info('info message')
        logger.warn('warn message')
        logger.error('error message')
        logger.critical('critical message')
