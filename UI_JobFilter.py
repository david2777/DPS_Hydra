# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_JobFilter.ui'
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

class Ui_jobFilterDialog(object):
    def setupUi(self, jobFilterDialog):
        jobFilterDialog.setObjectName(_fromUtf8("jobFilterDialog"))
        jobFilterDialog.resize(397, 280)
        self.formLayout_2 = QtGui.QFormLayout(jobFilterDialog)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.filterGroup = QtGui.QGroupBox(jobFilterDialog)
        self.filterGroup.setObjectName(_fromUtf8("filterGroup"))
        self.formLayout_3 = QtGui.QFormLayout(self.filterGroup)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.statusLabel = QtGui.QLabel(self.filterGroup)
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.statusLabel)
        self.statusGrid = QtGui.QGridLayout()
        self.statusGrid.setObjectName(_fromUtf8("statusGrid"))
        self.pausedCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.pausedCheckbox.setChecked(True)
        self.pausedCheckbox.setObjectName(_fromUtf8("pausedCheckbox"))
        self.statusGrid.addWidget(self.pausedCheckbox, 3, 0, 1, 1)
        self.crashedCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.crashedCheckbox.setChecked(True)
        self.crashedCheckbox.setObjectName(_fromUtf8("crashedCheckbox"))
        self.statusGrid.addWidget(self.crashedCheckbox, 5, 0, 1, 1)
        self.startedCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.startedCheckbox.setChecked(True)
        self.startedCheckbox.setObjectName(_fromUtf8("startedCheckbox"))
        self.statusGrid.addWidget(self.startedCheckbox, 0, 1, 1, 1)
        self.statusToggleButton = QtGui.QPushButton(self.filterGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusToggleButton.sizePolicy().hasHeightForWidth())
        self.statusToggleButton.setSizePolicy(sizePolicy)
        self.statusToggleButton.setObjectName(_fromUtf8("statusToggleButton"))
        self.statusGrid.addWidget(self.statusToggleButton, 5, 1, 1, 1)
        self.finishedCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.finishedCheckbox.setChecked(True)
        self.finishedCheckbox.setObjectName(_fromUtf8("finishedCheckbox"))
        self.statusGrid.addWidget(self.finishedCheckbox, 3, 1, 1, 1)
        self.killedCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.killedCheckbox.setChecked(True)
        self.killedCheckbox.setObjectName(_fromUtf8("killedCheckbox"))
        self.statusGrid.addWidget(self.killedCheckbox, 4, 0, 1, 1)
        self.readyCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.readyCheckbox.setChecked(True)
        self.readyCheckbox.setObjectName(_fromUtf8("readyCheckbox"))
        self.statusGrid.addWidget(self.readyCheckbox, 0, 0, 1, 1)
        self.errorCheckbox = QtGui.QCheckBox(self.filterGroup)
        self.errorCheckbox.setChecked(True)
        self.errorCheckbox.setObjectName(_fromUtf8("errorCheckbox"))
        self.statusGrid.addWidget(self.errorCheckbox, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.statusGrid.addItem(spacerItem, 6, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.statusGrid.addItem(spacerItem1, 6, 1, 1, 1)
        self.formLayout_3.setLayout(0, QtGui.QFormLayout.FieldRole, self.statusGrid)
        self.ownerLabel = QtGui.QLabel(self.filterGroup)
        self.ownerLabel.setObjectName(_fromUtf8("ownerLabel"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.ownerLabel)
        self.ownerLineEdit = QtGui.QLineEdit(self.filterGroup)
        self.ownerLineEdit.setObjectName(_fromUtf8("ownerLineEdit"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.ownerLineEdit)
        self.nameLabel = QtGui.QLabel(self.filterGroup)
        self.nameLabel.setObjectName(_fromUtf8("nameLabel"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.nameLabel)
        self.nameLineEdit = QtGui.QLineEdit(self.filterGroup)
        self.nameLineEdit.setObjectName(_fromUtf8("nameLineEdit"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.nameLineEdit)
        self.limitLabel = QtGui.QLabel(self.filterGroup)
        self.limitLabel.setObjectName(_fromUtf8("limitLabel"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.LabelRole, self.limitLabel)
        self.limitSpinBox = QtGui.QSpinBox(self.filterGroup)
        self.limitSpinBox.setMinimum(1)
        self.limitSpinBox.setMaximum(9999999)
        self.limitSpinBox.setProperty("value", 100)
        self.limitSpinBox.setObjectName(_fromUtf8("limitSpinBox"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.FieldRole, self.limitSpinBox)
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.SpanningRole, self.filterGroup)
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        self.resetButton = QtGui.QPushButton(jobFilterDialog)
        self.resetButton.setObjectName(_fromUtf8("resetButton"))
        self.buttonsLayout.addWidget(self.resetButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem2)
        self.okButton = QtGui.QPushButton(jobFilterDialog)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(jobFilterDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonsLayout.addWidget(self.cancelButton)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.SpanningRole, self.buttonsLayout)

        self.retranslateUi(jobFilterDialog)
        QtCore.QMetaObject.connectSlotsByName(jobFilterDialog)

    def retranslateUi(self, jobFilterDialog):
        jobFilterDialog.setWindowTitle(_translate("jobFilterDialog", "Dialog", None))
        self.filterGroup.setTitle(_translate("jobFilterDialog", "Job Filters...", None))
        self.statusLabel.setText(_translate("jobFilterDialog", "Filter By Status:", None))
        self.pausedCheckbox.setText(_translate("jobFilterDialog", "Paused", None))
        self.crashedCheckbox.setText(_translate("jobFilterDialog", "Crashed", None))
        self.startedCheckbox.setText(_translate("jobFilterDialog", "Started", None))
        self.statusToggleButton.setText(_translate("jobFilterDialog", "All On", None))
        self.finishedCheckbox.setText(_translate("jobFilterDialog", "Finished", None))
        self.killedCheckbox.setText(_translate("jobFilterDialog", "Killed", None))
        self.readyCheckbox.setText(_translate("jobFilterDialog", "Ready", None))
        self.errorCheckbox.setText(_translate("jobFilterDialog", "Error", None))
        self.ownerLabel.setText(_translate("jobFilterDialog", "Filter By Owner:", None))
        self.ownerLineEdit.setPlaceholderText(_translate("jobFilterDialog", ", = delimiter % = wildcard", None))
        self.nameLabel.setText(_translate("jobFilterDialog", "Filter By Name:", None))
        self.nameLineEdit.setPlaceholderText(_translate("jobFilterDialog", ", = delimiter % = wildcard", None))
        self.limitLabel.setText(_translate("jobFilterDialog", "Limit:", None))
        self.resetButton.setText(_translate("jobFilterDialog", "Reset", None))
        self.okButton.setText(_translate("jobFilterDialog", "Ok", None))
        self.cancelButton.setText(_translate("jobFilterDialog", "Cancel", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    jobFilterDialog = QtGui.QDialog()
    ui = Ui_jobFilterDialog()
    ui.setupUi(jobFilterDialog)
    jobFilterDialog.show()
    sys.exit(app.exec_())

