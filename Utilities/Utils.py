"""Miscellaneous pieces of useful code"""
#Standard
import ConfigParser
import os
import sys
import itertools
import shutil
import socket
import xml.etree.ElementTree as ET

#Hydra
from Setups.LoggingSetup import logger
import Constants

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

def getInfoFromCFG(section, option):
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)
    #Create a copy if it doesn't exist
    if not os.path.exists(Constants.SETTINGS):
        folder = os.path.dirname(Constants.SETTINGS)
        logger.info('Check for folder {0}'.format(folder))
        if os.path.exists(folder):
            logger.info('{0} Exists'.format(folder))
        else:
            logger.info('Make {0}'.format(folder))
            os.mkdir(folder)
        cfgFile = os.path.join(os.path.dirname(sys.argv[0]), os.path.basename(Constants.SETTINGS))
        logger.info('Copy {0}'.format(cfgFile))
        shutil.copyfile(cfgFile, Constants.SETTINGS)

    config.read(Constants.SETTINGS)

    return config.get(section = section, option = option)

def getDbInfo():
    host = getInfoFromCFG("database", "host")
    db = getInfoFromCFG("database", "db")
    username = getInfoFromCFG("database", "username")
    password = getInfoFromCFG("database", "password")
    return host, db, username, password

def myHostName():
    """This computer's host name in the RenderHost table"""
    domain = getInfoFromCFG("network", "dnsDomainExtension")
    return socket.gethostname() + domain

def getRedshiftPreference(attribute):
    """Returns an attribute from the Redshift preferences.xml file"""
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
    """
    Receive all bytes from a socket, with no buffer size limit
    Generator to recieve strings from socket, will return
    Empty strings(forever) upon EOF
    """
    receivedStrings  = (sock.recv(Constants.MANYBYTES)
                        for i in itertools.count(0))
    #Concatenate the nonempty ones
    return ''.join(itertools.takewhile(len, receivedStrings))

def flushOut(f):
    "Flush and sync a file to disk"
    f.flush()
    os.fsync(f.fileno())
