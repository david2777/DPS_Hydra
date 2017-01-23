# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_JobResetDialog.ui'
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

class Ui_jobResetDialog(object):
    def setupUi(self, jobResetDialog):
        jobResetDialog.setObjectName(_fromUtf8("jobResetDialog"))
        jobResetDialog.resize(444, 144)
        self.formLayout = QtGui.QFormLayout(jobResetDialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.frameRangeLabel = QtGui.QLabel(jobResetDialog)
        self.frameRangeLabel.setObjectName(_fromUtf8("frameRangeLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.frameRangeLabel)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.startFrameSpinbox = QtGui.QSpinBox(jobResetDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startFrameSpinbox.sizePolicy().hasHeightForWidth())
        self.startFrameSpinbox.setSizePolicy(sizePolicy)
        self.startFrameSpinbox.setMinimum(1)
        self.startFrameSpinbox.setMaximum(999999)
        self.startFrameSpinbox.setProperty("value", 101)
        self.startFrameSpinbox.setObjectName(_fromUtf8("startFrameSpinbox"))
        self.horizontalLayout_2.addWidget(self.startFrameSpinbox)
        self.toLabel = QtGui.QLabel(jobResetDialog)
        self.toLabel.setObjectName(_fromUtf8("toLabel"))
        self.horizontalLayout_2.addWidget(self.toLabel)
        self.endFrameSpinbox = QtGui.QSpinBox(jobResetDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endFrameSpinbox.sizePolicy().hasHeightForWidth())
        self.endFrameSpinbox.setSizePolicy(sizePolicy)
        self.endFrameSpinbox.setMinimum(1)
        self.endFrameSpinbox.setMaximum(999999)
        self.endFrameSpinbox.setProperty("value", 101)
        self.endFrameSpinbox.setObjectName(_fromUtf8("endFrameSpinbox"))
        self.horizontalLayout_2.addWidget(self.endFrameSpinbox)
        self.byLabel = QtGui.QLabel(jobResetDialog)
        self.byLabel.setObjectName(_fromUtf8("byLabel"))
        self.horizontalLayout_2.addWidget(self.byLabel)
        self.byFrameSpinbox = QtGui.QSpinBox(jobResetDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.byFrameSpinbox.sizePolicy().hasHeightForWidth())
        self.byFrameSpinbox.setSizePolicy(sizePolicy)
        self.byFrameSpinbox.setMinimum(1)
        self.byFrameSpinbox.setMaximum(999999)
        self.byFrameSpinbox.setProperty("value", 1)
        self.byFrameSpinbox.setObjectName(_fromUtf8("byFrameSpinbox"))
        self.horizontalLayout_2.addWidget(self.byFrameSpinbox)
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.resetNodeCheckbox = QtGui.QCheckBox(jobResetDialog)
        self.resetNodeCheckbox.setChecked(True)
        self.resetNodeCheckbox.setObjectName(_fromUtf8("resetNodeCheckbox"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.FieldRole, self.resetNodeCheckbox)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setObjectName(_fromUtf8("buttonLayout"))
        self.okButton = QtGui.QPushButton(jobResetDialog)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(jobResetDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonLayout.addWidget(self.cancelButton)
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.buttonLayout)
        self.renderLayersLineEdit = QtGui.QLineEdit(jobResetDialog)
        self.renderLayersLineEdit.setMaxLength(120)
        self.renderLayersLineEdit.setObjectName(_fromUtf8("renderLayersLineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.renderLayersLineEdit)
        self.renderLayersLabel = QtGui.QLabel(jobResetDialog)
        self.renderLayersLabel.setObjectName(_fromUtf8("renderLayersLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.renderLayersLabel)

        self.retranslateUi(jobResetDialog)
        QtCore.QMetaObject.connectSlotsByName(jobResetDialog)

    def retranslateUi(self, jobResetDialog):
        jobResetDialog.setWindowTitle(_translate("jobResetDialog", "Dialog", None))
        self.frameRangeLabel.setText(_translate("jobResetDialog", "Frame Range:", None))
        self.toLabel.setText(_translate("jobResetDialog", "to", None))
        self.byLabel.setText(_translate("jobResetDialog", "by", None))
        self.resetNodeCheckbox.setText(_translate("jobResetDialog", "Reset Crashed Nodes", None))
        self.okButton.setText(_translate("jobResetDialog", "Ok", None))
        self.cancelButton.setText(_translate("jobResetDialog", "Cancel", None))
        self.renderLayersLineEdit.setPlaceholderText(_translate("jobResetDialog", "RenderLayers,Seperated,By,Commas", None))
        self.renderLayersLabel.setText(_translate("jobResetDialog", "Render Layers:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    jobResetDialog = QtGui.QDialog()
    ui = Ui_jobResetDialog()
    ui.setupUi(jobResetDialog)
    jobResetDialog.show()
    sys.exit(app.exec_())

