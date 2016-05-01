"""Update Me!"""
#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_DetailedDialog import Ui_detailedDialog

#Hydra
from Setups.WidgetFactories import labelFactory
from Setups.MySQLSetup import db_username, hydra_jobboard

class DetailedDialog(QDialog, Ui_detailedDialog):
    def __init__(self, data, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        #Connect Buttons
        self.okButton.clicked.connect(self.okButtonHandler)

        self.updateRenderJobGrid()

    def okButtonHandler(self):
        self.close()

    def updateRenderJobGrid(self):
        columns = self.data[0].__dict__.keys()
        columns = [labelFactory(col) for col in columns if col.find("__") is not 0]

        clearLayout(self.detailedGridLayout)
        setupDataGrid(self.data, columns, self.detailedGridLayout)

    @classmethod
    def create(cls, data):
        dialog = DetailedDialog(data)
        dialog.exec_()


def setupDataGrid(records, columns, grid):
    """Populate a data grid. "colums" is a list of widget factory objects."""
    #Build the header row
    for(column, attr) in enumerate(columns):
        item = grid.itemAtPosition(0, column)
        if item:
            grid.removeItem(item)
            item.widget().hide()
        grid.addWidget(attr.headerWidget(), 0, column)

    #Build the data rows
    for(row, record) in enumerate(records):
        for(column, attr) in enumerate(columns):
            item = grid.itemAtPosition(row + 1, column)
            if item:
                grid.removeItem(item)
                item.widget().hide()
            grid.addWidget(attr.dataWidget(record),row + 1, column,)

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())
