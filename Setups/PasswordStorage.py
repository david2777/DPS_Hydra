#Strandard
import os
import sys
from getpass import getpass

#Third Party
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
    username = raw_input("Username: ")
    _password = getpass("Password: ")
    #TODO: Make sure login is valid
    storeCredentials(username, _password)
    updateAutologinUser(username)

def qtPrompt():
    app = QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.show()
    retcode = app.exec_()
    username, _password = loginWin.getValues()
    if username:
        updateAutologinUser(username)
        storeCredentials(username, _password)
    return username, _password

if __name__ == "__main__":
    consolePrompt()
