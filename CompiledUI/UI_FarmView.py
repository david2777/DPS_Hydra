# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_FarmView.ui'
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

class Ui_FarmView(object):
    def setupUi(self, FarmView):
        FarmView.setObjectName(_fromUtf8("FarmView"))
        FarmView.resize(1294, 716)
        self.centralwidget = QtGui.QWidget(FarmView)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_fetchButton = QtGui.QHBoxLayout()
        self.horizontalLayout_fetchButton.setSpacing(6)
        self.horizontalLayout_fetchButton.setObjectName(_fromUtf8("horizontalLayout_fetchButton"))
        self.updateButton = QtGui.QPushButton(self.centralwidget)
        self.updateButton.setObjectName(_fromUtf8("updateButton"))
        self.horizontalLayout_fetchButton.addWidget(self.updateButton)
        self.fetchButton = QtGui.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.fetchButton.setFont(font)
        self.fetchButton.setObjectName(_fromUtf8("fetchButton"))
        self.horizontalLayout_fetchButton.addWidget(self.fetchButton)
        self.autoUpdateCheckbox = QtGui.QCheckBox(self.centralwidget)
        self.autoUpdateCheckbox.setCheckable(True)
        self.autoUpdateCheckbox.setChecked(True)
        self.autoUpdateCheckbox.setObjectName(_fromUtf8("autoUpdateCheckbox"))
        self.horizontalLayout_fetchButton.addWidget(self.autoUpdateCheckbox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_fetchButton.addItem(spacerItem)
        self.onlineThisNodeButton = QtGui.QPushButton(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.onlineThisNodeButton.setFont(font)
        self.onlineThisNodeButton.setObjectName(_fromUtf8("onlineThisNodeButton"))
        self.horizontalLayout_fetchButton.addWidget(self.onlineThisNodeButton)
        self.offlineThisNodeButton = QtGui.QPushButton(self.centralwidget)
        self.offlineThisNodeButton.setObjectName(_fromUtf8("offlineThisNodeButton"))
        self.horizontalLayout_fetchButton.addWidget(self.offlineThisNodeButton)
        self.getOffThisNodeButton = QtGui.QPushButton(self.centralwidget)
        self.getOffThisNodeButton.setObjectName(_fromUtf8("getOffThisNodeButton"))
        self.horizontalLayout_fetchButton.addWidget(self.getOffThisNodeButton)
        self.gridLayout.addLayout(self.horizontalLayout_fetchButton, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.jobListTab = QtGui.QWidget()
        self.jobListTab.setObjectName(_fromUtf8("jobListTab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.jobListTab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter_nodelist = QtGui.QSplitter(self.jobListTab)
        self.splitter_nodelist.setOrientation(QtCore.Qt.Vertical)
        self.splitter_nodelist.setObjectName(_fromUtf8("splitter_nodelist"))
        self.splitter_jobList = QtGui.QSplitter(self.splitter_nodelist)
        self.splitter_jobList.setFrameShape(QtGui.QFrame.NoFrame)
        self.splitter_jobList.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_jobList.setObjectName(_fromUtf8("splitter_jobList"))
        self.layoutWidget_2 = QtGui.QWidget(self.splitter_jobList)
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.gridLayout_jobListJobs = QtGui.QGridLayout(self.layoutWidget_2)
        self.gridLayout_jobListJobs.setHorizontalSpacing(6)
        self.gridLayout_jobListJobs.setObjectName(_fromUtf8("gridLayout_jobListJobs"))
        self.jobTree = QtGui.QTreeWidget(self.layoutWidget_2)
        self.jobTree.setAlternatingRowColors(True)
        self.jobTree.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.jobTree.setIndentation(15)
        self.jobTree.setAnimated(True)
        self.jobTree.setObjectName(_fromUtf8("jobTree"))
        self.jobTree.header().setDefaultSectionSize(50)
        self.jobTree.header().setMinimumSectionSize(50)
        self.jobTree.header().setSortIndicatorShown(False)
        self.gridLayout_jobListJobs.addWidget(self.jobTree, 2, 0, 1, 4)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_jobListJobs.addItem(spacerItem1, 1, 1, 1, 1)
        self.userFilterCheckbox = QtGui.QCheckBox(self.layoutWidget_2)
        self.userFilterCheckbox.setObjectName(_fromUtf8("userFilterCheckbox"))
        self.gridLayout_jobListJobs.addWidget(self.userFilterCheckbox, 1, 3, 1, 1)
        self.jobTableLabel = QtGui.QLabel(self.layoutWidget_2)
        self.jobTableLabel.setObjectName(_fromUtf8("jobTableLabel"))
        self.gridLayout_jobListJobs.addWidget(self.jobTableLabel, 1, 0, 1, 1)
        self.archivedCheckBox = QtGui.QCheckBox(self.layoutWidget_2)
        self.archivedCheckBox.setObjectName(_fromUtf8("archivedCheckBox"))
        self.gridLayout_jobListJobs.addWidget(self.archivedCheckBox, 1, 2, 1, 1)
        self.layoutWidget_3 = QtGui.QWidget(self.splitter_jobList)
        self.layoutWidget_3.setObjectName(_fromUtf8("layoutWidget_3"))
        self.gridLayout_taskList = QtGui.QGridLayout(self.layoutWidget_3)
        self.gridLayout_taskList.setObjectName(_fromUtf8("gridLayout_taskList"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_taskList.addItem(spacerItem2, 0, 2, 1, 2)
        self.taskTableLabel = QtGui.QLabel(self.layoutWidget_3)
        self.taskTableLabel.setObjectName(_fromUtf8("taskTableLabel"))
        self.gridLayout_taskList.addWidget(self.taskTableLabel, 0, 0, 1, 2)
        self.taskTable = QtGui.QTableWidget(self.layoutWidget_3)
        self.taskTable.setEnabled(True)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.taskTable.setFont(font)
        self.taskTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.taskTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.taskTable.setAlternatingRowColors(False)
        self.taskTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.taskTable.setShowGrid(True)
        self.taskTable.setGridStyle(QtCore.Qt.SolidLine)
        self.taskTable.setCornerButtonEnabled(False)
        self.taskTable.setRowCount(0)
        self.taskTable.setObjectName(_fromUtf8("taskTable"))
        self.taskTable.setColumnCount(10)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(8, item)
        item = QtGui.QTableWidgetItem()
        self.taskTable.setHorizontalHeaderItem(9, item)
        self.taskTable.horizontalHeader().setDefaultSectionSize(100)
        self.taskTable.horizontalHeader().setMinimumSectionSize(25)
        self.taskTable.horizontalHeader().setStretchLastSection(True)
        self.taskTable.verticalHeader().setVisible(False)
        self.taskTable.verticalHeader().setDefaultSectionSize(20)
        self.gridLayout_taskList.addWidget(self.taskTable, 2, 0, 1, 4)
        self.renderNodeTable = QtGui.QTableWidget(self.splitter_nodelist)
        font = QtGui.QFont()
        font.setPointSize(8)
        self.renderNodeTable.setFont(font)
        self.renderNodeTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.renderNodeTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.renderNodeTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.renderNodeTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.renderNodeTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
        self.renderNodeTable.setShowGrid(True)
        self.renderNodeTable.setCornerButtonEnabled(False)
        self.renderNodeTable.setObjectName(_fromUtf8("renderNodeTable"))
        self.renderNodeTable.setColumnCount(9)
        self.renderNodeTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(6, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(7, item)
        item = QtGui.QTableWidgetItem()
        self.renderNodeTable.setHorizontalHeaderItem(8, item)
        self.renderNodeTable.horizontalHeader().setMinimumSectionSize(26)
        self.renderNodeTable.horizontalHeader().setStretchLastSection(True)
        self.renderNodeTable.verticalHeader().setVisible(False)
        self.renderNodeTable.verticalHeader().setDefaultSectionSize(20)
        self.gridLayout_3.addWidget(self.splitter_nodelist, 0, 0, 1, 1)
        self.tabWidget.addTab(self.jobListTab, _fromUtf8(""))
        self.jobsTab = QtGui.QWidget()
        self.jobsTab.setObjectName(_fromUtf8("jobsTab"))
        self.gridLayout_5 = QtGui.QGridLayout(self.jobsTab)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.scrollArea_recentTasks = QtGui.QScrollArea(self.jobsTab)
        self.scrollArea_recentTasks.setWidgetResizable(True)
        self.scrollArea_recentTasks.setObjectName(_fromUtf8("scrollArea_recentTasks"))
        self.scrollAreaWidgetContents_recentTasks = QtGui.QWidget()
        self.scrollAreaWidgetContents_recentTasks.setGeometry(QtCore.QRect(0, 0, 1250, 601))
        self.scrollAreaWidgetContents_recentTasks.setObjectName(_fromUtf8("scrollAreaWidgetContents_recentTasks"))
        self.gridLayout_2 = QtGui.QGridLayout(self.scrollAreaWidgetContents_recentTasks)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.limitSpinBox = QtGui.QSpinBox(self.scrollAreaWidgetContents_recentTasks)
        self.limitSpinBox.setMaximum(999)
        self.limitSpinBox.setProperty("value", 100)
        self.limitSpinBox.setObjectName(_fromUtf8("limitSpinBox"))
        self.gridLayout_2.addWidget(self.limitSpinBox, 0, 0, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem3, 2, 0, 1, 1)
        self.taskGrid = QtGui.QGridLayout()
        self.taskGrid.setObjectName(_fromUtf8("taskGrid"))
        self.gridLayout_2.addLayout(self.taskGrid, 1, 0, 1, 1)
        self.scrollArea_recentTasks.setWidget(self.scrollAreaWidgetContents_recentTasks)
        self.gridLayout_5.addWidget(self.scrollArea_recentTasks, 0, 0, 1, 1)
        self.tabWidget.addTab(self.jobsTab, _fromUtf8(""))
        self.thisNodeTab = QtGui.QWidget()
        self.thisNodeTab.setObjectName(_fromUtf8("thisNodeTab"))
        self.layoutWidget = QtGui.QWidget(self.thisNodeTab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 651, 223))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.formLayout_thisNodeLabels = QtGui.QFormLayout(self.layoutWidget)
        self.formLayout_thisNodeLabels.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_thisNodeLabels.setObjectName(_fromUtf8("formLayout_thisNodeLabels"))
        self.nodeNameLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.nodeNameLabel_LABEL.setObjectName(_fromUtf8("nodeNameLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.LabelRole, self.nodeNameLabel_LABEL)
        self.nodeNameLabel = QtGui.QLabel(self.layoutWidget)
        self.nodeNameLabel.setObjectName(_fromUtf8("nodeNameLabel"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.FieldRole, self.nodeNameLabel)
        self.nodeStatusLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.nodeStatusLabel_LABEL.setObjectName(_fromUtf8("nodeStatusLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.LabelRole, self.nodeStatusLabel_LABEL)
        self.nodeStatusLabel = QtGui.QLabel(self.layoutWidget)
        self.nodeStatusLabel.setObjectName(_fromUtf8("nodeStatusLabel"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.FieldRole, self.nodeStatusLabel)
        self.taskIDLabelLabel = QtGui.QLabel(self.layoutWidget)
        self.taskIDLabelLabel.setObjectName(_fromUtf8("taskIDLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.LabelRole, self.taskIDLabelLabel)
        self.taskIDLabel = QtGui.QLabel(self.layoutWidget)
        self.taskIDLabel.setObjectName(_fromUtf8("taskIDLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.FieldRole, self.taskIDLabel)
        self.nodeVersionLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.nodeVersionLabel_LABEL.setObjectName(_fromUtf8("nodeVersionLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.LabelRole, self.nodeVersionLabel_LABEL)
        self.nodeVersionLabel = QtGui.QLabel(self.layoutWidget)
        self.nodeVersionLabel.setObjectName(_fromUtf8("nodeVersionLabel"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.FieldRole, self.nodeVersionLabel)
        self.minPriorityLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.minPriorityLabel_LABEL.setObjectName(_fromUtf8("minPriorityLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.LabelRole, self.minPriorityLabel_LABEL)
        self.minPriorityLabel = QtGui.QLabel(self.layoutWidget)
        self.minPriorityLabel.setObjectName(_fromUtf8("minPriorityLabel"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.FieldRole, self.minPriorityLabel)
        self.capabilitiesLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.capabilitiesLabel_LABEL.setObjectName(_fromUtf8("capabilitiesLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.LabelRole, self.capabilitiesLabel_LABEL)
        self.capabilitiesLabel = QtGui.QLabel(self.layoutWidget)
        self.capabilitiesLabel.setObjectName(_fromUtf8("capabilitiesLabel"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.FieldRole, self.capabilitiesLabel)
        self.onlineTimeLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.onlineTimeLabel_LABEL.setObjectName(_fromUtf8("onlineTimeLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(6, QtGui.QFormLayout.LabelRole, self.onlineTimeLabel_LABEL)
        self.onlineTimeLabel = QtGui.QLabel(self.layoutWidget)
        self.onlineTimeLabel.setObjectName(_fromUtf8("onlineTimeLabel"))
        self.formLayout_thisNodeLabels.setWidget(6, QtGui.QFormLayout.FieldRole, self.onlineTimeLabel)
        self.offlineTimeLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.offlineTimeLabel_LABEL.setObjectName(_fromUtf8("offlineTimeLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(7, QtGui.QFormLayout.LabelRole, self.offlineTimeLabel_LABEL)
        self.offlineTimeLabel = QtGui.QLabel(self.layoutWidget)
        self.offlineTimeLabel.setObjectName(_fromUtf8("offlineTimeLabel"))
        self.formLayout_thisNodeLabels.setWidget(7, QtGui.QFormLayout.FieldRole, self.offlineTimeLabel)
        self.editThisNodeButton = QtGui.QPushButton(self.layoutWidget)
        self.editThisNodeButton.setEnabled(True)
        self.editThisNodeButton.setObjectName(_fromUtf8("editThisNodeButton"))
        self.formLayout_thisNodeLabels.setWidget(9, QtGui.QFormLayout.LabelRole, self.editThisNodeButton)
        self.pulseLabel_LABEL = QtGui.QLabel(self.layoutWidget)
        self.pulseLabel_LABEL.setObjectName(_fromUtf8("pulseLabel_LABEL"))
        self.formLayout_thisNodeLabels.setWidget(8, QtGui.QFormLayout.LabelRole, self.pulseLabel_LABEL)
        self.pulseLabel = QtGui.QLabel(self.layoutWidget)
        self.pulseLabel.setObjectName(_fromUtf8("pulseLabel"))
        self.formLayout_thisNodeLabels.setWidget(8, QtGui.QFormLayout.FieldRole, self.pulseLabel)
        self.tabWidget.addTab(self.thisNodeTab, _fromUtf8(""))
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        FarmView.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(FarmView)
        self.statusbar.setEnabled(True)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        FarmView.setStatusBar(self.statusbar)

        self.retranslateUi(FarmView)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(FarmView)

    def retranslateUi(self, FarmView):
        FarmView.setWindowTitle(_translate("FarmView", "FarmView", None))
        self.updateButton.setText(_translate("FarmView", "Soft Update", None))
        self.fetchButton.setText(_translate("FarmView", "Full Update", None))
        self.autoUpdateCheckbox.setText(_translate("FarmView", "Auto Update", None))
        self.onlineThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Allow this node to accept render tasks</p></body></html>", None))
        self.onlineThisNodeButton.setText(_translate("FarmView", "Online", None))
        self.offlineThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Don\'t allow this node to accept any new jobs (it will still finish what it\'s working on)</p></body></html>", None))
        self.offlineThisNodeButton.setText(_translate("FarmView", "Offline", None))
        self.getOffThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Tell this node to stop the current job, put it back on the job board, and don\'t accept any more.</p></body></html>", None))
        self.getOffThisNodeButton.setText(_translate("FarmView", "Get Off!", None))
        self.jobTree.headerItem().setText(0, _translate("FarmView", "1", None))
        self.userFilterCheckbox.setText(_translate("FarmView", "Only Show My Jobs", None))
        self.jobTableLabel.setText(_translate("FarmView", "Job List:", None))
        self.archivedCheckBox.setText(_translate("FarmView", "Show Archived Jobs", None))
        self.taskTableLabel.setText(_translate("FarmView", "Task List (Job ID: 0) (Node Limit: 0)", None))
        self.taskTable.setSortingEnabled(True)
        item = self.taskTable.horizontalHeaderItem(0)
        item.setText(_translate("FarmView", "Task ID", None))
        item = self.taskTable.horizontalHeaderItem(1)
        item.setText(_translate("FarmView", "Priority", None))
        item = self.taskTable.horizontalHeaderItem(2)
        item.setText(_translate("FarmView", "Frame", None))
        item = self.taskTable.horizontalHeaderItem(3)
        item.setText(_translate("FarmView", "Host", None))
        item = self.taskTable.horizontalHeaderItem(4)
        item.setText(_translate("FarmView", "Status", None))
        item = self.taskTable.horizontalHeaderItem(5)
        item.setText(_translate("FarmView", "Start Time", None))
        item = self.taskTable.horizontalHeaderItem(6)
        item.setText(_translate("FarmView", "End Time", None))
        item = self.taskTable.horizontalHeaderItem(7)
        item.setText(_translate("FarmView", "Duration", None))
        item = self.taskTable.horizontalHeaderItem(8)
        item.setText(_translate("FarmView", "Exit Code", None))
        item = self.taskTable.horizontalHeaderItem(9)
        item.setText(_translate("FarmView", "Reqs", None))
        self.renderNodeTable.setSortingEnabled(True)
        item = self.renderNodeTable.horizontalHeaderItem(0)
        item.setText(_translate("FarmView", "Host", None))
        item = self.renderNodeTable.horizontalHeaderItem(1)
        item.setText(_translate("FarmView", "Status", None))
        item = self.renderNodeTable.horizontalHeaderItem(2)
        item.setText(_translate("FarmView", "Task ID", None))
        item = self.renderNodeTable.horizontalHeaderItem(3)
        item.setText(_translate("FarmView", "Min Priority", None))
        item = self.renderNodeTable.horizontalHeaderItem(4)
        item.setText(_translate("FarmView", "Online Time", None))
        item = self.renderNodeTable.horizontalHeaderItem(5)
        item.setText(_translate("FarmView", "Offline Time", None))
        item = self.renderNodeTable.horizontalHeaderItem(6)
        item.setText(_translate("FarmView", "Last heartbeat", None))
        item = self.renderNodeTable.horizontalHeaderItem(7)
        item.setText(_translate("FarmView", "Version", None))
        item = self.renderNodeTable.horizontalHeaderItem(8)
        item.setText(_translate("FarmView", "Capabilities", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jobListTab), _translate("FarmView", "Job List", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jobsTab), _translate("FarmView", "Recent Jobs", None))
        self.nodeNameLabel_LABEL.setText(_translate("FarmView", "Node name:", None))
        self.nodeNameLabel.setText(_translate("FarmView", "N/A", None))
        self.nodeStatusLabel_LABEL.setText(_translate("FarmView", "Node status:", None))
        self.nodeStatusLabel.setText(_translate("FarmView", "N/A", None))
        self.taskIDLabelLabel.setText(_translate("FarmView", "Task ID:", None))
        self.taskIDLabel.setText(_translate("FarmView", "N/A", None))
        self.nodeVersionLabel_LABEL.setText(_translate("FarmView", "Version:", None))
        self.nodeVersionLabel.setText(_translate("FarmView", "N/A", None))
        self.minPriorityLabel_LABEL.setText(_translate("FarmView", "Min Priority:", None))
        self.minPriorityLabel.setText(_translate("FarmView", "N/A", None))
        self.capabilitiesLabel_LABEL.setText(_translate("FarmView", "Capabilities:", None))
        self.capabilitiesLabel.setText(_translate("FarmView", "N/A", None))
        self.onlineTimeLabel_LABEL.setText(_translate("FarmView", "Online Time:", None))
        self.onlineTimeLabel.setText(_translate("FarmView", "N/A", None))
        self.offlineTimeLabel_LABEL.setText(_translate("FarmView", "Offline Time:", None))
        self.offlineTimeLabel.setText(_translate("FarmView", "N/A", None))
        self.editThisNodeButton.setText(_translate("FarmView", "Edit This Node...", None))
        self.pulseLabel_LABEL.setText(_translate("FarmView", "Pulse:", None))
        self.pulseLabel.setText(_translate("FarmView", "N/A", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thisNodeTab), _translate("FarmView", "This Node", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FarmView = QtGui.QMainWindow()
    ui = Ui_FarmView()
    ui.setupUi(FarmView)
    FarmView.show()
    sys.exit(app.exec_())

