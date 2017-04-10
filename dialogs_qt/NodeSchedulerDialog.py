"""Update Me!"""
#Standard
import sys

#Third Party
from PyQt4 import QtGui

#Hydra
from hydra.node_scheduling import simplify_schedule_data, expand_schedule_data
from hydra.hydra_utils import find_resource

#Hydra Qt
from compiled_qt.UI_NodeScheduler import Ui_nodeSchedulerDialog

class NodeSchedulerDialog(QtGui.QDialog, Ui_nodeSchedulerDialog):
    def __init__(self, defaults, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.defaults = defaults

        if self.defaults:
            self.editorGroup.setTitle("Week Schedule for {0}".format(self.defaults["host"]))
            self.defaultSchedule = expand_schedule_data(self.defaults["week_schedule"])

        self.buildUI()

        #Set globals
        self.save = False

    def buildUI(self):
        #Load style sheet
        with open(find_resource("assets/styleSheet.css"), "r") as myStyles:
            self.setStyleSheet(myStyles.read())

        #Global colors
        self.onlineColor = QtGui.QColor(200, 240, 200)
        self.offlineColor = QtGui.QColor(240, 200, 200)
        self.whiteColor = QtGui.QColor(255, 255, 255)

        #Connect Buttons
        self.cancelButton.clicked.connect(self.cancelButtonHandler)
        self.okButton.clicked.connect(self.okButtonHandler)
        self.onlineButton.clicked.connect(self.onlineButtonHandler)
        self.offlineButton.clicked.connect(self.offlineButtonHandler)

        #Set properties
        self.scheduleTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        self.scheduleTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)

        #Make items in scheduleTable
        rowCount = self.scheduleTable.rowCount()
        colCount = self.scheduleTable.columnCount()
        for i in range(0, rowCount):
            for j in range(0, colCount):
                self.scheduleTable.setItem(i, j, QtGui.QTableWidgetItem())
                if not self.defaultSchedule:
                    self.scheduleTable.item(i, j).setBackgroundColor(self.onlineColor)
                    self.scheduleTable.item(i, j).setText("1")

        if self.defaultSchedule:
            schedList = []
            for i in range(0, len(self.defaultSchedule)):
                startRow = int(self.defaultSchedule[i].split(":")[0])
                startCol = int(self.defaultSchedule[i].split(":")[1])
                action = int(self.defaultSchedule[i].split(":")[2])
                try:
                    endRow = int(self.defaultSchedule[i + 1].split(":")[0])
                    endCol = int(self.defaultSchedule[i + 1].split(":")[1])
                except IndexError:
                    endRow = 6
                    endCol = 48
                if endRow > startRow:
                    for j in range(startRow, endRow):
                        schedList += [action for _ in range(0, (48 - startCol))]
                        startCol = 0
                schedList += [action for _ in range(startCol, endCol)]

            row = 0
            col = 0
            for item in schedList:
                if item == 1:
                    self.scheduleTable.item(row, col).setBackgroundColor(self.onlineColor)
                    self.scheduleTable.item(row, col).setText("1")
                else:
                    self.scheduleTable.item(row, col).setBackgroundColor(self.offlineColor)
                    self.scheduleTable.item(row, col).setText("0")
                col += 1
                if col > 47:
                    col = 0
                    row += 1
                if row > 6:
                    break

    def cancelButtonHandler(self):
        self.close()

    def okButtonHandler(self):
        self.save = True
        self.close()

    def getCurrentTableSelection(self):
        tableSel = self.scheduleTable.selectedRanges()
        returnList = []
        for sel in tableSel:
            top = sel.topRow()
            bottom = sel.bottomRow()
            left = sel.leftColumn()
            right = sel.rightColumn()
            vertical = [i for i in range(top, bottom + 1)]
            horizontal = [i for i in range(left, right + 1)]
            for i in vertical:
                for j in horizontal:
                    returnList.append([i, j])

        return returnList

    def onlineButtonHandler(self):
        mySel = self.getCurrentTableSelection()
        for sel in mySel:
            self.scheduleTable.item(sel[0], sel[1]).setBackgroundColor(self.onlineColor)
            self.scheduleTable.item(sel[0], sel[1]).setText("1")
        self.scheduleTable.clearSelection()

    def offlineButtonHandler(self):
        mySel = self.getCurrentTableSelection()
        for sel in mySel:
            self.scheduleTable.item(sel[0], sel[1]).setBackgroundColor(self.offlineColor)
            self.scheduleTable.item(sel[0], sel[1]).setText("0")
        self.scheduleTable.clearSelection()

    def getValues(self):
        rowCount = self.scheduleTable.rowCount()
        colCount = self.scheduleTable.columnCount()
        current = None
        valueList = []
        for i in range(0, rowCount):
            for j in range(0, colCount):
                item = int(self.scheduleTable.item(i, j).text())
                if current != item:
                    current = item
                    valueList.append("{0}:{1}:{2}".format(i, j, item))

        scheduleData = simplify_schedule_data(valueList)
        return scheduleData

    @classmethod
    def create(cls, defaults):
        dialog = NodeSchedulerDialog(defaults)
        dialog.exec_()
        if dialog.save:
            return dialog.getValues()

def main():
    app = QtGui.QApplication(sys.argv)
    window = NodeSchedulerDialog(None, None)
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
