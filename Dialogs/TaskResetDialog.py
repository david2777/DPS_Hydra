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
        self.renderLayersCheckbox.stateChanged.connect(self.renderLayersCbxHandler)

        self.populateData()

    @classmethod
    def create(cls, data):
        dialog = ResetDialog(data)
        dialog.exec_()
        if dialog.save:
            return dialog.getValues()

    def renderLayersCbxHandler(self):
        if self.renderLayersCheckbox.isChecked():
            self.renderLayerListWidget.setEnabled(True)
            self.startFrameSpinbox.setEnabled(True)
        else:
            self.renderLayerListWidget.setEnabled(False)
            self.startFrameSpinbox.setEnabled(False)

    def populateData(self):
        renderLayers = self.data[0]
        startFrame = self.data[1]

        self.renderLayerListWidget.addItems(renderLayers)
        for i in range(len(self.data[0])):
            self.renderLayerListWidget.item(i).setSelected(True)
        self.startFrameSpinbox.setValue(startFrame)

    def getValues(self):
        if not bool(self.renderLayersCheckbox.isChecked()):
            selectedLayers = []
            startFrame = 0
        else:
            selectedLayers = [str(item.text()) for item in self.renderLayerListWidget.selectedItems()]
            startFrame = self.startFrameSpinbox.value()

        resetNode = bool(self.resetNodeCheckbox.isChecked())
        return [selectedLayers, startFrame, resetNode]

    def okButtonHandler(self):
        self.save = True
        self.close()

    def cancelButtonHandler(self):
        self.close()
