#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_DetailedDialog import Ui_detailedDialog

#Hydra
from Setups.WidgetFactories import labelFactory, clearLayout, setupDataGrid

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

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
