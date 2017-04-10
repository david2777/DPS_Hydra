"""Miscellaneous pieces of useful code that don't fit in elsewhere."""
#Standard
import ConfigParser
import os
import sys
import shutil
import socket

#Hydra
from hydra.logging_setup import logger
import Constants

def find_resource(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(basePath, relativePath)

def get_info_from_cfg(section, option):
    """Return information from the local configuration file."""
    config = ConfigParser.RawConfigParser()
    #Create a copy if it doesn't exist
    if not os.path.exists(Constants.SETTINGS):
        folder = os.path.dirname(Constants.SETTINGS)
        logger.info("Check for folder %s", folder)
        if os.path.exists(folder):
            logger.info("%s Exists", folder)
        else:
            logger.info("Make %s", folder)
            os.mkdir(folder)
        cfgFile = find_resource(os.path.basename(Constants.SETTINGS))
        logger.info("Copy %s", cfgFile)
        shutil.copyfile(cfgFile, Constants.SETTINGS)

    config.read(Constants.SETTINGS)
    return config.get(section=section, option=option)

def write_info_to_cfg(section, option, value):
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)
    #Make sure it exists
    if not os.path.exists(Constants.SETTINGS):
        return

    config.set(section, option, value)

    with open(Constants.SETTINGS, "wb") as configFile:
        config.write(configFile)

def my_host_name():
    """Return this computers hostname with the dns extension from the local
    configuration file."""
    baseName = socket.gethostname()
    domain = get_info_from_cfg("network", "dnsDomainExtension").replace(" ", "")
    if domain != "":
        return "{0}.{1}".format(baseName, domain)
    else:
        return baseName

def flanged(name):
    return name.startswith('__') and name.endswith('__')

def non_flanged(name):
    return not flanged(name)
