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

def store_credentials(username, _password):
    keyring.set_password("Hydra", username, _password)
    logger.info("Password Stored in Credentials Vault")

def load_credentials(username):
    logger.info("Fetching login for %s", username)
    return keyring.get_password("Hydra", username)

def update_autologin_user(newUsername):
    if hydra_utils.get_info_from_cfg("database", "username") != newUsername:
        return hydra_utils.write_info_to_cfg("database", "username", newUsername)

def console_prompt():
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
        store_credentials(username, _password)
        update_autologin_user(username)

    except MySQLdb.Error:
        print "Login information was invalid!"

def qt_prompt():
    app = QtGui.QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.show()
    app.exec_()
    username, _password = loginWin.getValues()
    autoLogin = hydra_utils.get_info_from_cfg("database", "autologin")
    autoLogin = True if str(autoLogin).lower().startswith("t") else False
    if username and autoLogin:
        update_autologin_user(username)
        store_credentials(username, _password)
    return username, _password
