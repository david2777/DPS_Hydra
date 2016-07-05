#Standard
import sys

#Third Party
import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_Login import Ui_Login

#Hydra
from Utilities.Utils import getInfoFromCFG
from Setups.LoggingSetup import logger
from Dialogs.MessageBoxes import aboutBox

class DatabaseLogin(QWidget, Ui_Login):
    #Set autoLogin and get default DB info from .cfg
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.host = getInfoFromCFG("database", "host")
        self.databseName = getInfoFromCFG("database", "db")
        self.port = int(getInfoFromCFG("database", "port"))

        QObject.connect(self.loginButton, SIGNAL("clicked()"),
                        self.loginButtonHandler)

        self.loginSuccess = False


    def getValues(self):
        if self.loginSuccess:
            return self.db_username, self._db_password
        else:
            return None, None

    def closeEvent(self, event):
        """Make it so when the user presses the X in the window it exits
        rather than just closing the login window and opening FarmView"""
        event.accept()
        if not self.loginSuccess:
            sys.exit(1)


    def loginButtonHandler(self):
        self.db_username = str(self.user.text())
        self._db_password = str(self.password.text())

        if self.remoteAccess.isChecked():
            #self.host = "REMOTE"
            pass

        try:
            MySQLdb.connect(host = self.host,
                                user = self.db_username,
                                passwd = self._db_password,
                                db = self.databseName,
                                port = self.port)
            self.loginSuccess = True
            self.close()

        except MySQLdb.Error:
            aboutBox(self,
            "Could Not Login",
            "Invalid username/password or server is down...")
