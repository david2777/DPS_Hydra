#Standard
from PyQt4 import QtGui

#Hydra Qt
from compiled_qt.UI_DetailedDialog import Ui_detailedDialog

#Hydra
from dialogs_qt.WidgetFactories import labelFactory, clear_layout, setup_data_grid

class DetailedDialog(QtGui.QDialog, Ui_detailedDialog):
    def __init__(self, data, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        #Connect Buttons
        self.okButton.clicked.connect(self.ok_button_handler)

        self.update_render_job_grid()

    def ok_button_handler(self):
        self.close()

    def update_render_job_grid(self):
        columns = self.data[0].__dict__.keys()
        columns = [labelFactory(col) for col in columns if col.find("__") is not 0]

        clear_layout(self.detailedGridLayout)
        setup_data_grid(self.data, columns, self.detailedGridLayout)

    @classmethod
    def create(cls, data):
        dialog = DetailedDialog(data)
        dialog.exec_()
