# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_NodeScheduler.ui'
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

class Ui_nodeSchedulerDialog(object):
    def setupUi(self, nodeSchedulerDialog):
        nodeSchedulerDialog.setObjectName(_fromUtf8("nodeSchedulerDialog"))
        nodeSchedulerDialog.resize(1073, 338)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(nodeSchedulerDialog.sizePolicy().hasHeightForWidth())
        nodeSchedulerDialog.setSizePolicy(sizePolicy)
        nodeSchedulerDialog.setMinimumSize(QtCore.QSize(1073, 338))
        nodeSchedulerDialog.setMaximumSize(QtCore.QSize(1073, 338))
        self.formLayout = QtGui.QFormLayout(nodeSchedulerDialog)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.editorGroup = QtGui.QGroupBox(nodeSchedulerDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.editorGroup.sizePolicy().hasHeightForWidth())
        self.editorGroup.setSizePolicy(sizePolicy)
        self.editorGroup.setObjectName(_fromUtf8("editorGroup"))
        self.gridLayout_2 = QtGui.QGridLayout(self.editorGroup)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.hourLabel_01 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_01.setObjectName(_fromUtf8("hourLabel_01"))
        self.horizontalLayout.addWidget(self.hourLabel_01)
        self.hourLabel_02 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_02.setObjectName(_fromUtf8("hourLabel_02"))
        self.horizontalLayout.addWidget(self.hourLabel_02)
        self.hourLabel_03 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_03.setObjectName(_fromUtf8("hourLabel_03"))
        self.horizontalLayout.addWidget(self.hourLabel_03)
        self.hourLabel_04 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_04.setObjectName(_fromUtf8("hourLabel_04"))
        self.horizontalLayout.addWidget(self.hourLabel_04)
        self.hourLabel_05 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_05.setObjectName(_fromUtf8("hourLabel_05"))
        self.horizontalLayout.addWidget(self.hourLabel_05)
        self.hourLabel_06 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_06.setObjectName(_fromUtf8("hourLabel_06"))
        self.horizontalLayout.addWidget(self.hourLabel_06)
        self.hourLabel_07 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_07.setObjectName(_fromUtf8("hourLabel_07"))
        self.horizontalLayout.addWidget(self.hourLabel_07)
        self.hourLabel_08 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_08.setObjectName(_fromUtf8("hourLabel_08"))
        self.horizontalLayout.addWidget(self.hourLabel_08)
        self.hourLabel_09 = QtGui.QLabel(self.editorGroup)
        self.hourLabel_09.setObjectName(_fromUtf8("hourLabel_09"))
        self.horizontalLayout.addWidget(self.hourLabel_09)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.scheduleTable = QtGui.QTableWidget(self.editorGroup)
        self.scheduleTable.setMinimumSize(QtCore.QSize(1035, 212))
        self.scheduleTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scheduleTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scheduleTable.setAutoScroll(False)
        self.scheduleTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.scheduleTable.setTabKeyNavigation(False)
        self.scheduleTable.setProperty("showDropIndicator", False)
        self.scheduleTable.setDragDropOverwriteMode(False)
        self.scheduleTable.setWordWrap(False)
        self.scheduleTable.setCornerButtonEnabled(False)
        self.scheduleTable.setObjectName(_fromUtf8("scheduleTable"))
        self.scheduleTable.setColumnCount(48)
        self.scheduleTable.setRowCount(7)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setVerticalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(9, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(10, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(11, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(12, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(13, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(14, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(15, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(16, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(17, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(18, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(19, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(20, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(21, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(22, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(23, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(24, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(25, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(26, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(27, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(28, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(29, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(30, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(31, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(32, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(33, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(34, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(35, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(36, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(37, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(38, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(39, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(40, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(41, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(42, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(43, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(44, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(45, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(46, item)
        item = QtGui.QTableWidgetItem()
        self.scheduleTable.setHorizontalHeaderItem(47, item)
        self.scheduleTable.horizontalHeader().setDefaultSectionSize(20)
        self.scheduleTable.horizontalHeader().setStretchLastSection(True)
        self.scheduleTable.verticalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.scheduleTable, 1, 0, 1, 1)
        self.formLayout.setWidget(0, QtGui.QFormLayout.SpanningRole, self.editorGroup)
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        self.onlineButton = QtGui.QPushButton(nodeSchedulerDialog)
        self.onlineButton.setObjectName(_fromUtf8("onlineButton"))
        self.buttonsLayout.addWidget(self.onlineButton)
        self.offlineButton = QtGui.QPushButton(nodeSchedulerDialog)
        self.offlineButton.setObjectName(_fromUtf8("offlineButton"))
        self.buttonsLayout.addWidget(self.offlineButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem)
        self.okButton = QtGui.QPushButton(nodeSchedulerDialog)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.buttonsLayout.addWidget(self.okButton)
        self.cancelButton = QtGui.QPushButton(nodeSchedulerDialog)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))
        self.buttonsLayout.addWidget(self.cancelButton)
        self.formLayout.setLayout(1, QtGui.QFormLayout.SpanningRole, self.buttonsLayout)

        self.retranslateUi(nodeSchedulerDialog)
        QtCore.QMetaObject.connectSlotsByName(nodeSchedulerDialog)
        nodeSchedulerDialog.setTabOrder(self.okButton, self.cancelButton)

    def retranslateUi(self, nodeSchedulerDialog):
        nodeSchedulerDialog.setWindowTitle(_translate("nodeSchedulerDialog", "Dialog", None))
        self.editorGroup.setTitle(_translate("nodeSchedulerDialog", "Week Schedule for {0}", None))
        self.hourLabel_01.setText(_translate("nodeSchedulerDialog", "         Midnight |", None))
        self.hourLabel_02.setText(_translate("nodeSchedulerDialog", "                 3AM |", None))
        self.hourLabel_03.setText(_translate("nodeSchedulerDialog", "                   6AM |", None))
        self.hourLabel_04.setText(_translate("nodeSchedulerDialog", "                    9AM |", None))
        self.hourLabel_05.setText(_translate("nodeSchedulerDialog", "                   Noon |", None))
        self.hourLabel_06.setText(_translate("nodeSchedulerDialog", "                       3PM |", None))
        self.hourLabel_07.setText(_translate("nodeSchedulerDialog", "                         6PM |", None))
        self.hourLabel_08.setText(_translate("nodeSchedulerDialog", "                          9PM |", None))
        self.hourLabel_09.setText(_translate("nodeSchedulerDialog", "                    Midnight |", None))
        item = self.scheduleTable.verticalHeaderItem(0)
        item.setText(_translate("nodeSchedulerDialog", "Sunday", None))
        item = self.scheduleTable.verticalHeaderItem(1)
        item.setText(_translate("nodeSchedulerDialog", "Monday", None))
        item = self.scheduleTable.verticalHeaderItem(2)
        item.setText(_translate("nodeSchedulerDialog", "Tuesday", None))
        item = self.scheduleTable.verticalHeaderItem(3)
        item.setText(_translate("nodeSchedulerDialog", "Wednesday", None))
        item = self.scheduleTable.verticalHeaderItem(4)
        item.setText(_translate("nodeSchedulerDialog", "Thursday", None))
        item = self.scheduleTable.verticalHeaderItem(5)
        item.setText(_translate("nodeSchedulerDialog", "Friday", None))
        item = self.scheduleTable.verticalHeaderItem(6)
        item.setText(_translate("nodeSchedulerDialog", "Saturday", None))
        item = self.scheduleTable.horizontalHeaderItem(0)
        item.setText(_translate("nodeSchedulerDialog", "00", None))
        item = self.scheduleTable.horizontalHeaderItem(2)
        item.setText(_translate("nodeSchedulerDialog", "01", None))
        item = self.scheduleTable.horizontalHeaderItem(4)
        item.setText(_translate("nodeSchedulerDialog", "02", None))
        item = self.scheduleTable.horizontalHeaderItem(6)
        item.setText(_translate("nodeSchedulerDialog", "03", None))
        item = self.scheduleTable.horizontalHeaderItem(8)
        item.setText(_translate("nodeSchedulerDialog", "04", None))
        item = self.scheduleTable.horizontalHeaderItem(10)
        item.setText(_translate("nodeSchedulerDialog", "05", None))
        item = self.scheduleTable.horizontalHeaderItem(12)
        item.setText(_translate("nodeSchedulerDialog", "06", None))
        item = self.scheduleTable.horizontalHeaderItem(14)
        item.setText(_translate("nodeSchedulerDialog", "07", None))
        item = self.scheduleTable.horizontalHeaderItem(16)
        item.setText(_translate("nodeSchedulerDialog", "08", None))
        item = self.scheduleTable.horizontalHeaderItem(18)
        item.setText(_translate("nodeSchedulerDialog", "09", None))
        item = self.scheduleTable.horizontalHeaderItem(20)
        item.setText(_translate("nodeSchedulerDialog", "10", None))
        item = self.scheduleTable.horizontalHeaderItem(22)
        item.setText(_translate("nodeSchedulerDialog", "11", None))
        item = self.scheduleTable.horizontalHeaderItem(24)
        item.setText(_translate("nodeSchedulerDialog", "12", None))
        item = self.scheduleTable.horizontalHeaderItem(26)
        item.setText(_translate("nodeSchedulerDialog", "13", None))
        item = self.scheduleTable.horizontalHeaderItem(28)
        item.setText(_translate("nodeSchedulerDialog", "14", None))
        item = self.scheduleTable.horizontalHeaderItem(30)
        item.setText(_translate("nodeSchedulerDialog", "15", None))
        item = self.scheduleTable.horizontalHeaderItem(32)
        item.setText(_translate("nodeSchedulerDialog", "16", None))
        item = self.scheduleTable.horizontalHeaderItem(34)
        item.setText(_translate("nodeSchedulerDialog", "17", None))
        item = self.scheduleTable.horizontalHeaderItem(36)
        item.setText(_translate("nodeSchedulerDialog", "18", None))
        item = self.scheduleTable.horizontalHeaderItem(38)
        item.setText(_translate("nodeSchedulerDialog", "19", None))
        item = self.scheduleTable.horizontalHeaderItem(40)
        item.setText(_translate("nodeSchedulerDialog", "20", None))
        item = self.scheduleTable.horizontalHeaderItem(42)
        item.setText(_translate("nodeSchedulerDialog", "21", None))
        item = self.scheduleTable.horizontalHeaderItem(44)
        item.setText(_translate("nodeSchedulerDialog", "22", None))
        item = self.scheduleTable.horizontalHeaderItem(46)
        item.setText(_translate("nodeSchedulerDialog", "23", None))
        self.onlineButton.setText(_translate("nodeSchedulerDialog", "Online", None))
        self.offlineButton.setText(_translate("nodeSchedulerDialog", "Offline", None))
        self.okButton.setText(_translate("nodeSchedulerDialog", "Ok", None))
        self.cancelButton.setText(_translate("nodeSchedulerDialog", "Cancel", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    nodeSchedulerDialog = QtGui.QDialog()
    ui = Ui_nodeSchedulerDialog()
    ui.setupUi(nodeSchedulerDialog)
    nodeSchedulerDialog.show()
    sys.exit(app.exec_())

