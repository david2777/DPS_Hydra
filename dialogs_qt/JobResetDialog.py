#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from compiled_qt.UI_JobResetDialog import Ui_jobResetDialog

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

class ResetDialog(QDialog, Ui_jobResetDialog):
    def __init__(self, data, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        self.save = False
        #Connect Buttons
        self.okButton.clicked.connect(self.ok_button_handler)
        self.cancelButton.clicked.connect(self.cancel_button_handler)

        self.populate_data()

    @classmethod
    def create(cls, data):
        dialog = ResetDialog(data)
        dialog.exec_()
        if dialog.save:
            return dialog.get_values()

    def populate_data(self):
        self.renderLayersLineEdit.setText(self.data[0])
        self.startFrameSpinbox.setValue(self.data[1])
        self.endFrameSpinbox.setValue(self.data[2])
        self.byFrameSpinbox.setValue(self.data[3])

    def get_values(self):
        renderLayers = str(self.renderLayersLineEdit.text())
        startFrame = self.startFrameSpinbox.value()
        endFrame = self.endFrameSpinbox.value()
        byFrame = self.byFrameSpinbox.value()
        resetNode = bool(self.resetNodeCheckbox.isChecked())
        return [renderLayers, startFrame, endFrame, byFrame, resetNode]

    def ok_button_handler(self):
        self.save = True
        self.close()

    def cancel_button_handler(self):
        self.close()
