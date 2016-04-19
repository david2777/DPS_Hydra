# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_DetailedDialog.ui'
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

class Ui_detailedDialog(object):
    def setupUi(self, detailedDialog):
        detailedDialog.setObjectName(_fromUtf8("detailedDialog"))
        detailedDialog.resize(1188, 449)
        self.formLayout = QtGui.QFormLayout(detailedDialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.scrollArea = QtGui.QScrollArea(detailedDialog)
        self.scrollArea.setMinimumSize(QtCore.QSize(0, 400))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 1168, 398))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.formLayout_3 = QtGui.QFormLayout(self.scrollAreaWidgetContents)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.detailedGridLayout = QtGui.QGridLayout()
        self.detailedGridLayout.setObjectName(_fromUtf8("detailedGridLayout"))
        self.formLayout_3.setLayout(0, QtGui.QFormLayout.LabelRole, self.detailedGridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.scrollArea)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(detailedDialog)
        self.okButton.setMinimumSize(QtCore.QSize(150, 0))
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.horizontalLayout.addWidget(self.okButton)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)

        self.retranslateUi(detailedDialog)
        QtCore.QMetaObject.connectSlotsByName(detailedDialog)

    def retranslateUi(self, detailedDialog):
        detailedDialog.setWindowTitle(_translate("detailedDialog", "Form", None))
        self.okButton.setText(_translate("detailedDialog", "Ok", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    detailedDialog = QtGui.QWidget()
    ui = Ui_detailedDialog()
    ui.setupUi(detailedDialog)
    detailedDialog.show()
    sys.exit(app.exec_())

