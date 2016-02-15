#Standard
import sys
import os
import logging
import traceback
import functools
from multiprocessing import Process

#Third Party
from MySQLdb import Error as sqlerror

#Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from UI_RenderNodeMain import Ui_RenderNodeMainWindow
from MessageBoxes import aboutBox, yesNoBox

#Hydra
from MySQLSetup import *
from LoggingSetup import logger
from FarmView import getSoftwareVersionText
import RenderNode
import NodeUtils

class NoSQLFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().startswith('SELECT * FROM')

#logger.addFilter(NoSQLFilter())

class RenderNodeMainUI(QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        logger.info('Starting in {0}'.format(os.getcwd()))
        logger.info('arglist {0}'.format(sys.argv))
        #Get Pixmaps and Icon
        self.donePixmap = QPixmap("images/status/done.png")
        self.inProgPixmap = QPixmap("images/status/inProgress.png")
        self.needsAttentionPixmap = QPixmap("images/status/needsAttention.png")
        self.nonePixmap = QPixmap("images/status/none.png")
        self.notStartedPixmap = QPixmap("images/status/notStarted.png")
        self.RIcon = QIcon('images/RIcon.png')

        self.thisNode = None
        try:
            self.thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()

        self.buildUI()
        self.connectButtons()
        self.updateThisNodeInfo()
        self.startupServers()


    def buildUI(self):
        self.renderServerPixmap.setPixmap(self.notStartedPixmap)
        self.scheduleThreadPixmap.setPixmap(self.nonePixmap)
        self.pulseThreadPixmap.setPixmap(self.notStartedPixmap)
        self.setWindowIcon(self.RIcon)

        #Setup tray icon
        self.icon=QSystemTrayIcon()
        self.iconBool = self.icon.isSystemTrayAvailable()
        if self.iconBool:
            self.icon.setIcon(self.RIcon)
            self.icon.show()
            self.icon.setVisible(True)
            self.icon.activated.connect(self.activate)
        else:
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
                        self.getoffThisNodeHandler)
        if not self.iconBool:
            self.trayButton.setEnabled(False)

    def closeEvent(self, event):
        choice = yesNoBox(self, "Confirm", "Really exit the RenderNodeMain server?")
        if choice == QMessageBox.Yes:
            logger.info("Shutting down...")
            if self.pulseProcStatus:
                self.pulseProc.terminate()
            if self.renderServerStatus:
                self.renderServer.shutdownCMD()
            self.icon.hide()
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

    def activate(self, reason):
        if reason==2:
            self.show()

    def __icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def sendToTrayHandler(self):
        self.icon.show()
        self.hide()

    def onlineThisNodeHandler(self):
        if self.thisNode:
            try:
                NodeUtils.onlineNode(self.thisNode)
                self.updateThisNodeInfo()
            except sqlerror as err:
                logger.error(str(err))
                self.sqlErrorBox()

    def offlineThisNodeHandler(self):
       if self.thisNode:
           try:
               NodeUtils.offlineNode(self.thisNode)
               self.updateThisNodeInfo()
           except sqlerror as err:
               logger.error(str(err))
               self.sqlErrorBox()

    def getoffThisNodeHandler(self):
        aboutBox(self, "Oops", "Not Implemeted")

    def startupServers(self):
        #Startup Pulse thread
        self.pulseProcStatus = False
        """
        self.pulseProc = Process(target = RenderNode.heartbeat,
                                        name = "heartbeat",
                                        args = (60,))
        try:
            self.pulseProc.start()
            self.pulseProc.join()
            self.pulseProcStatus = True
            self.pulseThreadPixmap.setPixmap(self.donePixmap)
            logger.info("Pulse proc started")
        except Exception, e:
            logger.error("Exception caught in RenderNodeMain: {0}".format(traceback.format_exc()))
            self.pulseThreadPixmap.setPixmap(self.needsAttentionPixmap)
        """


        #Start Render Server
        self.renderServerStatus = False
        try:
            self.renderServer = RenderNode.RenderTCPServer()
            self.renderServer.createIdleLoop(5, self.renderServer.processRenderTasks)
            self.renderServerStatus = True
            self.renderServerPixmap.setPixmap(self.donePixmap)
        except Exception, e:
            logger.error("Exception caught in RenderNodeMain: {0}".format(traceback.format_exc()))
            self.renderServerPixmap.setPixmap(self.needsAttentionPixmap)

    def updateThisNodeInfo(self):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        #Get the most current info from the database
        if self.thisNode:
            #Update the labels
            if self.thisNode.task_id:
                self.taskIDLabel.setText(str(self.thisNode.task_id))
            else:
                self.taskIDLabel.setText("None")
            self.nodeNameLabel.setText(self.thisNode.host)
            self.nodeStatusLabel.setText(niceNames[self.thisNode.status])
            self.nodeVersionLabel.setText(getSoftwareVersionText(self.thisNode.software_version))
            self.minPriorityLabel.setText(str(self.thisNode.minPriority))
            self.capabilitiesLabel.setText(str(self.thisNode.capabilities))

        else:
            aboutBox(self, "Notice",
                "Information about this node cannot be displayed because it is "
                "not registered on the render farm. You may continue to use"
                " Farm View, but it must be restarted after this node is "
                "registered if you wish to see this node's information.")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RenderNodeMainUI()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
