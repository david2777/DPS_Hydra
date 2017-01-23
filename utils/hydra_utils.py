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
from hydra.logging_setup import logger
import Constants

def changeHydraEnviron(newEnviron):
    if sys.platform == "win32":
        logger.info("Changing Hydra Environ to %s", newEnviron)
        proc = subprocess.Popen(["setx", "HYDRA", newEnviron], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        if out.find("SUCCESS") > 0:
            os.environ["HYDRA"] = newEnviron
            return True
        else:
            logger.critical("Could not change enviromental variable!")
            return False
    else:
        raise "Not Implemented!"

def launchHydraApp(app, wait=0):
    """Primarily for killing the app and restarting it"""
    hydraPath = os.getenv("HYDRA")

    if not hydraPath:
        logger.error("HYDRA enviromental variable does not exit!")
        return None

    if sys.platform == "win32":
        execs = os.listdir(hydraPath)
        if not any([x.startswith(app) for x in execs]):
            logger.error("%s is not a vaild Hydra Win32 App", app)
            return None

    distFolder, _ = os.path.split(hydraPath)
    shortcutPath = os.path.join(distFolder, "_shortcuts")
    ext = ".bat" if sys.platform == "win32" else ".sh"
    script = "StartHydraApp{}".format(ext)
    scriptPath = os.path.join(shortcutPath, script)

    command = [scriptPath, app]
    if wait > 0:
        command += [str(int(wait))]
    subprocess.Popen(command, stdout=False)

def softwareUpdater():
    hydraPath = os.getenv("HYDRA")

    if not hydraPath:
        logger.error("HYDRA enviromental variable does not exit!")
        return False

    hydraPath, thisVersion = os.path.split(hydraPath)
    try:
        currentVersion = float(thisVersion.split("_")[-1])
    except ValueError:
        logger.warning("Unable to obtain version number from file path. Assuming version number from Constants")
        currentVersion = Constants.VERSION

    versions = os.listdir(hydraPath)
    versions = [float(x.split("_")[-1]) for x in versions if x.startswith("dist_")]
    if not versions:
        return False
    highestVersion = max(versions)
    logger.debug("Comparing versions. Env: %s Latest: %s", currentVersion, highestVersion)
    if highestVersion > currentVersion:
        logger.info("Update found! Current Version is %s / New Version is %s", currentVersion, highestVersion)
        newPath = os.path.join(hydraPath, "dist_{}".format(highestVersion))
        response = changeHydraEnviron(newPath)
        if not response:
            logger.critical("Could not update to newest environ for some reason!")
        return response
    else:
        return False

def findResource(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(basePath, relativePath)

def buildSubprocessArgs(include_stdout=False):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    ret = {'stdin': subprocess.PIPE,
            'startupinfo': si, 'env': env}

    if include_stdout:
        ret.update({'stdout:': subprocess.PIPE})

    return ret

def getInfoFromCFG(section, option):
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
        cfgFile = findResource(os.path.basename(Constants.SETTINGS))
        logger.info("Copy %s", cfgFile)
        shutil.copyfile(cfgFile, Constants.SETTINGS)

    config.read(Constants.SETTINGS)
    return config.get(section=section, option=option)

def writeInfoToCFG(section, option, value):
    config = ConfigParser.RawConfigParser()
    config.read(Constants.SETTINGS)
    #Make sure it exists
    if not os.path.exists(Constants.SETTINGS):
        return

    config.set(section, option, value)

    with open(Constants.SETTINGS, "wb") as configFile:
        config.write(configFile)

def myHostName():
    """Return this computers hostname with the dns extension from the local
    configuration file."""
    baseName = socket.gethostname()
    domain = getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
    if domain != "":
        return "{0}.{1}".format(baseName, domain)
    else:
        return baseName

def getRedshiftPreference(attribute):
    """Return an attribute from the Redshift preferences.xml file"""
    if sys.platform == "win32":
        try:
            tree = ET.parse("C:\\ProgramData\\Redshift\\preferences.xml")
        except IOError:
            logger.error("Could not find Redshift Preferences!")
            return None
    else:
        #TODO:Other platforms
        return None
    root = tree.getroot()
    perfDict = {c.attrib["name"]:c.attrib["value"] for c in root}
    try:
        return perfDict[attribute]
    except KeyError:
        logger.error("Could not find %s in Redshift Preferences!", attribute)
        return None

def flanged(name):
    return name.startswith('__') and name.endswith('__')

def nonFlanged(name):
    return not flanged(name)

def sockRecvAll(sock):
    """Receive all bytes from a socket, with no buffer size limit"""
    receivedStrings = (sock.recv(Constants.MANYBYTES) for i in itertools.count(0))
    #Concatenate the nonempty ones
    return ''.join(itertools.takewhile(len, receivedStrings))

def flushOut(f):
    """Flush and sync a file to disk"""
    f.flush()
    os.fsync(f.fileno())
