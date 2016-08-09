# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_DataTableDialog.ui'
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

class Ui_DataTableWidget(object):
    def setupUi(self, DataTableWidget):
        DataTableWidget.setObjectName(_fromUtf8("DataTableWidget"))
        DataTableWidget.resize(643, 556)
        self.gridLayout = QtGui.QGridLayout(DataTableWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.DataTable = QtGui.QTableWidget(DataTableWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.DataTable.sizePolicy().hasHeightForWidth())
        self.DataTable.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.DataTable.setFont(font)
        self.DataTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.DataTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.DataTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.DataTable.setTabKeyNavigation(False)
        self.DataTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.DataTable.setGridStyle(QtCore.Qt.SolidLine)
        self.DataTable.setWordWrap(False)
        self.DataTable.setCornerButtonEnabled(False)
        self.DataTable.setRowCount(0)
        self.DataTable.setObjectName(_fromUtf8("DataTable"))
        self.DataTable.setColumnCount(1)
        item = QtGui.QTableWidgetItem()
        self.DataTable.setHorizontalHeaderItem(0, item)
        self.DataTable.horizontalHeader().setVisible(False)
        self.DataTable.horizontalHeader().setDefaultSectionSize(95)
        self.DataTable.horizontalHeader().setMinimumSectionSize(30)
        self.DataTable.horizontalHeader().setStretchLastSection(True)
        self.DataTable.verticalHeader().setDefaultSectionSize(20)
        self.DataTable.verticalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.DataTable, 0, 0, 1, 1)
        self.OkButton = QtGui.QPushButton(DataTableWidget)
        self.OkButton.setObjectName(_fromUtf8("OkButton"))
        self.gridLayout.addWidget(self.OkButton, 1, 0, 1, 1)

        self.retranslateUi(DataTableWidget)
        QtCore.QMetaObject.connectSlotsByName(DataTableWidget)
        DataTableWidget.setTabOrder(self.OkButton, self.DataTable)

    def retranslateUi(self, DataTableWidget):
        DataTableWidget.setWindowTitle(_translate("DataTableWidget", "Dialog", None))
        item = self.DataTable.horizontalHeaderItem(0)
        item.setText(_translate("DataTableWidget", "New Column", None))
        self.OkButton.setText(_translate("DataTableWidget", "Ok", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DataTableWidget = QtGui.QDialog()
    ui = Ui_DataTableWidget()
    ui.setupUi(DataTableWidget)
    DataTableWidget.show()
    sys.exit(app.exec_())

