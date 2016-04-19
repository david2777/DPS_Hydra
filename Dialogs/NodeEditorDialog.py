"""Update Me!"""
#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime

#Hydra
from CompiledUI.UI_NodeEditor import Ui_nodeEditorDialog
from Setups.MySQLSetup import db_username, hydra_capabilities, hydra_executable

class NodeEditorDialog(QDialog, Ui_nodeEditorDialog):
    def __init__(self, defaults, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        #Connect Buttons
        QObject.connect(self.cancelButton, SIGNAL("clicked()"),
                        self.cancelButtonHandler)
        QObject.connect(self.okButton, SIGNAL("clicked()"),
                        self.okButtonHandler)
        QObject.connect(self.schedCheckBox, SIGNAL("stateChanged(int)"),
                        self.schedCheckBoxHandler)

        #Set globals
        self.save = False

        self.populateComps()

        if defaults:
            title = "Editing {0}:".format(defaults["node"])
            self.editorGroup.setTitle(title)
            self.minPrioritySpinbox.setValue(defaults["priority"])
            if defaults["startTime"]:
                self.schedEnabled = True
                self.onlineTimeEdit.setTime(defaults["startTime"])
                self.offlineTimeEdit.setTime(defaults["endTime"])
            else:
                #NOTE: This will be changed by the setCheckState call to
                #       schedCheckBoxHandler
                self.schedEnabled = True
                self.schedCheckBox.setCheckState(0)

            cbxList = defaults["comps"]
            for cbx in self.compChecks:
                if cbx.text() in cbxList:
                    cbx.setCheckState(2)

    def populateComps(self):
        #Get requirements master list from the DB
        compatabilities = hydra_capabilities.fetch()
        compatabilities = [comp.name for comp in compatabilities]
        self.compChecks = []
        col = 0
        row = 0
        for item in compatabilities:
            c = QCheckBox(item)
            self.compGrid.addWidget(c, row, col)
            if col == 2:
                row += 1
                col = 0
            else:
                col += 1

            self.compChecks.append(c)

    def getComps(self):
        compList = []
        for check in self.compChecks:
            if check.isChecked():
                compList.append(str(check.text()))
        return sorted(compList)

    def getValues(self):
        if self.schedEnabled:
            startTime = str(self.onlineTimeEdit.time().toString())
            endTime = str(self.offlineTimeEdit.time().toString())
        else:
            startTime = None
            endTime = None
        comps = " ".join(self.getComps())
        rDict = {"priority" : int(self.minPrioritySpinbox.value()),
                "startTime" : startTime,
                "endTime" : endTime,
                "comps" : comps}
        return rDict

    def schedCheckBoxHandler(self):
        if self.schedEnabled:
            self.schedEnabled = False
            self.onlineTimeEdit.setEnabled(False)
            self.offlineTimeEdit.setEnabled(False)
        elif not self.schedEnabled:
            self.schedEnabled = True
            self.onlineTimeEdit.setEnabled(True)
            self.offlineTimeEdit.setEnabled(True)

    def cancelButtonHandler(self):
        self.close()

    def okButtonHandler(self):
        self.save = True
        self.close()

    @classmethod
    def create(cls, defaults):
        dialog = NodeEditorDialog(defaults)
        dialog.exec_()
        if dialog.save:
            return dialog.getValues()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NodeEditorDialog(None, None)
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
