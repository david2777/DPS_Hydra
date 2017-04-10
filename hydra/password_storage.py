#Strandard
import sys
from getpass import getpass

#Third Party
import MySQLdb
from PyQt4 import QtGui
import keyring

#Hydra
from hydra.logging_setup import logger
import hydra.hydra_utils as hydra_utils

#Hydra Qt
from dialogs_qt.LoginWidget import DatabaseLogin

#pylint: disable=E1101

def storeCredentials(username, _password):
    keyring.set_password("Hydra", username, _password)
    logger.info("Password Stored in Credentials Vault")

def loadCredentials(username):
    logger.info("Fetching login for %s", username)
    return keyring.get_password("Hydra", username)

def updateAutologinUser(newUsername):
    if hydra_utils.get_info_from_cfg("database", "username") != newUsername:
        return hydra_utils.write_info_to_cfg("database", "username", newUsername)

def consolePrompt():
    print "\n\nStore Auto Login information?"
    #Get Login Information
    username = raw_input("Username: ")
    _password = getpass("Password: ")
    #Get DB Info
    host = hydra_utils.get_info_from_cfg("database", "host")
    domain = hydra_utils.get_info_from_cfg("network", "dnsDomainExtension").replace(" ", "")
    if domain != "" and host != "localhost":
        host += ".{}".format(domain)
    databaseName = hydra_utils.get_info_from_cfg("database", "db")
    port = int(hydra_utils.get_info_from_cfg("database", "port"))

    #Check  if login is valid
    try:
        MySQLdb.connect(host=host, user=username, passwd=_password,
                        db=databaseName, port=port)
        storeCredentials(username, _password)
        updateAutologinUser(username)

    except MySQLdb.Error:
        print "Login information was invalid!"

def qtPrompt():
    app = QtGui.QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.show()
    app.exec_()
    username, _password = loginWin.getValues()
    autoLogin = hydra_utils.get_info_from_cfg("database", "autologin")
    autoLogin = True if str(autoLogin).lower().startswith("t") else False
    if username and autoLogin:
        updateAutologinUser(username)
        storeCredentials(username, _password)
    return username, _password
