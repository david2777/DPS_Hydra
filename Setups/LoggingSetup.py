"""Sets up a global logger instance for use in other modules."""
#Standard
import os
import logging
import logging.handlers
import sys
import ConfigParser

#Hydra
from Constants import BASELOGDIR, SETTINGS

#-------------------------------Initialize-------------------------------------#
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

#-------------------------------Load Config------------------------------------#
#Logs will be much more verbose if debug is set to True in the config file
try:
    config = ConfigParser.RawConfigParser()
    config.read(SETTINGS)
    debugMode = config.get(section = "hydra", option = "debug")
    debugMode = True if str(debugMode).lower() == "true" else False
    configErr = False
except ConfigParser.NoSectionError:
    debugMode = True
    configErr = True

#-------------------------------Formatters-------------------------------------#
consoleFormatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                      "%(pathname)s line %(lineno)s\n"
                                      "%(asctime)s\n")

outputWindowFormatter = logging.Formatter("%(levelname)-9s [%(asctime)s]: %(message)s\n",
                                            "%m-%d %H:%M:%S")

if debugMode:
    fileFormatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                          "%(pathname)s line %(lineno)s\n"
                                          "%(asctime)s\n")
else:
    fileFormatter = logging.Formatter("%(levelname)-9s%(message)s\n"
                                          "%(asctime)s\n", "%Y-%m-%d %H:%M:%S")

#-----------------------------Console Logger-----------------------------------#
#Make sure we have a console window attached
try:
    if sys.stdout.isatty():
        consoleLogger = logging.StreamHandler()
        consoleLogger.setLevel(logging.DEBUG)
        consoleLogger.setFormatter(consoleFormatter)
        logger.addHandler(consoleLogger)
except AttributeError:
    sys.stderr = sys.stdout

#-------------------------------File Logger------------------------------------#
if sys.argv[0]:
    appname = sys.argv[0].split('\\')[-1]
    appname = os.path.splitext(appname)[0]
else:
    appname = "interpreter_output"

if not os.path.isdir(BASELOGDIR):
    os.makedirs(BASELOGDIR)

logfileName = os.path.join(BASELOGDIR, appname + '.txt')

fileLogger = logging.handlers.TimedRotatingFileHandler(logfileName,
                                                        when = 'midnight',
                                                        backupCount = 7)
fileLogger.setLevel(logging.DEBUG if debugMode else logging.INFO)
fileLogger.setFormatter(fileFormatter)
logger.addHandler(fileLogger)

if configErr:
    logger.error("Could not find config file when setting up formatter! Maybe because node had yet to be registered.")
