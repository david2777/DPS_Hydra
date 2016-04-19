#Standard
import sys
import os
import ConfigParser
import shutil

#Hydra
import Constants
from Setups.LoggingSetup import logger

#3rd party
import MySQLdb

#QT
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from CompiledUI.UI_Login import Ui_Login
from MessageBoxes import aboutBox

def getDbInfo():
    SETTINGS = Constants.SETTINGS
    #Open config file
    config = ConfigParser.RawConfigParser()
    #Create a copy if it doesn't exist
    if not os.path.exists(SETTINGS):
        folder = os.path.dirname(SETTINGS)
        logger.info('Check for folder {0}'.format(folder))
        if os.path.exists(folder):
            logger.info('{0} Exists'.format(folder))
        else:
            logger.info('Make {0}'.format(folder))
            os.mkdir(folder)
        cfgFile = os.path.join(os.path.dirname(sys.argv[0]), os.path.basename(SETTINGS))
        logger.info('Copy {0}'.format(cfgFile))
        shutil.copyfile(cfgFile, SETTINGS)

    config.read(SETTINGS)

    #Get server & db names
    host = config.get(section="database", option="host")
    db = config.get(section="database", option="db")
    #Get Username and Password
    username = config.get(section="database", option="username")
    password = config.get(section="database", option="password")

    return host, db, username, password


class DatabaseLogin(QWidget, Ui_Login):
    #Set autoLogin and get default DB info from .cfg
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self._db_host, self._db_name, self._db_username, self._db_password = getDbInfo()

        QObject.connect(self.loginButton, SIGNAL("clicked()"),
                        self.loginButtonHandler)

        self.loginSuccess = False


    def getValues(self):
        if self.loginSuccess:
            return self._db_host, self._db_name, self._db_username, self._db_password
        else:
            return None, None, None, None

    def closeEvent(self, event):
        """Make it so when the user presses the X in the window it exits
        rather than just closing the login window and opening FarmView"""
        event.accept()
        if not self.loginSuccess:
            sys.exit(1)


    def loginButtonHandler(self):
        self._db_username = str(self.user.text())
        self._db_password = str(self.password.text())

        if self.remoteAccess.isChecked():
            #self.host = "REMOTE"
            pass

        try:
            MySQLdb.connect(self._db_host,
                                        user=self._db_username,
                                        passwd = self._db_password,
                                        db=self._db_name)
            self.loginSuccess = True
            self.close()
        except MySQLdb.Error:
            aboutBox(self,
            "Could Not Login",
            "Invalid username/password or server is down...")
