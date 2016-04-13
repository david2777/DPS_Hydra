#Standard
import sys
import os
import logging
import traceback
import functools
import threading
import datetime
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
            aboutBox(self, "Error!", "More than one RenderNode found!"
                    "You cannot run more than one RenderNode at the same time")
            sys.exit(1)

        #Add handlers
        emStream = EmittingStream(textWritten=self.normalOutputWritten)
        handler = logging.StreamHandler(emStream)
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
        try:
            self.startupServers()
        except Exception, e:
            logger.error(traceback.format_exc(e))
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
                    "Could not create tray icon. Minimizing to tray has been"
                    " disabled.")
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
            #Force update UI
            app.processEvents()
            if self.schedThreadStatus:
                self.schedThread.terminate()
            app.processEvents()
            if self.pulseThreadStatus:
                self.pulseThread.terminate()
            self.updateThisNodeInfo()
            app.processEvents()
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
                    killed = TaskUtils.killTask(task_id, "R")
                    if not killed:
                        logger.error("Node could not kill for some reason!")
                        self.aboutBoxHidden("Error",
                                    "Task couldn't be killed for some reason.")
                    else:
                        logger.info("Node Got Off current task!")
                except socketerror as err:
                    logger.error(str(err))
                    self.aboutBoxHidden("Error", "Task couldn't be killed "
                    "because there was a problem communicating with the "
                    "host running it.")
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
        self.renderServerStatus = False
        self.schedThreadStatus = False
        if self.thisNode:
            self.pulseThread = stoppableThread(pulse, 60, "Pulse")
            try:
                self.pulseThread.start()
                self.pulseThreadStatus = True
                self.pulseThreadPixmap.setPixmap(self.donePixmap)
                logger.info("Pulse Thread started!")
            except Exception, e:
                logger.error("Exception: {0}".format(traceback.format_exc()))
                self.pulseThreadPixmap.setPixmap(self.needsAttentionPixmap)

            #Start Render Server
            try:
                self.renderServer = RenderNode.RenderTCPServer()
                self.renderServer.createIdleLoop(5,
                                                self.renderServer.processRenderTasks)
                self.renderServerStatus = True
                self.renderServerPixmap.setPixmap(self.donePixmap)
                logger.info("Render Server Started!")
            except Exception, e:
                logger.error("Exception: {0}".format(traceback.format_exc()))
                self.renderServerPixmap.setPixmap(self.needsAttentionPixmap)

            #Start Schedule Thread
            try:
                self.schedThread = schedulerThread(900, self.schedulerMain)
                self.schedThread.start()
                self.schedThreadStatus = True
                self.scheduleThreadPixmap.setPixmap(self.donePixmap)
                logger.info("Schedule Thread started!")
            except Exception, e:
                logger.error("Exception: {0}".format(traceback.format_exc()))
                self.scheduleThreadPixmap.setPixmap(self.needsAttentionPixmap)

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
            niceStatus = niceNames[self.thisNode.status]
            self.nodeStatusLabel.setText(niceStatus)
            vText = getSoftwareVersionText(self.thisNode.software_version)
            self.nodeVersionLabel.setText(vText)
            self.minPriorityLabel.setText(str(self.thisNode.minPriority))
            self.capabilitiesLabel.setText(str(self.thisNode.capabilities))

            if self.trayIconBool:
                iconStatus = "Hydra RenderNodeMain\nNode: {0}\nStatus: {1}\nTask: {2}"
                self.trayIcon.setToolTip(iconStatus.format(self.thisNode.host,
                                                        niceStatus,
                                                        taskText))

        else:
            aboutBox(self, "Notice",
                "Information about this node cannot be displayed because it is "
                "not registered on the render farm. You may continue to use"
                " Farm View, but it must be restarted after this node is "
                "registered if you wish to see this node's information.")

    def aboutBoxHidden(self, title="", msg=""):
        """Creates a window that has been minimzied to the tray"""
        QMessageBox.about(self, title, msg)
        #Work around...
        if not self.isVisable():
            self.show()
            self.hide()

    def schedulerMain(self):
        #Do the stuff
        if not self.thisNode:
            return

        self.updateThisNodeInfo()

        if self.thisNode.onlineTime == None or self.thisNode.offlineTime == None:
            return

        now = datetime.datetime.now().replace(microsecond = 0, second = 0)
        nowTime = now.time()
        nowDate = now.date()

        sTimeData = self.thisNode.onlineTime.split(":")
        sTimeData = [int(t) for t in sTimeData]
        startTime = datetime.time(sTimeData[0], sTimeData[1], sTimeData[2])

        eTimeData = self.thisNode.offlineTime.split(":")
        eTimeData = [int(t) for t in eTimeData]
        endTime = datetime.time(eTimeData[0], eTimeData[1], eTimeData[2])

        startDT = datetime.datetime.combine(nowDate, startTime)
        endDT = datetime.datetime.combine(nowDate, endTime)

        holidays = [] #TODO:Get the actual holidays lol

        logger.info("Current time: {0}".format(str(now)))

        if self.thisNode.status == "O" or self.thisNode.status == "P":
            endDT = endDT + datetime.timedelta(days = 1)
            if nowDate in holidays:
                logger.info("Today is a holiday!")
                sleepyTime = (endDT - now).total_seconds()
                self.startupEvent()
            elif nowDate.isoweekday() == 6:
                logger.info("Today is Saturday!")
                endDT = endDT + datetime.timedelta(days = 1)
                sleepyTime = (endDT - now).total_seconds()
                self.startupEvent()
            elif nowDate.isoweekday() == 7:
                logger.info("Today is Sunday!")
                sleepyTime = (endDT - now).total_seconds()
                self.startupEvent()
            else:
                logger.info("Regular Startup")
                sleepyTime = (endDT - now).total_seconds()
                self.startupEvent()

        else:
            if nowDate in holidays:
                logger.info("Today is a holiday!")
                sleepyTime = (endDT - now).total_seconds()
            elif nowDate.isoweekday() == 6:
                logger.info("Today is Saturday!")
                endDT = endDT + datetime.timedelta(days = 1)
                sleepyTime = (endDT - now).total_seconds()
            elif nowDate.isoweekday() == 7:
                logger.info("Today is Sunday!")
                sleepyTime = (endDT - now).total_seconds()
            else:
                logger.info("Regular Shutdown")
                sleepyTime = (now - startDT).total_seconds()
                self.shutdownEvent()

        if sleepyTime < 59:
            logger.error("Bad sleep time!")
            return 600
        else:
            return int(sleepyTime)

    def startupEvent(self):
        logger.info("Triggering Startup Event")
        self.onlineThisNodeHandler()
        return True

    def shutdownEvent(self):
        logger.info("Triggering Shutdown Event")
        self.offlineThisNodeHandler()
        return True

