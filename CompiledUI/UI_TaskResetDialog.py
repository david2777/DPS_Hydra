# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_TaskResetDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_taskResetDialog(object):
    def setupUi(self, taskResetDialog):
        taskResetDialog.setObjectName(_fromUtf8("taskResetDialog"))
        taskResetDialog.resize(345, 291)
        self.formLayout_2 = QtGui.QFormLayout(taskResetDialog)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.renderLayerListWidget = QtGui.QListWidget(taskResetDialog)
        self.renderLayerListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.renderLayerListWidget.setProperty("showDropIndicator", False)
        self.renderLayerListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.renderLayerListWidget.setUniformItemSizes(True)
        self.renderLayerListWidget.setObjectName(_fromUtf8("renderLayerListWidget"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.SpanningRole, self.renderLayerListWidget)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setObjectName(_fromUtf8("buttonLayout"))
        self.okButton = QtGui.QPushButton(taskResetDialog)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(taskResetDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonLayout.addWidget(self.cancelButton)
        self.formLayout_2.setLayout(4, QtGui.QFormLayout.FieldRole, self.buttonLayout)
        self.renderLayerLabel = QtGui.QLabel(taskResetDialog)
        self.renderLayerLabel.setObjectName(_fromUtf8("renderLayerLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.renderLayerLabel)
        self.startFrameSpinbox = QtGui.QSpinBox(taskResetDialog)
        self.startFrameSpinbox.setMaximum(999999)
        self.startFrameSpinbox.setProperty("value", 101)
        self.startFrameSpinbox.setObjectName(_fromUtf8("startFrameSpinbox"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.startFrameSpinbox)
        self.frameRangeLabel = QtGui.QLabel(taskResetDialog)
        self.frameRangeLabel.setObjectName(_fromUtf8("frameRangeLabel"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.frameRangeLabel)

        self.retranslateUi(taskResetDialog)
        QtCore.QMetaObject.connectSlotsByName(taskResetDialog)

    def retranslateUi(self, taskResetDialog):
        taskResetDialog.setWindowTitle(_translate("taskResetDialog", "Dialog", None))
        self.okButton.setText(_translate("taskResetDialog", "Ok", None))
        self.cancelButton.setText(_translate("taskResetDialog", "Cancel", None))
        self.renderLayerLabel.setText(_translate("taskResetDialog", "Render Layers:", None))
        self.frameRangeLabel.setText(_translate("taskResetDialog", "Start Frame:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    taskResetDialog = QtGui.QDialog()
    ui = Ui_taskResetDialog()
    ui.setupUi(taskResetDialog)
    taskResetDialog.show()
    sys.exit(app.exec_())

