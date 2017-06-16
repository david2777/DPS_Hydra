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

def cfg_check():
    """Checks if CFG file exists, tries to copy one if it does not"""
    if not os.path.exists(Constants.SETTINGS):
        folder = os.path.dirname(Constants.SETTINGS)
        logger.debug("Check for folder %s", folder)
        if not os.path.exists(folder):
            logger.debug("Make %s", folder)
            os.mkdir(folder)
        cfgFile = find_resource(os.path.basename(Constants.SETTINGS))
        if not os.path.exists(cfgFile):
            err = "Unable to find base config file @ {}".format(cfgFile)
            logger.critical(err)
            raise Exception(err)
        logger.debug("Copy %s", cfgFile)
        shutil.copyfile(cfgFile, Constants.SETTINGS)
        if not os.path.exists(Constants.SETTINGS):
            err = "Unable to find or create config file @ {}".format(Constants.SETTINGS)
            logger.critical(err)
            raise Exception(err)
        else:
            return True
    else:
        return True

def get_info_from_cfg(section, option):
    """Return information from the local configuration file."""
    cfg_check()
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)
    return str(config.get(section=section, option=option)).strip()

def write_info_to_cfg(section, option, value):
    cfg_check()
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)

    config.set(section, option, value)

    with open(Constants.SETTINGS, "wb") as configFile:
        config.write(configFile)

def my_host_name():
    """Return this computers hostname with the dns extension from the local
    configuration file."""
    baseName = socket.gethostname()
    domain = get_info_from_cfg("network", "dnsDomainExtension")
    if domain:
        return "{0}.{1}".format(baseName, domain)
    else:
        return baseName

def flanged(name):
    return name.startswith('__') and name.endswith('__')

def non_flanged(name):
    return not flanged(name)
