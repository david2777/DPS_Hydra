#Standard
import sys
import os
import logging

#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from compiled_qt.UI_RenderNodeMain import Ui_RenderNodeMainWindow
from dialogs_qt.NodeEditorDialog import NodeEditorDialog
from dialogs_qt.MessageBoxes import aboutBox, yesNoBox

#Hydra
import RenderNode
from hydra.logging_setup import logger, outputWindowFormatter
from hydra.mysql_setup import *
from hydra.threads import *
from hydra.single_instance import InstanceLock
import utils.node_utils as node_utils
import utils.hydra_utils as hydra_utils

#Doesn't like Qt classes
#pylint: disable=E0602,E1101

class EmittingStream(QObject):
    """For writing text to the console output"""
    textWritten = pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class RenderNodeMainUI(QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        with open(hydra_utils.findResource("assets/styleSheet.css"), "r") as myStyles:
            self.setStyleSheet(myStyles.read())

        self.thisNode = node_utils.getThisNodeOBJ()
        self.isVisable = True

        self.pulseThreadStatus = False
        self.renderServerStatus = False
        self.schedThreadStatus = False
        self.autoUpdateStatus = False

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
        self.startupServers()

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
        self.donePixmap = QPixmap(hydra_utils.findResource("assets/status/done.png"))
        self.inProgPixmap = QPixmap(hydra_utils.findResource("assets/status/inProgress.png"))
        self.needsAttentionPixmap = QPixmap(hydra_utils.findResource("assets/status/needsAttention.png"))
        self.nonePixmap = QPixmap(hydra_utils.findResource("assets/status/none.png"))
        self.notStartedPixmap = QPixmap(hydra_utils.findResource("assets/status/notStarted.png"))
        self.refreshPixmap = QPixmap(hydra_utils.findResource("assets/refresh.png"))
        self.refreshIcon = QIcon()
        self.refreshIcon.addPixmap(self.refreshPixmap)
        self.RIcon = QIcon(hydra_utils.findResource("assets/RenderNodeMain.png"))

        self.isVisable = True

        self.refreshButton.setIcon(self.refreshIcon)

        self.renderServerPixmap.setPixmap(self.notStartedPixmap)
        self.scheduleThreadPixmap.setPixmap(self.notStartedPixmap)
        self.pulseThreadPixmap.setPixmap(self.notStartedPixmap)
        self.setWindowIcon(self.RIcon)

        #Setup tray icon
        self.trayIcon = QSystemTrayIcon()
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
            self.shutdown()
        else:
            event.ignore()

    def shutdown(self):
        logger.info("Shutting down...")
        if self.schedThreadStatus:
            self.schedThread.terminate()
        if self.autoUpdateStatus:
            self.autoUpdateThread.terminate()
        if self.renderServerStatus:
            self.renderServer.shutdown()
        logger.debug("All servers Shutdown")
        self.trayIcon.hide()
        event.accept()
        sys.exit(0)

    def autoUpdateHandler(self):
        """Toggles Auto Updater
        Note that this is run AFTER the CheckState is changed so when we do
        .isChecked() it's looking for the state after it has been checked."""
        if not self.autoUpdateCheckBox.isChecked():
            self.autoUpdateStatus = False
            self.autoUpdateThread.terminate()
        else:
            self.autoUpdateStatus = True
            self.autoUpdateThread.restart()

    def showWindowHandler(self):
        self.isVisable = True
        self.show()
        self.updateThisNodeInfo()

    def activate(self, reason):
        if reason == 2:
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
        #Start Render Server
        self.renderServer = RenderNode.RenderTCPServer()
        self.renderServerStatus = True
        self.renderServerPixmap.setPixmap(self.donePixmap)
        logger.info("Render Server Started!")

        #Start Pulse Thread
        self.renderServer.createIdleLoop("Pulse_Thread", pulse, 60)
        self.pulseThreadStatus = True
        self.pulseThreadPixmap.setPixmap(self.donePixmap)
        logger.info("Pulse Thread started!")

        #Start Auto Update Thread
        SIGNAL("updateThisNodeInfo")
        QObject.connect(self, SIGNAL("updateThisNodeInfo"), self.updateThisNodeInfo)
        self.autoUpdateStatus = True

        self.autoUpdateThread = stoppableThread(self.updateThisNodeInfoSignaler, 1,
                                                "AutoUpdate_Thread")
        self.startScheduleThread()

    def startScheduleThread(self):
        """This is in it's own function because it starts and stops often"""
        #pylint: disable=W0703,W0201
        if bool(self.currentScheduleEnabled) and self.currentSchedule:
            self.schedThread = schedulerThread(self.schedulerMain,
                                                "Schedule_Thread", None)
            self.schedThreadStatus = True
            self.scheduleThreadPixmap.setPixmap(self.donePixmap)
            logger.info("Schedule Thread started!")
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

    def updateThisNodeInfoSignaler(self):
        self.emit(SIGNAL("updateThisNodeInfo"))

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

        sleepTime, nowStatus = node_utils.calcuateSleepTimeFromNode(self.thisNode.host)
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

class schedulerThread(stoppableThread):
    """Modified version of the stoppableThread"""
    def tgt(self):
        while not self.stopEvent.is_set():
            #target = schedulerMain from the RenderNodeMainUI class
            self.interval = self.targetFunction()
            hours = int(self.interval / 60 / 60)
            minutes = int(self.interval / 60 % 60)
            logger.info("Scheduler Sleeping for %d hours and %d minutes", hours, minutes)
            self.stopEvent.wait(self.interval)

def pulse():
    host = hydra_utils.myHostName()
    with transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() "
                    "WHERE host = '{0}'".format(host))

if __name__ == "__main__":
    logger.info("Starting in %s", os.getcwd())
    logger.info("arglist is %s", sys.argv)

    app = QApplication(sys.argv)
    app.quitOnLastWindowClosed = False

    lockFile = InstanceLock("HydraRenderNode")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderNode is allowed to run at a time! Exiting...")
        aboutBox(None, "ERROR", "Only one RenderNode is allowed to run at a time! Exiting...")
        sys.exit(-1)

    window = RenderNodeMainUI()
    retcode = app.exec_()
    lockFile.remove()
    sys.exit(retcode)
