#Standard
import sys
import os
import logging
import traceback
import threading
import time

#Third Party
from MySQLdb import Error as sqlerror
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_RenderNodeMain import Ui_RenderNodeMainWindow
from Dialogs.NodeEditorDialog import NodeEditorDialog
from Dialogs.MessageBoxes import aboutBox, yesNoBox

#Hydra
import RenderNode
from Setups.LoggingSetup import logger, outputWindowFormatter
from Setups.MySQLSetup import *
from Setups.Threads import stoppableThread, workerSignalThread
import Utilities.NodeUtils as NodeUtils
import Utilities.Utils as Utils
from Setups.SingleInstanceLocker import InstanceLock

class EmittingStream(QObject):
    """For writing text to the console output"""
    textWritten = pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class RenderNodeMainUI(QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        with open(Utils.findResource("styleSheet.css"),"r") as myStyles:
            self.setStyleSheet(myStyles.read())

        self.thisNode = NodeUtils.getThisNodeOBJ()

        if not self.thisNode:
            self.offlineButton.setEnabled(False)
            self.getoffButton.setEnabled(False)
            logger.error("Node does not exist in database!")
            aboutBox(self, "Error",
                "This node was not found in the database! If you wish to render  "
                "on this node it must be registered with the databse. Run "
                "Register.exe or Register.py to regiester this node and "
                " try again.")
            sys.exit(1)

        self.currentSchedule = self.thisNode.weekSchedule
        self.currentScheduleEnabled = self.thisNode.scheduleEnabled

        self.buildUI()
        self.connectButtons()
        self.updateThisNodeInfo()
        #Note: sys.exit calls after this might not kill the server threads
        #TODO: Fix that
        self.startupServers()

        self.autoUpdateThread = workerSignalThread("run", 15)
        QObject.connect(self.autoUpdateThread, SIGNAL("run"), self.updateThisNodeInfo)
        self.autoUpdateThread.start()

        logger.info("Render Node Main is live! Waiting for tasks...")

        try:
            autoHide = True if str(sys.argv[1]).lower() == "true" else False
            logger.info(autoHide)
        except IndexError:
            autoHide = False

        if autoHide and self.trayIconBool:
            logger.info("Autohide is enabled!")
            self.sendToTrayHandler()
        else:
            self.show()

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()

    def buildUI(self):
        def addItem(name, handler, statusTip, menu):
            action = QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            menu.addAction(action)

        #Add Logging handlers for output field
        emStream = EmittingStream(textWritten=self.normalOutputWritten)
        handler = logging.StreamHandler(emStream)
        handler.setLevel(logging.INFO)
        handler.setFormatter(outputWindowFormatter)
        logger.addHandler(handler)

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        #Get Pixmaps and Icon
        self.donePixmap = QPixmap(Utils.findResource("Images/status/done.png"))
        self.inProgPixmap = QPixmap(Utils.findResource("Images/status/inProgress.png"))
        self.needsAttentionPixmap = QPixmap(Utils.findResource("Images/status/needsAttention.png"))
        self.nonePixmap = QPixmap(Utils.findResource("Images/status/none.png"))
        self.notStartedPixmap = QPixmap(Utils.findResource("Images/status/notStarted.png"))
        self.refreshPixmap = QPixmap(Utils.findResource("Images/refresh.png"))
        self.refreshIcon = QIcon()
        self.refreshIcon.addPixmap(self.refreshPixmap)
        self.RIcon = QIcon(Utils.findResource("Images/RenderNodeMain.png"))

        self.isVisable = True

        self.refreshButton.setIcon(self.refreshIcon)

        self.renderServerPixmap.setPixmap(self.notStartedPixmap)
        self.scheduleThreadPixmap.setPixmap(self.notStartedPixmap)
        self.pulseThreadPixmap.setPixmap(self.notStartedPixmap)
        self.setWindowIcon(self.RIcon)

        #Setup tray icon
        self.trayIcon=QSystemTrayIcon()
        self.trayIconBool = self.trayIcon.isSystemTrayAvailable()
        if self.trayIconBool:
            self.trayIcon.setIcon(self.RIcon)
            self.trayIcon.show()
            self.trayIcon.setVisible(True)
            self.trayIcon.activated.connect(self.activate)
            self.trayIcon.messageClicked.connect(self.activate)

            #Tray Icon Context Menu
            self.taskIconMenu = QMenu(self)

            addItem("Open", self.showWindowHandler,
                    "Show the RenderNodeMain Window", self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Update", self.updateThisNodeInfo,
                    "Fetch the latest information from the Database", self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Online", self.onlineThisNodeHandler,
                    "Online this node", self.taskIconMenu)
            addItem("Offline", self.offlineThisNodeHandler,
                    "Offline this node", self.taskIconMenu)
            addItem("GetOff!", self.getOffThisNodeHandler,
                    "Kill the current task and offline this node", self.taskIconMenu)

            self.trayIcon.setContextMenu(self.taskIconMenu)
        else:
            logger.error("Tray Icon Error! Could not create tray icon.")
            aboutBox(self, "Tray Icon Error",
                    "Could not create tray icon. Minimizing to tray has been disabled.")
            self.trayButton.setEnabled(False)

    def connectButtons(self):
        self.trayButton.clicked.connect(self.sendToTrayHandler)
        self.onlineButton.clicked.connect(self.onlineThisNodeHandler)
        self.offlineButton.clicked.connect(self.offlineThisNodeHandler)
        self.getoffButton.clicked.connect(self.getOffThisNodeHandler)
        self.clearButton.clicked.connect(self.clearOutputHandler)
        self.refreshButton.clicked.connect(self.updateThisNodeInfo)
        self.editThisNodeButton.clicked.connect(self.nodeEditorHandler)
        self.autoUpdateCheckBox.stateChanged.connect(self.autoUpdateHandler)
        if not self.trayIconBool:
            self.trayButton.setEnabled(False)

    def closeEvent(self, event):
        choice = yesNoBox(self, "Confirm", "Really exit the RenderNodeMain server?")
        if choice == QMessageBox.Yes:
            self.doExit()
        else:
            event.ignore()

    def doExit(self):
        logger.info("Shutting down...")
        #Force update UI
        self.autoUpdateThread.terminate()
        app.processEvents()
        if self.schedThreadStatus:
            self.schedThread.terminate()
        app.processEvents()
        if self.pulseThreadStatus:
            self.pulseThread.terminate()
        self.updateThisNodeInfo()
        app.processEvents()
        if self.thisNode.task_id:
            self.getOffThisNodeHandler()
        if self.renderServerStatus:
            self.renderServer.shutdownCMD()
            #Wait to make sure the render server is dead
            time.sleep(1)
        self.trayIcon.hide()
        app.processEvents()
        event.accept()
        sys.exit(0)

    def autoUpdateHandler(self):
        """Toggles Auto Updater
        Note that this is run AFTER the CheckState is changed so when we do
        .isChecked() it's looking for the state after it has been checked."""
        if not self.autoUpdateCheckBox.isChecked():
            self.autoUpdateThread.terminate()
        else:
            self.autoUpdateThread.start()

    def showWindowHandler(self):
        self.isVisable = True
        self.show()
        self.updateThisNodeInfo()

    def activate(self, reason):
        if reason==2:
            self.showWindowHandler()

    def __icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showWindowHandler()

    def sendToTrayHandler(self):
        self.isVisable = False
        self.trayIcon.show()
        self.hide()

    def onlineThisNodeHandler(self):
        response = self.thisNode.online()
        self.updateThisNodeInfo()
        if response:
            logger.info("Node Onlined")
        else:
            logger.error("Node could not be Onlined!")

    def offlineThisNodeHandler(self):
       response = self.thisNode.offline()
       self.updateThisNodeInfo()
       if response:
           logger.info("Node Offlined")
       else:
           logger.error("Node could not be Offlined!")

    def getOffThisNodeHandler(self):
        response = self.thisNode.getOff()
        self.updateThisNodeInfo()
        if response:
            logger.info("Node Offlined and Task Killed")
        else:
            logger.error("Node could not be Onlined or the Task could not be killed!")

    def clearOutputHandler(self):
        choice = yesNoBox(self, "Confirm", "Really clear output?")
        if choice == QMessageBox.Yes:
            self.outputTextEdit.clear()
            logger.info("Output cleared")

    def nodeEditorHandler(self):
        response = self.nodeEditor()
        if response:
            logger.info("Updating this node...")
            logger.info("Node updated!")
        else:
            logger.info("No changes detected. Nothing was changed.")

    def startupServers(self):
        logger.debug("Firing up main threads")
        #Startup Pulse thread
        self.pulseThreadStatus = False
        self.renderServerStatus = False
        self.schedThreadStatus = False

        self.pulseThread = stoppableThread(pulse, 60, "Pulse")
        try:
            self.pulseThread.start()
            self.pulseThreadStatus = True
            self.pulseThreadPixmap.setPixmap(self.donePixmap)
            logger.info("Pulse Thread started!")
        except Exception as e:
            logger.error("Exception: {0}".format(traceback.format_exc()))
            self.pulseThreadPixmap.setPixmap(self.needsAttentionPixmap)

        #Start Render Server
        try:
            self.renderServer = RenderNode.RenderTCPServer()
            self.renderServerStatus = True
            self.renderServerPixmap.setPixmap(self.donePixmap)
            logger.info("Render Server Started!")
        except Exception as e:
            logger.error("Exception: {0}".format(traceback.format_exc()))
            self.renderServerPixmap.setPixmap(self.needsAttentionPixmap)

        #Start Schedule Thread
        self.startScheduleThread()

    def startScheduleThread(self):
        if bool(self.currentScheduleEnabled) and self.currentSchedule:
            try:
                self.schedThread = schedulerThread(self.schedulerMain)
                self.schedThread.deamon = True
                self.schedThread.start()
                self.schedThreadStatus = True
                self.scheduleThreadPixmap.setPixmap(self.donePixmap)
                logger.info("Schedule Thread started!")
            except Exception as e:
                logger.error("Exception: {0}".format(traceback.format_exc()))
                self.scheduleThreadPixmap.setPixmap(self.needsAttentionPixmap)
        else:
            logger.info("Schedule disabled. Running in manual control mode.")
            self.scheduleThreadPixmap.setPixmap(self.nonePixmap)

    def nodeEditor(self):
        comps = self.thisNode.capabilities.split(" ")
        defaults = {"host" : self.thisNode.host,
                    "priority" : self.thisNode.minPriority,
                    "comps" : comps,
                    "scheduleEnabled" : int(self.thisNode.scheduleEnabled),
                    "weekSchedule" : self.thisNode.weekSchedule}
        edits = NodeEditorDialog.create(defaults)
        #logger.debug(edits)
        if edits:
            if edits["schedEnabled"]:
                schedEnabled = 1
            else:
                schedEnabled = 0
            query = "UPDATE hydra_rendernode SET minPriority = %s"
            query += ", scheduleEnabled = %s, capabilities = %s"
            query += " WHERE host = %s"
            editsTuple = (edits["priority"], schedEnabled, edits["comps"], self.thisNode.host)
            with transaction() as t:
                t.cur.execute(query, editsTuple)
            self.updateThisNodeInfo()
            return True
        else:
            return False

    def updateThisNodeInfo(self):
        self.thisNode = hydra_rendernode.fetch("WHERE host = %s", (self.thisNode.host,))

        #Check for changes in schedule
        if self.thisNode.weekSchedule != self.currentSchedule or self.thisNode.scheduleEnabled != self.currentScheduleEnabled:
            self.currentSchedule = self.thisNode.weekSchedule
            self.currentScheduleEnabled = self.thisNode.scheduleEnabled
            if self.schedThreadStatus:
                self.schedThread.terminate()
                app.processEvents()
            self.startScheduleThread()

        self.nodeNameLabel.setText(self.thisNode.host)
        self.nodeStatusLabel.setText(niceNames[self.thisNode.status])
        if self.thisNode.task_id:
            taskText = str(self.thisNode.task_id)
        else:
            taskText = "None"
        self.taskIDLabel.setText(taskText)
        self.nodeVersionLabel.setText(str(self.thisNode.software_version))
        self.minPriorityLabel.setText(str(self.thisNode.minPriority))
        self.capabilitiesLabel.setText(self.thisNode.capabilities)
        self.scheduleEnabled.setText(str(self.thisNode.scheduleEnabled))
        self.pulseLabel.setText(str(self.thisNode.pulse))

        if self.trayIconBool:
            niceStatus = niceNames[self.thisNode.status]
            iconStatus = "Hydra RenderNodeMain\nNode: {0}\nStatus: {1}\nTask: {2}"
            self.trayIcon.setToolTip(iconStatus.format(self.thisNode.host,
                                                    niceStatus,
                                                    taskText))

    def aboutBoxHidden(self, title="", msg=""):
        """Creates a window that has been minimzied to the tray"""
        if self.isVisable:
            aboutBox(self, title, msg)
        else:
            self.trayIcon.showMessage(title, msg)

    def schedulerMain(self):
        if not self.thisNode:
            self.scheduleThreadPixmap.setPixmap(self.needsAttentionPixmap)
            logger.error("Node OBJ not found by schedulerMain! Checking again in 24 hours.")
            #Sleep for 24 hours
            return 86400

        self.updateThisNodeInfo()

        sleepTime, nowStatus = NodeUtils.calcuateSleepTimeFromNode(self.thisNode.host)
        if not sleepTime or not nowStatus:
            logger.error("Could not find schdule! Checking again in 24 hours.")
            return 86400

        if nowStatus == READY:
            self.startupEvent()
        else:
            self.shutdownEvent()

        #Add an extra minute just in case
        return sleepTime + 60

    def startupEvent(self):
        logger.info("Triggering Startup Event")
        self.onlineThisNodeHandler()

    def shutdownEvent(self):
        logger.info("Triggering Shutdown Event")
        self.offlineThisNodeHandler()

class schedulerThread(threading.Thread):
    """Modified version of the stoppableThread"""
    def __init__(self, target):
        self.threadName = "Scheduler_Thread"
        self.stopEvent = threading.Event()
        self.target = target
        threading.Thread.__init__(self, target = self.tgt)

    def tgt(self):
        while not self.stopEvent.is_set():
            #target = schedulerMain from the RenderNodeMainUI class
            self.interval = self.target()
            hours = int(self.interval / 60 / 60)
            minutes = int(self.interval / 60 % 60)
            logger.info("Scheduler Sleeping for {0} hours and {1} minutes".format(hours, minutes))
            self.stopEvent.wait(self.interval)

    def terminate(self):
        logger.info("Killing {0}...".format(self.threadName))
        self.stopEvent.set()

def pulse():
    host = Utils.myHostName()
    with transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() "
                    "WHERE host = '{0}'".format(host))

if __name__ == "__main__":
    logger.info('Starting in {0}'.format(os.getcwd()))
    logger.info('arglist is {0}'.format(sys.argv))

    app = QApplication(sys.argv)
    app.quitOnLastWindowClosed = False

    lockFile = InstanceLock("HydraRenderNode")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: {}".format(lockStatus))
    if not lockStatus:
        logger.critical("Only one RenderNode is allowed to run at a time! Exiting...")
        aboutBox(None, "ERROR", "Only one RenderNode is allowed to run at a time! Exiting...")
        sys.exit(-1)

    window = RenderNodeMainUI()
    retcode = app.exec_()
    lockFile.remove()
    sys.exit(retcode)
