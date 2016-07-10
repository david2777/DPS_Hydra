"""Miscellaneous pieces of useful code that don't fit in elsewhere."""
#Standard
import ConfigParser
import os
import sys
import itertools
import shutil
import socket
import subprocess
import xml.etree.ElementTree as ET

#Hydra
from Setups.LoggingSetup import logger
import Constants

def findResource(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(basePath, relativePath)

def buildSubprocessArgs(include_stdout = False):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    if include_stdout:
        ret = {'stdout:': subprocess.PIPE}
    else:
        ret = {}

    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret

def getInfoFromCFG(section, option):
    """Return information from the local configuration file."""
    config = ConfigParser.RawConfigParser()
    #Create a copy if it doesn't exist
    if not os.path.exists(Constants.SETTINGS):
        folder = os.path.dirname(Constants.SETTINGS)
        logger.info('Check for folder {0}'.format(folder))
        if os.path.exists(folder):
            logger.info('{0} Exists'.format(folder))
        else:
            logger.info('Make {0}'.format(folder))
            os.mkdir(folder)
        cfgFile = findResource(os.path.basename(Constants.SETTINGS))
        logger.info('Copy {0}'.format(cfgFile))
        shutil.copyfile(cfgFile, Constants.SETTINGS)

    config.read(Constants.SETTINGS)
    return config.get(section = section, option = option)

def writeInfoToCFG(section, option, value):
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)
    #Make sure it exists
    if not os.path.exists(Constants.SETTINGS):
        return None

    config.set(section, option, value)

    with open(Constants.SETTINGS, "wb") as configFile:
        config.write(configFile)

def myHostName():
    """Return this computers hostname with the dns extension from the local
    configuration file."""
    domain = getInfoFromCFG("network", "dnsDomainExtension")
    return socket.gethostname() + domain

def getRedshiftPreference(attribute):
    """Return an attribute from the Redshift preferences.xml file"""
    if sys.platform == "win32":
        try:
            tree = ET.parse(r"C:\ProgramData\Redshift\preferences.xml")
        except IOError:
            logger.error("Could not find Redshift Preferences!")
            return
    else:
        #TODO:Other platforms
        return
    root = tree.getroot()
    perfDict = {c.attrib["name"]:c.attrib["value"] for c in root}
    try:
        returnVal = perfDict[attribute]
    except KeyError:
        returnVal = None
        logger.error("Could not find {0} in Redshift Preferences!".format(attribute))
    return returnVal

def flanged(name):
    return name.startswith ('__') and name.endswith ('__')

def nonFlanged(name):
    return not flanged(name)

def sockRecvAll(sock):
    """Receive all bytes from a socket, with no buffer size limit"""
    receivedStrings  = (sock.recv(Constants.MANYBYTES)
                        for i in itertools.count(0))
    #Concatenate the nonempty ones
    return ''.join(itertools.takewhile(len, receivedStrings))

def flushOut(f):
    """Flush and sync a file to disk"""
    f.flush()
    os.fsync(f.fileno())
