#Standard
import sys
import os

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
import NodeUtils


class RenderNodeMainUI(QMainWindow, Ui_RenderNodeMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.buildUI()
        self.connectButtons()
        self.updateThisNodeInfo()
        
    def buildUI(self):
        self.icon=QSystemTrayIcon()
        self.iconBool = self.icon.isSystemTrayAvailable()
        if self.iconBool:
            self.icon.setIcon(QIcon('images/RIcon.png'))
            self.icon.show()
            self.icon.setVisible(True)
            self.setWindowIcon(QIcon('images/RIcon.png'))          
            self.icon.activated.connect(self.activate)
            
    def connectButtons(self):
        QObject.connect(self.trayButton, SIGNAL("clicked()"),
                        self.sendToTrayHandler)
        if not self.iconBool:
            self.trayButton.setEnabled(False)
            
    def closeEvent(self, event):
        choice = yesNoBox(self, "Confirm", "Really exit the RenderNodeMain server?")
        if choice == QMessageBox.Yes:
            self.icon.hide()
            event.accept()
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
        
    def updateTaskIDLabel(self, task_id):
        if task_id:
            self.taskIDLabel.setText(str(task_id))
        else:
            self.taskIDLabel.setText("None")
            
    def updateMinPriorityLabel(self, minPriority):
        self.minPriorityLabel.setText(str(minPriority))

    def updateCapabilitiesLabel(self, capabilities):
        self.capabilitiesLabel.setText(capabilities)
        
    def updateThisNodeInfo(self):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        #Get the most current info from the database
        thisNode = None
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()

        if thisNode:
            #Update the labels
            self.nodeNameLabel.setText(thisNode.host)
            self.nodeStatusLabel.setText(niceNames[thisNode.status])
            self.updateTaskIDLabel(thisNode.task_id)
            self.nodeVersionLabel.setText(getSoftwareVersionText(thisNode.software_version))
            self.updateMinPriorityLabel(thisNode.minPriority)
            self.updateCapabilitiesLabel(thisNode.capabilities)

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