class stoppableThread(threading.Thread):
    def __init__(self, targetFunction, interval, tName):
        self.targetFunction = targetFunction
        self.interval = interval
        self.tName = tName
        self._flag = False
        self.stop = threading.Event()
        threading.Thread.__init__(self, target = self.tgt)

    def tgt(self):
        try:
            while (not self.stop.wait(1)):
                self._flag = True
                self.targetFunction()
                self.stop.wait(self.interval)
        finally:
            self._flag = False

    def terminate(self):
        logger.info("Killing {0} Thread...".format(self.tName))
        self.stop.set()

class schedulerThread(threading.Thread):
    def __init__(self, interval, target):
        self.interval = interval
        self._flag = False
        self.tName = "Scheduler Thread"
        self.stop = threading.Event()
        self.target = target
        threading.Thread.__init__(self, target = self.tgt)

    def tgt(self):
        try:
            self.interval = self.target()
            while (not self.stop.wait(1)):
                self._flag = True
                self.interval = self.target()
                hours = int(self.interval/ 60 / 60 )
                minutes = int(self.interval/ 60 % 60)
                logger.info("Scheduler Sleeping for {0} hours and {1} minutes".format(hours, minutes))
                self.stop.wait(self.interval)
        finally:
            self._flag = False

    def terminate(self):
        logger.info("Killing {0}...".format(self.tName))
        self.stop.set()



def pulse():
    host = Utils.myHostName()
    try:
        with transaction() as t:
            t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() "
                        "WHERE host = '{0}'".format(host))
    except Exception, e:
        logger.error(traceback.format_exc(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.quitOnLastWindowClosed = False
    window = RenderNodeMainUI()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
