#Standard
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_TaskResetDialog import Ui_taskResetDialog

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

class ResetDialog(QDialog, Ui_taskResetDialog):
    def __init__(self, data, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.data = data
        self.save = False
        #Connect Buttons
        self.okButton.clicked.connect(self.okButtonHandler)
        self.cancelButton.clicked.connect(self.cancelButtonHandler)

        self.populateData()

    @classmethod
    def create(cls, data):
        dialog = ResetDialog(data)
        dialog.exec_()
        if dialog.save:
            return dialog.getValues()

    def populateData(self):
        renderLayers = self.data[0]
        startFrame = self.data[1]

        self.renderLayerListWidget.addItems(renderLayers)
        for i in range(len(self.data[0])):
            self.renderLayerListWidget.item(i).setSelected(True)
        self.startFrameSpinbox.setValue(startFrame)

    def getValues(self):
        selectedLayers = [str(item.text()) for item in self.renderLayerListWidget.selectedItems()]
        startFrame = self.startFrameSpinbox.value()
        return [selectedLayers, startFrame]

    def okButtonHandler(self):
        self.save = True
        self.close()

    def cancelButtonHandler(self):
        self.close()
