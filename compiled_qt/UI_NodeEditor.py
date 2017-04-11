# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\UI_NodeEditor.ui'
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
        nodeEditorDialog.resize(464, 228)
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
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.LabelRole, self.schedulerLabel)
        self.schedCheckBox = QtGui.QCheckBox(self.editorGroup)
        self.schedCheckBox.setObjectName(_fromUtf8("schedCheckBox"))
        self.formLayout_3.setWidget(2, QtGui.QFormLayout.FieldRole, self.schedCheckBox)
        self.compLabel = QtGui.QLabel(self.editorGroup)
        self.compLabel.setObjectName(_fromUtf8("compLabel"))
        self.formLayout_3.setWidget(6, QtGui.QFormLayout.LabelRole, self.compLabel)
        self.compGrid = QtGui.QGridLayout()
        self.compGrid.setObjectName(_fromUtf8("compGrid"))
        self.formLayout_3.setLayout(6, QtGui.QFormLayout.FieldRole, self.compGrid)
        self.minPrioritySpinbox = QtGui.QSpinBox(self.editorGroup)
        self.minPrioritySpinbox.setMinimum(1)
        self.minPrioritySpinbox.setMaximum(9999999)
        self.minPrioritySpinbox.setProperty("value", 50)
        self.minPrioritySpinbox.setObjectName(_fromUtf8("minPrioritySpinbox"))
        self.formLayout_3.setWidget(5, QtGui.QFormLayout.FieldRole, self.minPrioritySpinbox)
        self.minPriorityLabel = QtGui.QLabel(self.editorGroup)
        self.minPriorityLabel.setObjectName(_fromUtf8("minPriorityLabel"))
        self.formLayout_3.setWidget(5, QtGui.QFormLayout.LabelRole, self.minPriorityLabel)
        self.schedulerEditButton = QtGui.QPushButton(self.editorGroup)
        self.schedulerEditButton.setEnabled(False)
        self.schedulerEditButton.setObjectName(_fromUtf8("schedulerEditButton"))
        self.formLayout_3.setWidget(4, QtGui.QFormLayout.FieldRole, self.schedulerEditButton)
        self.renderNodeLabel = QtGui.QLabel(self.editorGroup)
        self.renderNodeLabel.setObjectName(_fromUtf8("renderNodeLabel"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.LabelRole, self.renderNodeLabel)
        self.renderNodeCheckBox = QtGui.QCheckBox(self.editorGroup)
        self.renderNodeCheckBox.setObjectName(_fromUtf8("renderNodeCheckBox"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.FieldRole, self.renderNodeCheckBox)
        self.ipLabel = QtGui.QLabel(self.editorGroup)
        self.ipLabel.setObjectName(_fromUtf8("ipLabel"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.ipLabel)
        self.ipLineEdit = QtGui.QLineEdit(self.editorGroup)
        self.ipLineEdit.setMaxLength(39)
        self.ipLineEdit.setObjectName(_fromUtf8("ipLineEdit"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.ipLineEdit)
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
        self.compLabel.setText(_translate("nodeEditorDialog", "Capabilities:", None))
        self.minPriorityLabel.setText(_translate("nodeEditorDialog", "Minimum Priority:", None))
        self.schedulerEditButton.setText(_translate("nodeEditorDialog", "Edit Node Schedule", None))
        self.renderNodeLabel.setText(_translate("nodeEditorDialog", "Render Node:", None))
        self.renderNodeCheckBox.setText(_translate("nodeEditorDialog", "Enable Rendering", None))
        self.ipLabel.setText(_translate("nodeEditorDialog", "IP Address:", None))
        self.ipLineEdit.setPlaceholderText(_translate("nodeEditorDialog", "Static IPv4 or IPv6 Address of Render Node", None))
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

