#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_DataTableDialog import Ui_DataTableWidget

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

class DataTableDialog(QDialog, Ui_DataTableWidget):
    def __init__(self, data, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        #Connect Buttons
        self.OkButton.clicked.connect(self.okButtonHandler)

        self.buildDataTable()

    def okButtonHandler(self):
        self.close()

    def buildDataTable(self):
        rows = self.data.__dict__.keys()
        rows = [str(row) for row in rows if row.find("__") is not 0]
        self.DataTable.setRowCount(len(rows))
        self.DataTable.setVerticalHeaderLabels(rows)

        for pos, row in enumerate(rows):
            self.DataTable.setItem(pos, 0, QTableWidgetItem(str(getattr(self.data, row))))

    @classmethod
    def create(cls, data):
        dialog = DataTableDialog(data)
        dialog.exec_()
