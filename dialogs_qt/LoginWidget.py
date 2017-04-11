#Standard
import sys

#Third Party
import MySQLdb
from PyQt4 import QtGui

#Hydra Qt
from compiled_qt.UI_Login import Ui_Login

#Hydra
from hydra.hydra_utils import get_info_from_cfg
from hydra.logging_setup import logger
from dialogs_qt.MessageBoxes import about_box

#pylint: disable=E1101

class DatabaseLogin(QtGui.QWidget, Ui_Login):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.host = get_info_from_cfg("database", "host")
        self.databaseName = get_info_from_cfg("database", "db")
        self.port = int(get_info_from_cfg("database", "port"))

        self.loginButton.clicked.connect(self.login_button_handler)

        self.loginSuccess = False


    def get_values(self):
        if self.loginSuccess:
            return self.db_username, self._db_password
        else:
            return None, None

    def close_event(self, event):
        """Make it so when the user presses the X in the window it exits
        rather than just closing the login window and opening FarmView"""
        event.accept()
        if not self.loginSuccess:
            sys.exit(1)


    def login_button_handler(self):
        self.db_username = str(self.user.text())
        self._db_password = str(self.password.text())

        if self.remoteAccess.isChecked():
            #self.host = "REMOTE"
            pass

        try:
            MySQLdb.connect(host=self.host, user=self.db_username,
                            passwd=self._db_password, db=self.databaseName,
                            port=self.port)
            self.loginSuccess = True
            self.close()

        except MySQLdb.Error:
            logger.error("Could not login!")
            about_box(self, "Could Not Login",
            "Invalid username/password or server is down...")
