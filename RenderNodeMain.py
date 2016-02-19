#Standard
import sys
import os
import logging
import traceback
import functools
import threading
import time

#Third Party
from MySQLdb import Error as sqlerror

#Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from UI_RenderNodeMain import Ui_RenderNodeMainWindow
from MessageBoxes import aboutBox, yesNoBox, strBox

#Logging
from LoggingSetup import logger, simpleFormatter

if sys.argv[0].split(".")[-1] == "exe":
    logger.removeHandler(logger.handlers[0])
    logger.propagate = False
    logger.debug("Running as exe!")

#Import after logging setup
#Hydra
from MySQLSetup import *
from Constants import BASELOGDIR
from FarmView import getSoftwareVersionText
import RenderNode
import NodeUtils
import TaskUtils

class EmittingStream(QObject):
    """For writing text to the console output"""
    textWritten = pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

class Blackhole(object):
    def write(self,text):
        pass
    def flush(self):
        pass

class RenderNodeMainUI(QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        inst = RenderNode.checkRenderNodeInstances()
        if not inst:
            aboutBox(self, "Error!", "More than one RenderNode found! You cannot run more than one RenderNode at the same time")
            sys.exit(1)

        #Add handlers
        handler = logging.StreamHandler(EmittingStream(textWritten=self.normalOutputWritten))
        handler.setLevel(logging.INFO)
        handler.setFormatter(simpleFormatter)
        logger.addHandler(handler)

        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.normalOutputWritten)

        logger.info('Starting in {0}'.format(os.getcwd()))
        logger.info('arglist is {0}'.format(sys.argv))
        #Get Pixmaps and Icon
        self.donePixmap = QPixmap("images/status/done.png")
        self.inProgPixmap = QPixmap("images/status/inProgress.png")
        self.needsAttentionPixmap = QPixmap("images/status/needsAttention.png")
        self.nonePixmap = QPixmap("images/status/none.png")
        self.notStartedPixmap = QPixmap("images/status/notStarted.png")
        self.refreshPixmap = QPixmap("images/refresh.png")
        self.refreshIcon = QIcon()
        self.refreshIcon.addPixmap(self.refreshPixmap)
        self.RIcon = QIcon('images/RIcon.png')

        self.thisNode = None
        try:
            self.thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.onlineButton.setEnabled(False)
            self.offlineButton.setEnabled(False)
            self.getoffButton.setEnabled(False)
            self.sqlErrorBox()

        self.buildUI()
        self.connectButtons()
        self.updateThisNodeInfo()
        self.startupServers()
        logger.info("LIVE LIVE LIVE")

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
        
        self.isVisable = True    
        
        self.refreshButton.setIcon(self.refreshIcon)

        self.renderServerPixmap.setPixmap(self.notStartedPixmap)
        self.scheduleThreadPixmap.setPixmap(self.nonePixmap)
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

            #Tray Icon Context Menu
            self.taskIconMenu = QMenu(self)
            
            addItem("Open",
                    self.showWindowHandler,
                    "Show the RenderNodeMain Window",
                    self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Update",
                    self.updateThisNodeInfo,
                    "Fetch the latest information from the Database",
                    self.taskIconMenu)
            self.taskIconMenu.addSeparator()
            addItem("Online",
                    self.onlineThisNodeHandler,
                    "Online this node",
                    self.taskIconMenu)
            addItem("Offline",
                    self.offlineThisNodeHandler,
                    "Offline this node",
                    self.taskIconMenu)
            addItem("GetOff!",
                    self.getOffThisNodeHandler,
                    "Kill the current task and offline this node",
                    self.taskIconMenu)
                    
            self.trayIcon.setContextMenu(self.taskIconMenu)
        else:
            logger.error("Tray Icon Error! Could not create tray icon.")
            aboutBox(self,
                    "Tray Icon Error",
                    "Could not create tray icon. Minimizing to tray has been disabled.")
            self.trayButton.setEnabled(False)

    def connectButtons(self):
        QObject.connect(self.trayButton, SIGNAL("clicked()"),
                        self.sendToTrayHandler)
        QObject.connect(self.onlineButton, SIGNAL("clicked()"),
                        self.onlineThisNodeHandler)
        QObject.connect(self.offlineButton, SIGNAL("clicked()"),
                        self.offlineThisNodeHandler)
        QObject.connect(self.getoffButton, SIGNAL("clicked()"),
                        self.getOffThisNodeHandler)
        QObject.connect(self.clearButton, SIGNAL("clicked()"),
                        self.clearOutputHandler)
        QObject.connect(self.runCmdButton, SIGNAL("clicked()"),
                        self.runCommandHandler)
        QObject.connect(self.refreshButton, SIGNAL("clicked()"),
                        self.updateThisNodeInfo)
        if not self.trayIconBool:
            self.trayButton.setEnabled(False)

    def closeEvent(self, event):
        choice = yesNoBox(self, "Confirm", "Really exit the RenderNodeMain server?")
        if choice == QMessageBox.Yes:
            logger.info("Shutting down...")
            logger.info("Please wait, this may take up to 60 seconds...")
            #Force update UI
            app.processEvents()
            if self.pulseThreadStatus:
                #This can take up to 60 seconds, so do it first
                self.pulseThreadVar = False
            self.updateThisNodeInfo()
            isTask = False
            if self.thisNode.task_id:
                isTask = True
                self.getOffThisNodeHandler()
            if self.renderServerStatus:
                self.renderServer.shutdownCMD()
                #Wait to make sure the render server is dead
                time.sleep(5)
            if isTask:
                self.onlineThisNodeHandler()
            self.trayIcon.hide()
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

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
        if self.thisNode:
            try:
                NodeUtils.onlineNode(self.thisNode)
                self.updateThisNodeInfo()
                logger.info("Node Onlined")
            except sqlerror as err:
                logger.error(str(err))
                self.sqlErrorBox()

    def offlineThisNodeHandler(self):
       if self.thisNode:
           try:
               NodeUtils.offlineNode(self.thisNode)
               self.updateThisNodeInfo()
               logger.info("Node Offlined")
           except sqlerror as err:
               logger.error(str(err))
               self.sqlErrorBox()

    def getOffThisNodeHandler(self):
        if self.thisNode:
            self.updateThisNodeInfo()
            task_id = self.thisNode.task_id
            self.offlineThisNodeHandler()
            if task_id:
                try:
                    killed = TaskUtils.killTask(task_id)
                    if not killed:
                        logger.error("Node could not kill for some reason!")
                        self.aboutBoxHidden("Error",
                                    "Task couldn't be killed for some reason.")
                    else:
                        logger.info("Node Got Off current task!")
                except socketerror as err:
                    logger.error(str(err))
                    self.aboutBoxHidden("Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.error(str(err))
                    self.aboutBoxHidden("SQL Error", str(err))
            else:
                self.aboutBoxHidden("Task Kill Error",
                        "No tasks found on current node. Set status to Offline.")

    def runCommandHandler(self):
        reply = strBox(self, "Eval", "Eval this code:")
        if reply[1]:
            command = str(reply[0])
            value = eval(command)
            logger.info(value)

    def clearOutputHandler(self):
        choice = yesNoBox(self, "Confirm", "Really clear output?")
        if choice == QMessageBox.Yes:
            self.outputTextEdit.clear()
            logger.info("Output cleared")

    def startupServers(self):
        #Startup Pulse thread
        self.pulseThreadStatus = False
        self.pulseThreadVar = True
        self.pulseThread = threading.Thread(target = self.pulse,
                                            name = "Pulse Thread",
                                            args = (60,))
        try:
            #self.pulseThread.start()
            self.pulseThreadStatus = True
            self.pulseThreadPixmap.setPixmap(self.donePixmap)
            logger.info("Pulse Thread started!")
        except Exception, e:
            logger.error("Exception caught in RenderNodeMain: {0}".format(traceback.format_exc()))
            self.pulseThreadPixmap.setPixmap(self.needsAttentionPixmap)

        #Start Render Server
        self.renderServerStatus = False
        try:
            self.renderServer = RenderNode.RenderTCPServer()
            self.renderServer.createIdleLoop(5, self.renderServer.processRenderTasks)
            self.renderServerStatus = True
            self.renderServerPixmap.setPixmap(self.donePixmap)
            logger.info("Render Server Started!")
        except Exception, e:
            logger.error("Exception caught in RenderNodeMain: {0}".format(traceback.format_exc()))
            self.renderServerPixmap.setPixmap(self.needsAttentionPixmap)

    def updateThisNodeInfo(self):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        #Update thisNode if it is already set (so we don't error over and over)
        if self.thisNode:
            #Get the most current info from the database
            self.thisNode = NodeUtils.getThisNodeData()
            #Update the labels
            if self.thisNode.task_id:
                taskText = str(self.thisNode.task_id)
            else:
                taskText = "None"
            self.taskIDLabel.setText(taskText)
            self.nodeNameLabel.setText(self.thisNode.host)
            self.nodeStatusLabel.setText(niceNames[self.thisNode.status])
            self.nodeVersionLabel.setText(getSoftwareVersionText(self.thisNode.software_version))
            self.minPriorityLabel.setText(str(self.thisNode.minPriority))
            self.capabilitiesLabel.setText(str(self.thisNode.capabilities))

            if self.trayIconBool:
                iconStatus = "Hydra RenderNodeMain\nNode: {0}\nStatus: {1}\nTask: {2}"
                self.trayIcon.setToolTip(iconStatus.format(self.thisNode.host,
                                                        niceNames[self.thisNode.status],
                                                        taskText))

        else:
            aboutBox(self, "Notice",
                "Information about this node cannot be displayed because it is "
                "not registered on the render farm. You may continue to use"
                " Farm View, but it must be restarted after this node is "
                "registered if you wish to see this node's information.")

    def pulse(self, interval = 5):
        while self.pulseThreadVar:
            try:
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = '{0}'".format(self.thisNode.host))
            except Exception, e:
                logger.error(traceback.format_exc(e))
            time.sleep(interval)
            
    def aboutBoxHidden(self, title="", msg=""):
        """Creates a window that has been minimzied to the tray"""
        QMessageBox.about(self, title, msg)
        #Work around...
        self.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.quitOnLastWindowClosed = False
    window = RenderNodeMainUI()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
