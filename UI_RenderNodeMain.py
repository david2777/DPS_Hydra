# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_RenderNodeMain.ui'
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

class Ui_RenderNodeMainWindow(object):
    def setupUi(self, RenderNodeMainWindow):
        RenderNodeMainWindow.setObjectName(_fromUtf8("RenderNodeMainWindow"))
        RenderNodeMainWindow.resize(837, 653)
        self.centralwidget = QtGui.QWidget(RenderNodeMainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.formLayout = QtGui.QFormLayout(self.centralwidget)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.MainGroup = QtGui.QGroupBox(self.centralwidget)
        self.MainGroup.setObjectName(_fromUtf8("MainGroup"))
        self.formLayout_2 = QtGui.QFormLayout(self.MainGroup)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.outputLabel = QtGui.QLabel(self.MainGroup)
        self.outputLabel.setObjectName(_fromUtf8("outputLabel"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.outputLabel)
        self.formLayout_thisNodeLabels = QtGui.QFormLayout()
        self.formLayout_thisNodeLabels.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_thisNodeLabels.setObjectName(_fromUtf8("formLayout_thisNodeLabels"))
        self.nodeNameLabelLabel = QtGui.QLabel(self.MainGroup)
        self.nodeNameLabelLabel.setObjectName(_fromUtf8("nodeNameLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.LabelRole, self.nodeNameLabelLabel)
        self.nodeNameLabel = QtGui.QLabel(self.MainGroup)
        self.nodeNameLabel.setText(_fromUtf8(""))
        self.nodeNameLabel.setObjectName(_fromUtf8("nodeNameLabel"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.FieldRole, self.nodeNameLabel)
        self.nodeStatusLabelLabel = QtGui.QLabel(self.MainGroup)
        self.nodeStatusLabelLabel.setObjectName(_fromUtf8("nodeStatusLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.LabelRole, self.nodeStatusLabelLabel)
        self.nodeStatusLabel = QtGui.QLabel(self.MainGroup)
        self.nodeStatusLabel.setText(_fromUtf8(""))
        self.nodeStatusLabel.setObjectName(_fromUtf8("nodeStatusLabel"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.FieldRole, self.nodeStatusLabel)
        self.taskIDLabelLabel = QtGui.QLabel(self.MainGroup)
        self.taskIDLabelLabel.setObjectName(_fromUtf8("taskIDLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.LabelRole, self.taskIDLabelLabel)
        self.taskIDLabel = QtGui.QLabel(self.MainGroup)
        self.taskIDLabel.setText(_fromUtf8(""))
        self.taskIDLabel.setObjectName(_fromUtf8("taskIDLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.FieldRole, self.taskIDLabel)
        self.nodeVersionLabelLabel = QtGui.QLabel(self.MainGroup)
        self.nodeVersionLabelLabel.setObjectName(_fromUtf8("nodeVersionLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel)
        self.nodeVersionLabel = QtGui.QLabel(self.MainGroup)
        self.nodeVersionLabel.setText(_fromUtf8(""))
        self.nodeVersionLabel.setObjectName(_fromUtf8("nodeVersionLabel"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.FieldRole, self.nodeVersionLabel)
        self.nodeVersionLabelLabel_4 = QtGui.QLabel(self.MainGroup)
        self.nodeVersionLabelLabel_4.setObjectName(_fromUtf8("nodeVersionLabelLabel_4"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel_4)
        self.minPriorityLabel = QtGui.QLabel(self.MainGroup)
        self.minPriorityLabel.setText(_fromUtf8(""))
        self.minPriorityLabel.setObjectName(_fromUtf8("minPriorityLabel"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.FieldRole, self.minPriorityLabel)
        self.nodeVersionLabelLabel_3 = QtGui.QLabel(self.MainGroup)
        self.nodeVersionLabelLabel_3.setObjectName(_fromUtf8("nodeVersionLabelLabel_3"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel_3)
        self.capabilitiesLabel = QtGui.QLabel(self.MainGroup)
        self.capabilitiesLabel.setText(_fromUtf8(""))
        self.capabilitiesLabel.setObjectName(_fromUtf8("capabilitiesLabel"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.FieldRole, self.capabilitiesLabel)
        self.editThisNodeButton = QtGui.QPushButton(self.MainGroup)
        self.editThisNodeButton.setEnabled(False)
        self.editThisNodeButton.setObjectName(_fromUtf8("editThisNodeButton"))
        self.formLayout_thisNodeLabels.setWidget(6, QtGui.QFormLayout.LabelRole, self.editThisNodeButton)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.SpanningRole, self.formLayout_thisNodeLabels)
        self.buttonLayout = QtGui.QHBoxLayout()
        self.buttonLayout.setObjectName(_fromUtf8("buttonLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem)
        self.onlineButton = QtGui.QPushButton(self.MainGroup)
        self.onlineButton.setObjectName(_fromUtf8("onlineButton"))
        self.buttonLayout.addWidget(self.onlineButton)
        self.offlineButton = QtGui.QPushButton(self.MainGroup)
        self.offlineButton.setObjectName(_fromUtf8("offlineButton"))
        self.buttonLayout.addWidget(self.offlineButton)
        self.getoffButton = QtGui.QPushButton(self.MainGroup)
        self.getoffButton.setObjectName(_fromUtf8("getoffButton"))
        self.buttonLayout.addWidget(self.getoffButton)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem1)
        self.formLayout_2.setLayout(2, QtGui.QFormLayout.SpanningRole, self.buttonLayout)
        self.outputTextEdit = QtGui.QTextEdit(self.MainGroup)
        self.outputTextEdit.setMinimumSize(QtCore.QSize(0, 350))
        self.outputTextEdit.setReadOnly(True)
        self.outputTextEdit.setObjectName(_fromUtf8("outputTextEdit"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.SpanningRole, self.outputTextEdit)
        self.trayButton = QtGui.QPushButton(self.MainGroup)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(50)
        font.setKerning(True)
        self.trayButton.setFont(font)
        self.trayButton.setObjectName(_fromUtf8("trayButton"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.SpanningRole, self.trayButton)
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.MainGroup)
        RenderNodeMainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(RenderNodeMainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        RenderNodeMainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(RenderNodeMainWindow)
        QtCore.QMetaObject.connectSlotsByName(RenderNodeMainWindow)

    def retranslateUi(self, RenderNodeMainWindow):
        RenderNodeMainWindow.setWindowTitle(_translate("RenderNodeMainWindow", "RenderNodeMain", None))
        self.MainGroup.setTitle(_translate("RenderNodeMainWindow", "Render Node Main", None))
        self.outputLabel.setText(_translate("RenderNodeMainWindow", "Output:", None))
        self.nodeNameLabelLabel.setText(_translate("RenderNodeMainWindow", "Node name:", None))
        self.nodeStatusLabelLabel.setText(_translate("RenderNodeMainWindow", "Node status:", None))
        self.taskIDLabelLabel.setText(_translate("RenderNodeMainWindow", "Task ID:", None))
        self.nodeVersionLabelLabel.setText(_translate("RenderNodeMainWindow", "Version:", None))
        self.nodeVersionLabelLabel_4.setText(_translate("RenderNodeMainWindow", "Min Priority:", None))
        self.nodeVersionLabelLabel_3.setText(_translate("RenderNodeMainWindow", "Capabilities:", None))
        self.editThisNodeButton.setText(_translate("RenderNodeMainWindow", "Edit This Node...", None))
        self.onlineButton.setText(_translate("RenderNodeMainWindow", "Online", None))
        self.offlineButton.setText(_translate("RenderNodeMainWindow", "Offline", None))
        self.getoffButton.setText(_translate("RenderNodeMainWindow", "Get Off!", None))
        self.trayButton.setText(_translate("RenderNodeMainWindow", "Send To Tray", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    RenderNodeMainWindow = QtGui.QMainWindow()
    ui = Ui_RenderNodeMainWindow()
    ui.setupUi(RenderNodeMainWindow)
    RenderNodeMainWindow.show()
    sys.exit(app.exec_())

