#Standard
import sys
import os
import logging

#Third Party
from PyQt4 import QtGui, QtCore

#Hydra Qt
from compiled_qt.UI_RenderNodeMain import Ui_RenderNodeMainWindow
from dialogs_qt.NodeEditorDialog import NodeEditorDialog
from dialogs_qt.MessageBoxes import about_box, yes_no_box

#Hydra
import RenderNode
import hydra.hydra_sql as sql
from hydra import threads
from hydra.long_strings import RenderNodeError_String
from hydra.logging_setup import logger, outputWindowFormatter
from hydra.single_instance import InstanceLock
import hydra.node_scheduling as node_scheduling
import hydra.hydra_utils as hydra_utils

#Doesn't like Qt classes
#pylint: disable=E0602,E1101

class EmittingStream(QtCore.QObject):
    """For writing text to the console output"""
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class RenderNodeMainUI(QtGui.QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)

        with open(hydra_utils.find_resource("assets/styleSheet.css"), "r") as myStyles:
            self.setStyleSheet(myStyles.read())

        self.thisNode = sql.get_this_node()
        self.isVisable = True

        self.pulseThreadStatus = False
        self.renderServerStatus = False
        self.schedThreadStatus = False
        self.autoUpdateStatus = False

        if not self.thisNode or not bool(self.thisNode.is_render_node):
            logger.error("Node Error!")
            about_box(self, "Error", RenderNodeError_String)
            sys.exit(1)

        self.currentSchedule = self.thisNode.week_schedule
        self.currentScheduleEnabled = self.thisNode.schedule_enabled

        self.build_ui()
        self.connect_buttons()
        self.update_thisnode()
        self.startup_servers()

        logger.info("Render Node Main is live! Waiting for tasks...")

        try:
            autoHide = True if str(sys.argv[1]).lower() == "true" else False
        except IndexError:
            autoHide = False

        if autoHide and self.trayIconBool:
            logger.info("Autohide is enabled!")
            self.hide_window()
        else:
            self.show()

    def write_to_window_logger(self, text):
        """Append text to the QTextEdit."""
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()

    def clear_window_logger(self):
        choice = yes_no_box(self, "Confirm", "Really clear output?")
        if choice == QtGui.QMessageBox.Yes:
            self.outputTextEdit.clear()
            logger.info("Output cleared")

    def build_ui(self):
        def addItem(name, handler, statusTip, menu):
            action = QtGui.QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            menu.addAction(action)

        #Add Logging handlers for output field
        emStream = EmittingStream(textWritten=self.write_to_window_logger)
        handler = logging.StreamHandler(emStream)
        handler.setLevel(logging.INFO)
        handler.setFormatter(outputWindowFormatter)
        logger.addHandler(handler)

        sys.stdout = EmittingStream(textWritten=self.write_to_window_logger)
        sys.stderr = EmittingStream(textWritten=self.write_to_window_logger)

        #Get Pixmaps and Icon
        self.donePixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/status/done.png"))
        self.inProgPixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/status/inProgress.png"))
        self.needsAttentionPixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/status/needsAttention.png"))
        self.nonePixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/status/none.png"))
        self.notStartedPixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/status/notStarted.png"))
        self.refreshPixmap = QtGui.QPixmap(hydra_utils.find_resource("assets/refresh.png"))
        self.refreshIcon = QtGui.QIcon()
        self.refreshIcon.addPixmap(self.refreshPixmap)
        self.RIcon = QtGui.QIcon(hydra_utils.find_resource("assets/RenderNodeMain.png"))

        self.isVisable = True

        self.refreshButton.setIcon(self.refreshIcon)

        self.renderServerPixmap.setPixmap(self.notStartedPixmap)
        self.scheduleThreadPixmap.setPixmap(self.notStartedPixmap)
        self.pulseThreadPixmap.setPixmap(self.notStartedPixmap)
        self.setWindowIcon(self.RIcon)

        #Setup tray icon
        self.trayIcon = QtGui.QSystemTrayIcon()
        self.trayIconBool = self.trayIcon.isSystemTrayAvailable()
        if self.trayIconBool:
            self.trayIcon.setIcon(self.RIcon)
            self.trayIcon.show()
            self.trayIcon.setVisible(True)
            self.trayIcon.activated.connect(self.activate)
            self.trayIcon.messageClicked.connect(self.activate)

            #Tray Icon Context Menu
            self.taskIconMenu = QtGui.QMenu(self)

            addItem("Open", self.show_window,
                    "Show the RenderNodeMain Window", self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Update", self.update_thisnode,
                    "Fetch the latest information from the Database", self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Online", self.online_thisnode,
                    "Online this node", self.taskIconMenu)
            addItem("Offline", self.offline_thisnode,
                    "Offline this node", self.taskIconMenu)
            addItem("GetOff!", self.get_off_thisnode,
                    "Kill the current task and offline this node", self.taskIconMenu)

            self.trayIcon.setContextMenu(self.taskIconMenu)
        else:
            logger.error("Tray Icon Error! Could not create tray icon.")
            about_box(self, "Tray Icon Error",
                    "Could not create tray icon. Minimizing to tray has been disabled.")
            self.trayButton.setEnabled(False)

    def connect_buttons(self):
        self.trayButton.clicked.connect(self.hide_window)
        self.onlineButton.clicked.connect(self.online_thisnode)
        self.offlineButton.clicked.connect(self.offline_thisnode)
        self.getoffButton.clicked.connect(self.get_off_thisnode)
        self.clearButton.clicked.connect(self.clear_window_logger)
        self.refreshButton.clicked.connect(self.update_thisnode)
        self.editThisNodeButton.clicked.connect(self.open_node_editor)
        self.autoUpdateCheckBox.stateChanged.connect(self.auto_update_handler)
        if not self.trayIconBool:
            self.trayButton.setEnabled(False)

    #DO NOT RENAME THIS FUNCTION
    def closeEvent(self, event):
        choice = yes_no_box(self, "Confirm", "Really exit the RenderNodeMain server?")
        if choice == QtGui.QMessageBox.Yes:
            self.exit()
        else:
            event.ignore()

    def exit(self):
        self.shutdown()
        self.trayIcon.hide()
        event.accept()
        sys.exit(0)

    def shutdown(self):
        logger.info("Shutting down...")
        if self.schedThreadStatus:
            self.schedThread.terminate()
        if self.autoUpdateStatus:
            self.autoUpdateThread.terminate()
        if self.renderServerStatus:
            self.renderServer.shutdown()
        logger.debug("All servers Shutdown")

    def reboot(self):
        #TODO: Make a timeout box so the user can stop a reboot
        logger.info("Rebooting Node...")
        self.shutdown()
        self.renderServer.reboot()

    def auto_update_handler(self):
        """Toggles Auto Updater
        Note that this is run AFTER the CheckState is changed so when we do
        .isChecked() it's looking for the state after it has been checked."""
        if not self.autoUpdateCheckBox.isChecked():
            self.autoUpdateStatus = False
            self.autoUpdateThread.terminate()
        else:
            self.autoUpdateStatus = True
            self.autoUpdateThread.restart()

    def show_window(self):
        self.isVisable = True
        self.show()
        self.update_thisnode()

    def hide_window(self):
        self.isVisable = False
        self.trayIcon.show()
        self.hide()

    def activate(self, reason):
        if reason == 2:
            self.show_window()

    def __icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_window()

    def online_thisnode(self):
        response = self.thisNode.online()
        self.update_thisnode()
        if response:
            logger.info("Node Onlined")
        else:
            logger.error("Node could not be Onlined!")

    def offline_thisnode(self):
        response = self.thisNode.offline()
        self.update_thisnode()
        if response:
            logger.info("Node Offlined")
        else:
            logger.error("Node could not be Offlined!")

    def get_off_thisnode(self):
        response = self.thisNode.get_off()
        self.update_thisnode()
        if response:
            logger.info("Node Offlined and Task Killed")
        else:
            logger.error("Node could not be Onlined or the Task could not be killed!")

    def startup_servers(self):
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
        QtCore.SIGNAL("update_thisnode")
        QtCore.QObject.connect(self, QtCore.SIGNAL("update_thisnode"), self.update_thisnode)
        self.autoUpdateStatus = True

        self.autoUpdateThread = threads.stoppableThread(self.update_thisnode_signaler, 10,
                                                "AutoUpdate_Thread")
        self.start_schedule_thread()

    def start_schedule_thread(self):
        """This is in it's own function because it starts and stops often"""
        #pylint: disable=W0703,W0201
        if bool(self.currentScheduleEnabled) and self.currentSchedule:
            self.schedThread = schedulerThread(self.scheduler_main,
                                                "Schedule_Thread", None)
            self.schedThreadStatus = True
            self.scheduleThreadPixmap.setPixmap(self.donePixmap)
            logger.info("Schedule Thread started!")
        else:
            logger.info("Schedule disabled. Running in manual control mode.")
            self.scheduleThreadPixmap.setPixmap(self.nonePixmap)

    def open_node_editor(self):
        response = self.node_editor()
        if response:
            logger.info("Updating this node...")
            logger.info("Node updated!")
        else:
            logger.info("No changes detected. Nothing was changed.")

    def node_editor(self):
        comps = self.thisNode.capabilities.split(" ")
        defaults = {"host" : self.thisNode.host,
                    "priority" : self.thisNode.minPriority,
                    "comps" : comps,
                    "schedule_enabled" : int(self.thisNode.schedule_enabled),
                    "week_schedule" : self.thisNode.week_schedule}
        edits = NodeEditorDialog.create(defaults)
        #logger.debug(edits)
        if edits:
            if edits["schedule_enabled"]:
                schedEnabled = 1
            else:
                schedEnabled = 0
            query = "UPDATE hydra_rendernode SET minPriority = %s"
            query += ", schedule_enabled = %s, capabilities = %s"
            query += " WHERE host = %s"
            editsTuple = (edits["priority"], schedEnabled, edits["comps"], self.thisNode.host)
            with sql.transaction() as t:
                t.cur.execute(query, editsTuple)
            self.update_thisnode()
            return True
        else:
            return False

    def update_thisnode_signaler(self):
        self.emit(QtCore.SIGNAL("update_thisnode"))

    def update_thisnode(self):
        self.thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (self.thisNode.host,))

        #Check for changes in schedule
        if self.thisNode.week_schedule != self.currentSchedule or self.thisNode.schedule_enabled != self.currentScheduleEnabled:
            self.currentSchedule = self.thisNode.week_schedule
            self.currentScheduleEnabled = self.thisNode.schedule_enabled
            if self.schedThreadStatus:
                self.schedThread.terminate()
                app.processEvents()
            self.start_schedule_thread()

        self.nodeNameLabel.setText(self.thisNode.host)
        self.nodeStatusLabel.setText(sql.niceNames[self.thisNode.status])
        taskText = str(self.thisNode.task_id)
        self.taskIDLabel.setText(taskText)
        self.nodeVersionLabel.setText(str(self.thisNode.software_version))
        self.minPriorityLabel.setText(str(self.thisNode.minPriority))
        self.capabilitiesLabel.setText(self.thisNode.capabilities)
        self.scheduleEnabled.setText(str(self.thisNode.schedule_enabled))
        self.pulseLabel.setText(str(self.thisNode.pulse))

        if self.trayIconBool:
            niceStatus = sql.niceNames[self.thisNode.status]
            iconStatus = "Hydra RenderNodeMain\nNode: {0}\nStatus: {1}\nTask: {2}"
            self.trayIcon.setToolTip(iconStatus.format(self.thisNode.host,
                                                    niceStatus,
                                                    taskText))

    def hidden_about_box(self, title="", msg=""):
        """Creates a window that has been minimzied to the tray"""
        if self.isVisable:
            about_box(self, title, msg)
        else:
            self.trayIcon.showMessage(title, msg)

    def scheduler_main(self):
        if not self.thisNode:
            self.scheduleThreadPixmap.setPixmap(self.needsAttentionPixmap)
            logger.error("Node OBJ not found by scheduler_main! Checking again in 24 hours.")
            #Sleep for 24 hours
            return 86400

        self.update_thisnode()

        sleepTime, nowStatus = node_scheduling.calcuate_sleep_time_from_node(self.thisNode.host)
        if not sleepTime or not nowStatus:
            logger.error("Could not find schdule! Checking again in 24 hours.")
            return 86400

        if nowStatus == sql.READY:
            self.startup_event()
        else:
            self.shutdown_event()

        #Add an extra minute just in case
        return sleepTime + 60

    def startup_event(self):
        logger.info("Triggering Startup Event")
        self.online_thisnode()

    def shutdown_event(self):
        logger.info("Triggering Shutdown Event")
        self.offline_thisnode()

class schedulerThread(threads.stoppableThread):
    """Modified version of the stoppableThread"""
    def tgt(self):
        while not self.stopEvent.is_set():
            #target = scheduler_main from the RenderNodeMainUI class
            self.interval = self.targetFunction()
            hours = int(self.interval / 60 / 60)
            minutes = int(self.interval / 60 % 60)
            logger.info("Scheduler Sleeping for %d hours and %d minutes", hours, minutes)
            self.stopEvent.wait(self.interval)

def pulse():
    host = hydra_utils.my_host_name()
    with sql.transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() "
                    "WHERE host = '{0}'".format(host))

if __name__ == "__main__":
    logger.info("Starting in %s", os.getcwd())
    logger.info("arglist is %s", sys.argv)

    app = QtGui.QApplication(sys.argv)
    app.quitOnLastWindowClosed = False

    lockFile = InstanceLock("HydraRenderNode")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderNode is allowed to run at a time! Exiting...")
        about_box(None, "ERROR", "Only one RenderNode is allowed to run at a time! Exiting...")
        sys.exit(-1)

    window = RenderNodeMainUI()
    retcode = app.exec_()
    lockFile.remove()
    sys.exit(retcode)
