"""Turns out you need admin to read/write to LSA"""
#Standard
import sys

#Third Party
import win32security
from pywintypes import error as WIN32ERROR
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra
from LoginWidget import DatabaseLogin, getDbInfo
from Setups.LoggingSetup import logger
from MessageBoxes import aboutBox

def storePrivateData(key, data):
    try:
        policy_handle = win32security.GetPolicyHandle('',win32security.POLICY_ALL_ACCESS)
    except WIN32ERROR:
        logger.error("Error! It looks like you don't have the right permissions to store data in LSA.")
        return False

    win32security.LsaStorePrivateData(policy_handle, key, data)

    #Make sure the data was stored correctly
    try:
        win32security.LsaRetrievePrivateData(policy_handle, key)
        win32security.LsaClose(policy_handle)
        return True
    except WIN32ERROR:
        win32security.LsaClose(policy_handle)
        logger.error("Could not find login password or key was invalid...")
        return False

def getPrivateData(key):
    try:
        policy_handle = win32security.GetPolicyHandle('',win32security.POLICY_ALL_ACCESS)
    except WIN32ERROR:
        logger.error("Error! It looks like you don't have the right permissions to read data from LSA.")
        return False
    try:
        data = win32security.LsaRetrievePrivateData(policy_handle, key)
        win32security.LsaClose(policy_handle)
        return data
    except WIN32ERROR:
        win32security.LsaClose(policy_handle)
        logger.error("Could not find login password or key was invalid...")
        return False

def deletePrivateData(key):
    try:
        policy_handle = win32security.GetPolicyHandle('',win32security.POLICY_ALL_ACCESS)
    except WIN32ERROR:
        logger.error("Error! It looks like you don't have the right permissions to delete data in LSA.")
        return False
    win32security.LsaStorePrivateData(policy_handle, key, None)
    win32security.LsaClose(policy_handle)
    return True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loginWin = DatabaseLogin()
    loginWin.setWindowTitle("Set Login Keys")
    loginWin.loginButton.setText("Store Keys")
    loginWin.show()
    retcode = app.exec_()
    _db_host, _db_name, _db_username, _db_password = loginWin.getValues()
    if _db_host != None:
        returnList = []
        returnList.append(storePrivateData("_db_host", _db_host))
        returnList.append(storePrivateData("_db_name", _db_name))
        returnList.append(storePrivateData("_db_username", _db_username))
        returnList.append(storePrivateData("_db_password", _db_password))
        if False in returnList:
            logger.error("Error setting valuses, rolling back...")
            deletePrivateData("_db_host")
            deletePrivateData("_db_name")
            deletePrivateData("_db_username")
            deletePrivateData("_db_password")
            aboutBox(loginWin, "Error Setting Values!", "An error occured while setting the values. All values were deleted. Read the output for more info.")
            sys.exit(retcode)
        else:
            aboutBox(loginWin, "Success!", "Values were stored successfully!")
    if retcode != 0:
        sys.exit(retcode)
    if _db_host ==  None:
        sys.exit(0)
