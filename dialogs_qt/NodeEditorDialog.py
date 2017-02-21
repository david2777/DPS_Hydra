"""Update Me!"""
#Standard
import sys

#Third Party
from PyQt4 import QtGui

#Hydra Qt
from compiled_qt.UI_NodeEditor import Ui_nodeEditorDialog
from dialogs_qt.NodeSchedulerDialog import NodeSchedulerDialog

#Hydra
import hydra.hydra_sql as sql

class NodeEditorDialog(QtGui.QDialog, Ui_nodeEditorDialog):
    def __init__(self, defaults, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.schedEnabled = False

        #Connect Buttons
        self.cancelButton.clicked.connect(self.cancelButtonHandler)
        self.okButton.clicked.connect(self.okButtonHandler)
        self.schedulerEditButton.clicked.connect(self.schedulerEditButtonHandler)
        self.schedCheckBox.stateChanged.connect(self.schedCheckBoxHandler)

        #Set globals
        self.save = False

        self.populateComps()

        self.defaults = defaults
        if defaults:
            title = "Editing {0}:".format(defaults["host"])
            self.editorGroup.setTitle(title)
            self.minPrioritySpinbox.setValue(defaults["priority"])
            if defaults["schedule_enabled"] == 1:
                self.schedCheckBox.setCheckState(2)


            cbxList = defaults["comps"]
            for cbx in self.compChecks:
                if cbx.text() in cbxList:
                    cbx.setCheckState(2)

    def populateComps(self):
        #Get requirements master list from the DB
        compatabilities = sql.hydra_capabilities.fetch()
        compatabilities = [comp.name for comp in compatabilities]
        self.compChecks = []
        col = 0
        row = 0
        for item in compatabilities:
            c = QtGui.QCheckBox(item)
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
        comps = " ".join(self.getComps())
        rDict = {"priority" : int(self.minPrioritySpinbox.value()),
                "schedule_enabled" : self.schedEnabled,
                "comps" : comps}
        return rDict

    def schedulerEditButtonHandler(self):
        edits = NodeSchedulerDialog.create(self.defaults)
        if edits is None:
            return

        #An empty list will return boolean False
        if edits:
            editsFormat = ",".join(edits)
            if editsFormat != self.defaults["week_schedule"]:
                self.defaults["week_schedule"] = editsFormat
                with sql.transaction() as t:
                    cmd = "UPDATE hydra_rendernode SET week_schedule = %s WHERE host = %s"
                    t.cur.execute(cmd, (editsFormat, self.defaults["host"]))
        else:
            with sql.transaction() as t:
                cmd = "UPDATE hydra_rendernode SET week_schedule = %s, schedule_enabled = 0 WHERE host = %s"
                t.cur.execute(cmd, (None, self.defaults["host"]))
            self.schedCheckBox.setCheckState(0)

    def schedCheckBoxHandler(self):
        if self.schedEnabled:
            self.schedEnabled = False
            self.schedulerEditButton.setEnabled(False)
        elif not self.schedEnabled:
            self.schedEnabled = True
            self.schedulerEditButton.setEnabled(True)

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
    app = QtGui.QApplication(sys.argv)

    window = NodeEditorDialog(None, None)
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
