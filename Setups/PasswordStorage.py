#Strandard
import os
import sys
from getpass import getpass

#Third Party
import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import keyring

#Hydra
from Setups.LoggingSetup import logger
import Utilities.Utils as Utils

#Hydra Qt
from Dialogs.LoginWidget import DatabaseLogin

def storeCredentials(username, _password):
    keyring.set_password("Hydra", username, _password)
    logger.info("Password Stored in Credentials Vault")

def loadCredentials(username):
    logger.info("Fetching login for {0}".format(username))
    return keyring.get_password("Hydra", username)

def updateAutologinUser(newUsername):
    if Utils.getInfoFromCFG("database", "username") != newUsername:
        return Utils.writeInfoToCFG("database", "username", newUsername)

def consolePrompt():
    print "\n\nStore Auto Login information?"
    #Get Login Information
    username = raw_input("Username: ")
    _password = getpass("Password: ")
    #Get DB Info
    host = Utils.getInfoFromCFG("database", "host")
    domain = Utils.getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
    if domain != "" and host != "localhost":
        host += ".{}".format(domain)
    databaseName = Utils.getInfoFromCFG("database", "db")
    port = int(Utils.getInfoFromCFG("database", "port"))

    #Check  if login is valid
    try:
        MySQLdb.connect(host = host, user = username, passwd = _password,
                        db = databaseName, port = port)
        storeCredentials(username, _password)
        updateAutologinUser(username)

    except MySQLdb.Error:
        print "Login information was invalid!"

def qtPrompt():
    app = QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.show()
    retcode = app.exec_()
    username, _password = loginWin.getValues()
    autoLogin = Utils.getInfoFromCFG("database", "autologin")
    autoLogin = True if str(autoLogin).lower().startswith("t") else False
    if username and autoLogin:
        updateAutologinUser(username)
        storeCredentials(username, _password)
    return username, _password
