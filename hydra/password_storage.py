#Strandard
import sys
from getpass import getpass

#Third Party
import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import keyring

#Hydra
from hydra.logging_setup import logger
import utils.hydra_utils as hydra_utils

#Hydra Qt
from dialogs_qt.LoginWidget import DatabaseLogin

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

def storeCredentials(username, _password):
    keyring.set_password("Hydra", username, _password)
    logger.info("Password Stored in Credentials Vault")

def loadCredentials(username):
    logger.info("Fetching login for %s", username)
    return keyring.get_password("Hydra", username)

def updateAutologinUser(newUsername):
    if hydra_utils.getInfoFromCFG("database", "username") != newUsername:
        return hydra_utils.writeInfoToCFG("database", "username", newUsername)

def consolePrompt():
    print "\n\nStore Auto Login information?"
    #Get Login Information
    username = raw_input("Username: ")
    _password = getpass("Password: ")
    #Get DB Info
    host = hydra_utils.getInfoFromCFG("database", "host")
    domain = hydra_utils.getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
    if domain != "" and host != "localhost":
        host += ".{}".format(domain)
    databaseName = hydra_utils.getInfoFromCFG("database", "db")
    port = int(hydra_utils.getInfoFromCFG("database", "port"))

    #Check  if login is valid
    try:
        MySQLdb.connect(host=host, user=username, passwd=_password,
                        db=databaseName, port=port)
        storeCredentials(username, _password)
        updateAutologinUser(username)

    except MySQLdb.Error:
        print "Login information was invalid!"

def qtPrompt():
    app = QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.show()
    app.exec_()
    username, _password = loginWin.getValues()
    autoLogin = hydra_utils.getInfoFromCFG("database", "autologin")
    autoLogin = True if str(autoLogin).lower().startswith("t") else False
    if username and autoLogin:
        updateAutologinUser(username)
        storeCredentials(username, _password)
    return username, _password
