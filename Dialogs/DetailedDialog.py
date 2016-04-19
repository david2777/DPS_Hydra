"""Update Me!"""
#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import datetime

#Hydra
from CompiledUI.UI_DetailedDialog import Ui_detailedDialog
from Setups.WidgetFactories import *
from Setups.MySQLSetup import db_username, hydra_jobboard

class DetailedDialog(QDialog, Ui_detailedDialog):
    def __init__(self, jobs, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.jobs = jobs
        #Connect Buttons
        self.okButton.clicked.connect(self.okButtonHandler)

        self.updateRenderJobGrid()

    def okButtonHandler(self):
        self.close()

    def updateRenderJobGrid(self):
        columns = [
            labelFactory('id'),
            labelFactory('owner'),
            labelFactory('niceName'),
            labelFactory('taskFile'),
            labelFactory('baseCMD'),
            labelFactory('startFrame'),
            labelFactory('endFrame'),
            labelFactory('execName'),
            labelFactory('phase'),
            labelFactory('requirements'),
            labelFactory('job_status'),
            labelFactory('maxNodes'),
            labelFactory('creationTime')
        ]

        clearLayout(self.detailedGridLayout)
        setupDataGrid(self.jobs, columns, self.detailedGridLayout)

    @classmethod
    def create(cls, jobs):
        dialog = DetailedDialog(jobs)
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

class widgetFactory():
    """A widget building class intended to be subclassed for building particular
    types of widgets. 'name' must be the name of a database column."""

    def __init__(self, name, intention = None):
        self.name = name
        self.intention = intention

    def headerWidget(self):
        """Makes a label for the header row of the display."""

        return QLabel('<b>' + self.name + '</b>')

    def data(self, record):

        return str(getattr(record, self.name))

    def dataWidget(self, record):
        """Create a QWidget instance and return a reference to it. To make a
        widget, given a record, extract the named attribute from the record
        with the data method, and use that as the widget's text/data."""

        raise NotImplementedError

class labelFactory(widgetFactory):
    """A label widget factory. The object's name is the name of a database
    column."""

    def dataWidget(self, record):
        return QLabel(self.data(record))
