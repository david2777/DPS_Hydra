# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_NodeEditor.ui'
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

class Ui_nodeEditorDialog(object):
    def setupUi(self, nodeEditorDialog):
        nodeEditorDialog.setObjectName(_fromUtf8("nodeEditorDialog"))
        nodeEditorDialog.resize(445, 184)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(nodeEditorDialog.sizePolicy().hasHeightForWidth())
        nodeEditorDialog.setSizePolicy(sizePolicy)
        self.formLayout_2 = QtGui.QFormLayout(nodeEditorDialog)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.editorGroup = QtGui.QGroupBox(nodeEditorDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.editorGroup.sizePolicy().hasHeightForWidth())
        self.editorGroup.setSizePolicy(sizePolicy)
        self.editorGroup.setObjectName(_fromUtf8("editorGroup"))
        self.formLayout_3 = QtGui.QFormLayout(self.editorGroup)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.schedulerLabel = QtGui.QLabel(self.editorGroup)
        self.schedulerLabel.setObjectName(_fromUtf8("schedulerLabel"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.schedulerLabel)
        self.schedCheckBox = QtGui.QCheckBox(self.editorGroup)
        self.schedCheckBox.setChecked(True)
        self.schedCheckBox.setObjectName(_fromUtf8("schedCheckBox"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.schedCheckBox)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.onlineTimeEdit = QtGui.QTimeEdit(self.editorGroup)
        self.onlineTimeEdit.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.onlineTimeEdit.sizePolicy().hasHeightForWidth())
        self.onlineTimeEdit.setSizePolicy(sizePolicy)
        self.onlineTimeEdit.setTime(QtCore.QTime(18, 0, 0))
        self.onlineTimeEdit.setMinimumTime(QtCore.QTime(12, 0, 0))
        self.onlineTimeEdit.setCalendarPopup(False)
        self.onlineTimeEdit.setObjectName(_fromUtf8("onlineTimeEdit"))
        self.horizontalLayout_2.addWidget(self.onlineTimeEdit)
        self.label = QtGui.QLabel(self.editorGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.offlineTimeEdit = QtGui.QTimeEdit(self.editorGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.offlineTimeEdit.sizePolicy().hasHeightForWidth())
        self.offlineTimeEdit.setSizePolicy(sizePolicy)
        self.offlineTimeEdit.setTime(QtCore.QTime(8, 30, 0))
        self.offlineTimeEdit.setMaximumTime(QtCore.QTime(11, 59, 59))
        self.offlineTimeEdit.setObjectName(_fromUtf8("offlineTimeEdit"))
        self.horizontalLayout_2.addWidget(self.offlineTimeEdit)
        self.formLayout_3.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.onlineTimeLabel = QtGui.QLabel(self.editorGroup)
        self.onlineTimeLabel.setObjectName(_fromUtf8("onlineTimeLabel"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.onlineTimeLabel)
        self.minPriorityLabel = QtGui.QLabel(self.editorGroup)
        self.minPriorityLabel.setObjectName(_fromUtf8("minPriorityLabel"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.minPriorityLabel)
        self.minPrioritySpinbox = QtGui.QSpinBox(self.editorGroup)
        self.minPrioritySpinbox.setMinimum(1)
        self.minPrioritySpinbox.setMaximum(9999999)
        self.minPrioritySpinbox.setProperty("value", 50)
        self.minPrioritySpinbox.setObjectName(_fromUtf8("minPrioritySpinbox"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.minPrioritySpinbox)
        self.compLabel = QtGui.QLabel(self.editorGroup)
        self.compLabel.setObjectName(_fromUtf8("compLabel"))
        self.formLayout_3.setWidget(3, QtGui.QFormLayout.LabelRole, self.compLabel)
        self.compGrid = QtGui.QGridLayout()
        self.compGrid.setObjectName(_fromUtf8("compGrid"))
        self.formLayout_3.setLayout(3, QtGui.QFormLayout.FieldRole, self.compGrid)
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.SpanningRole, self.editorGroup)
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(nodeEditorDialog)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(nodeEditorDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonsLayout.addWidget(self.cancelButton)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.SpanningRole, self.buttonsLayout)

        self.retranslateUi(nodeEditorDialog)
        QtCore.QMetaObject.connectSlotsByName(nodeEditorDialog)
        nodeEditorDialog.setTabOrder(self.schedCheckBox, self.okButton)
        nodeEditorDialog.setTabOrder(self.okButton, self.cancelButton)

    def retranslateUi(self, nodeEditorDialog):
        nodeEditorDialog.setWindowTitle(_translate("nodeEditorDialog", "Dialog", None))
        self.editorGroup.setTitle(_translate("nodeEditorDialog", "Edit This Node", None))
        self.schedulerLabel.setText(_translate("nodeEditorDialog", "Scheduler:", None))
        self.schedCheckBox.setText(_translate("nodeEditorDialog", "Auto Online/Offline", None))
        self.onlineTimeEdit.setDisplayFormat(_translate("nodeEditorDialog", "h:mm AP", None))
        self.label.setText(_translate("nodeEditorDialog", "  :  ", None))
        self.offlineTimeEdit.setDisplayFormat(_translate("nodeEditorDialog", "h:mm AP", None))
        self.onlineTimeLabel.setText(_translate("nodeEditorDialog", "Scheduler Times:", None))
        self.minPriorityLabel.setText(_translate("nodeEditorDialog", "Minimum Priority:", None))
        self.compLabel.setText(_translate("nodeEditorDialog", "Capabilities:", None))
        self.okButton.setText(_translate("nodeEditorDialog", "Ok", None))
        self.cancelButton.setText(_translate("nodeEditorDialog", "Cancel", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    nodeEditorDialog = QtGui.QDialog()
    ui = Ui_nodeEditorDialog()
    ui.setupUi(nodeEditorDialog)
    nodeEditorDialog.show()
    sys.exit(app.exec_())

