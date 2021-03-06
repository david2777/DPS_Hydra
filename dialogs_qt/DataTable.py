#Third Party
from PyQt4 import QtGui

#Hydra Qt
from compiled_qt.UI_DataTableDialog import Ui_DataTableWidget

class DataTableDialog(QtGui.QDialog, Ui_DataTableWidget):
    def __init__(self, data, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        #Connect Buttons
        self.OkButton.clicked.connect(self.ok_button_handler)

        self.build_data_table()

    def ok_button_handler(self):
        self.close()

    def build_data_table(self):
        rows = self.data.__dict__.keys()
        rows = [str(row) for row in rows if row.find("__") is not 0]
        self.DataTable.setRowCount(len(rows))
        self.DataTable.setVerticalHeaderLabels(rows)

        for pos, row in enumerate(rows):
            self.DataTable.setItem(pos, 0, QtGui.QTableWidgetItem(str(getattr(self.data, row))))

    @classmethod
    def create(cls, data):
        dialog = DataTableDialog(data)
        dialog.exec_()
