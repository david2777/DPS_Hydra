# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_FarmView.ui'
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
        FarmView.resize(1294, 710)
        self.centralwidget = QtGui.QWidget(FarmView)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.statusLabel = QtGui.QLabel(self.centralwidget)
        self.statusLabel.setText(_fromUtf8(""))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout.addWidget(self.statusLabel, 1, 0, 1, 1)
        self.horizontalLayout_fetchButton = QtGui.QHBoxLayout()
        self.horizontalLayout_fetchButton.setObjectName(_fromUtf8("horizontalLayout_fetchButton"))
        self.fetchButton = QtGui.QPushButton(self.centralwidget)
        self.fetchButton.setObjectName(_fromUtf8("fetchButton"))
        self.horizontalLayout_fetchButton.addWidget(self.fetchButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_fetchButton.addItem(spacerItem)
        self.gridLayout.addLayout(self.horizontalLayout_fetchButton, 2, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.thisNodeTab = QtGui.QWidget()
        self.thisNodeTab.setObjectName(_fromUtf8("thisNodeTab"))
        self.layoutWidget = QtGui.QWidget(self.thisNodeTab)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 20, 114, 122))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout_thisNodeButtons = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_thisNodeButtons.setObjectName(_fromUtf8("verticalLayout_thisNodeButtons"))
        self.onlineThisNodeButton = QtGui.QPushButton(self.layoutWidget)
        self.onlineThisNodeButton.setObjectName(_fromUtf8("onlineThisNodeButton"))
        self.verticalLayout_thisNodeButtons.addWidget(self.onlineThisNodeButton)
        self.offlineThisNodeButton = QtGui.QPushButton(self.layoutWidget)
        self.offlineThisNodeButton.setObjectName(_fromUtf8("offlineThisNodeButton"))
        self.verticalLayout_thisNodeButtons.addWidget(self.offlineThisNodeButton)
        self.getOffThisNodeButton = QtGui.QPushButton(self.layoutWidget)
        self.getOffThisNodeButton.setObjectName(_fromUtf8("getOffThisNodeButton"))
        self.verticalLayout_thisNodeButtons.addWidget(self.getOffThisNodeButton)
        self.layoutWidget1 = QtGui.QWidget(self.thisNodeTab)
        self.layoutWidget1.setGeometry(QtCore.QRect(150, 20, 651, 223))
        self.layoutWidget1.setObjectName(_fromUtf8("layoutWidget1"))
        self.formLayout_thisNodeLabels = QtGui.QFormLayout(self.layoutWidget1)
        self.formLayout_thisNodeLabels.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_thisNodeLabels.setObjectName(_fromUtf8("formLayout_thisNodeLabels"))
        self.nodeNameLabelLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeNameLabelLabel.setObjectName(_fromUtf8("nodeNameLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.LabelRole, self.nodeNameLabelLabel)
        self.nodeNameLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeNameLabel.setText(_fromUtf8(""))
        self.nodeNameLabel.setObjectName(_fromUtf8("nodeNameLabel"))
        self.formLayout_thisNodeLabels.setWidget(0, QtGui.QFormLayout.FieldRole, self.nodeNameLabel)
        self.nodeStatusLabelLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeStatusLabelLabel.setObjectName(_fromUtf8("nodeStatusLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.LabelRole, self.nodeStatusLabelLabel)
        self.nodeStatusLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeStatusLabel.setText(_fromUtf8(""))
        self.nodeStatusLabel.setObjectName(_fromUtf8("nodeStatusLabel"))
        self.formLayout_thisNodeLabels.setWidget(1, QtGui.QFormLayout.FieldRole, self.nodeStatusLabel)
        self.taskIDLabelLabel = QtGui.QLabel(self.layoutWidget1)
        self.taskIDLabelLabel.setObjectName(_fromUtf8("taskIDLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.LabelRole, self.taskIDLabelLabel)
        self.taskIDLabel = QtGui.QLabel(self.layoutWidget1)
        self.taskIDLabel.setText(_fromUtf8(""))
        self.taskIDLabel.setObjectName(_fromUtf8("taskIDLabel"))
        self.formLayout_thisNodeLabels.setWidget(2, QtGui.QFormLayout.FieldRole, self.taskIDLabel)
        self.nodeVersionLabelLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeVersionLabelLabel.setObjectName(_fromUtf8("nodeVersionLabelLabel"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel)
        self.nodeVersionLabel = QtGui.QLabel(self.layoutWidget1)
        self.nodeVersionLabel.setText(_fromUtf8(""))
        self.nodeVersionLabel.setObjectName(_fromUtf8("nodeVersionLabel"))
        self.formLayout_thisNodeLabels.setWidget(3, QtGui.QFormLayout.FieldRole, self.nodeVersionLabel)
        self.nodeVersionLabelLabel_4 = QtGui.QLabel(self.layoutWidget1)
        self.nodeVersionLabelLabel_4.setObjectName(_fromUtf8("nodeVersionLabelLabel_4"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel_4)
        self.minPriorityLabel = QtGui.QLabel(self.layoutWidget1)
        self.minPriorityLabel.setText(_fromUtf8(""))
        self.minPriorityLabel.setObjectName(_fromUtf8("minPriorityLabel"))
        self.formLayout_thisNodeLabels.setWidget(4, QtGui.QFormLayout.FieldRole, self.minPriorityLabel)
        self.nodeVersionLabelLabel_3 = QtGui.QLabel(self.layoutWidget1)
        self.nodeVersionLabelLabel_3.setObjectName(_fromUtf8("nodeVersionLabelLabel_3"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.LabelRole, self.nodeVersionLabelLabel_3)
        self.capabilitiesLabel = QtGui.QLabel(self.layoutWidget1)
        self.capabilitiesLabel.setText(_fromUtf8(""))
        self.capabilitiesLabel.setObjectName(_fromUtf8("capabilitiesLabel"))
        self.formLayout_thisNodeLabels.setWidget(5, QtGui.QFormLayout.FieldRole, self.capabilitiesLabel)
        self.tabWidget.addTab(self.thisNodeTab, _fromUtf8(""))
        self.renderNodesTab = QtGui.QWidget()
        self.renderNodesTab.setObjectName(_fromUtf8("renderNodesTab"))
        self.gridLayout_6 = QtGui.QGridLayout(self.renderNodesTab)
        self.gridLayout_6.setObjectName(_fromUtf8("gridLayout_6"))
        self.horizontalLayout_onOffButtons = QtGui.QHBoxLayout()
        self.horizontalLayout_onOffButtons.setObjectName(_fromUtf8("horizontalLayout_onOffButtons"))
        self.onlineRenderNodesButton = QtGui.QPushButton(self.renderNodesTab)
        self.onlineRenderNodesButton.setObjectName(_fromUtf8("onlineRenderNodesButton"))
        self.horizontalLayout_onOffButtons.addWidget(self.onlineRenderNodesButton)
        self.offlineRenderNodesButton = QtGui.QPushButton(self.renderNodesTab)
        self.offlineRenderNodesButton.setObjectName(_fromUtf8("offlineRenderNodesButton"))
        self.horizontalLayout_onOffButtons.addWidget(self.offlineRenderNodesButton)
        self.getOffRenderNodesButton = QtGui.QPushButton(self.renderNodesTab)
        self.getOffRenderNodesButton.setObjectName(_fromUtf8("getOffRenderNodesButton"))
        self.horizontalLayout_onOffButtons.addWidget(self.getOffRenderNodesButton)
        self.gridLayout_6.addLayout(self.horizontalLayout_onOffButtons, 1, 0, 1, 1)
        self.renderNodeTable = QtGui.QTableWidget(self.renderNodesTab)
        self.renderNodeTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.renderNodeTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.renderNodeTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.renderNodeTable.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerItem)
        self.renderNodeTable.setCornerButtonEnabled(False)
        self.renderNodeTable.setObjectName(_fromUtf8("renderNodeTable"))
        self.renderNodeTable.setColumnCount(8)
        self.renderNodeTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Wingdings"))
        item.setFont(font)
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
        self.renderNodeTable.horizontalHeader().setStretchLastSection(True)
        self.renderNodeTable.verticalHeader().setVisible(False)
        self.gridLayout_6.addWidget(self.renderNodeTable, 0, 0, 1, 1)
        self.tabWidget.addTab(self.renderNodesTab, _fromUtf8(""))
        self.jobListTab = QtGui.QWidget()
        self.jobListTab.setObjectName(_fromUtf8("jobListTab"))
        self.gridLayout_11 = QtGui.QGridLayout(self.jobListTab)
        self.gridLayout_11.setObjectName(_fromUtf8("gridLayout_11"))
        self.splitter_jobList = QtGui.QSplitter(self.jobListTab)
        self.splitter_jobList.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_jobList.sizePolicy().hasHeightForWidth())
        self.splitter_jobList.setSizePolicy(sizePolicy)
        self.splitter_jobList.setBaseSize(QtCore.QSize(0, 0))
        self.splitter_jobList.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_jobList.setOpaqueResize(True)
        self.splitter_jobList.setHandleWidth(5)
        self.splitter_jobList.setChildrenCollapsible(True)
        self.splitter_jobList.setObjectName(_fromUtf8("splitter_jobList"))
        self.layoutWidget_2 = QtGui.QWidget(self.splitter_jobList)
        self.layoutWidget_2.setObjectName(_fromUtf8("layoutWidget_2"))
        self.gridLayout_jobListJobs = QtGui.QGridLayout(self.layoutWidget_2)
        self.gridLayout_jobListJobs.setHorizontalSpacing(6)
        self.gridLayout_jobListJobs.setObjectName(_fromUtf8("gridLayout_jobListJobs"))
        self.jobTable = QtGui.QTableWidget(self.layoutWidget_2)
        self.jobTable.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.jobTable.setAutoFillBackground(False)
        self.jobTable.setFrameShape(QtGui.QFrame.StyledPanel)
        self.jobTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.jobTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.jobTable.setShowGrid(True)
        self.jobTable.setCornerButtonEnabled(False)
        self.jobTable.setColumnCount(6)
        self.jobTable.setObjectName(_fromUtf8("jobTable"))
        self.jobTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.jobTable.setHorizontalHeaderItem(5, item)
        self.jobTable.horizontalHeader().setStretchLastSection(True)
        self.jobTable.verticalHeader().setVisible(False)
        self.gridLayout_jobListJobs.addWidget(self.jobTable, 1, 0, 1, 5)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_jobListJobs.addItem(spacerItem1, 0, 1, 1, 4)
        self.jobTableLabel = QtGui.QLabel(self.layoutWidget_2)
        self.jobTableLabel.setObjectName(_fromUtf8("jobTableLabel"))
        self.gridLayout_jobListJobs.addWidget(self.jobTableLabel, 0, 0, 1, 1)
        self.groupBox_jobOptions = QtGui.QGroupBox(self.layoutWidget_2)
        self.groupBox_jobOptions.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBox_jobOptions.setObjectName(_fromUtf8("groupBox_jobOptions"))
        self.gridLayout_7 = QtGui.QGridLayout(self.groupBox_jobOptions)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.myFilterCheckbox = QtGui.QCheckBox(self.groupBox_jobOptions)
        self.myFilterCheckbox.setChecked(True)
        self.myFilterCheckbox.setObjectName(_fromUtf8("myFilterCheckbox"))
        self.gridLayout_7.addWidget(self.myFilterCheckbox, 2, 9, 1, 1)
        self.filterJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.filterJobButton.setEnabled(False)
        self.filterJobButton.setObjectName(_fromUtf8("filterJobButton"))
        self.gridLayout_7.addWidget(self.filterJobButton, 2, 5, 1, 1)
        self.testFramesButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.testFramesButton.setObjectName(_fromUtf8("testFramesButton"))
        self.gridLayout_7.addWidget(self.testFramesButton, 2, 0, 1, 1)
        self.startJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.startJobButton.setEnabled(True)
        self.startJobButton.setAcceptDrops(False)
        self.startJobButton.setAutoFillBackground(False)
        self.startJobButton.setStyleSheet(_fromUtf8(""))
        self.startJobButton.setCheckable(False)
        self.startJobButton.setFlat(False)
        self.startJobButton.setObjectName(_fromUtf8("startJobButton"))
        self.gridLayout_7.addWidget(self.startJobButton, 1, 0, 1, 1)
        self.pauseJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.pauseJobButton.setObjectName(_fromUtf8("pauseJobButton"))
        self.gridLayout_7.addWidget(self.pauseJobButton, 1, 1, 1, 1)
        self.resetJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.resetJobButton.setObjectName(_fromUtf8("resetJobButton"))
        self.gridLayout_7.addWidget(self.resetJobButton, 1, 9, 1, 1)
        self.editJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.editJobButton.setEnabled(False)
        self.editJobButton.setStyleSheet(_fromUtf8(""))
        self.editJobButton.setCheckable(False)
        self.editJobButton.setAutoDefault(False)
        self.editJobButton.setDefault(False)
        self.editJobButton.setObjectName(_fromUtf8("editJobButton"))
        self.gridLayout_7.addWidget(self.editJobButton, 2, 1, 1, 1)
        self.killJobButton = QtGui.QPushButton(self.groupBox_jobOptions)
        self.killJobButton.setObjectName(_fromUtf8("killJobButton"))
        self.gridLayout_7.addWidget(self.killJobButton, 1, 5, 1, 1)
        self.gridLayout_jobListJobs.addWidget(self.groupBox_jobOptions, 2, 0, 1, 5)
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
        self.taskTable.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.taskTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.taskTable.setGridStyle(QtCore.Qt.SolidLine)
        self.taskTable.setCornerButtonEnabled(False)
        self.taskTable.setObjectName(_fromUtf8("taskTable"))
        self.taskTable.setColumnCount(9)
        self.taskTable.setRowCount(0)
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
        self.taskTable.horizontalHeader().setStretchLastSection(True)
        self.taskTable.verticalHeader().setVisible(False)
        self.gridLayout_taskList.addWidget(self.taskTable, 2, 0, 1, 4)
        self.groupBox_subTaskOptions = QtGui.QGroupBox(self.layoutWidget_3)
        self.groupBox_subTaskOptions.setMinimumSize(QtCore.QSize(0, 28))
        self.groupBox_subTaskOptions.setObjectName(_fromUtf8("groupBox_subTaskOptions"))
        self.gridLayout_9 = QtGui.QGridLayout(self.groupBox_subTaskOptions)
        self.gridLayout_9.setObjectName(_fromUtf8("gridLayout_9"))
        self.loadLogButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.loadLogButton.setObjectName(_fromUtf8("loadLogButton"))
        self.gridLayout_9.addWidget(self.loadLogButton, 3, 0, 1, 1)
        self.startTaskButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.startTaskButton.setObjectName(_fromUtf8("startTaskButton"))
        self.gridLayout_9.addWidget(self.startTaskButton, 2, 0, 1, 1)
        self.pauseTaskButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.pauseTaskButton.setObjectName(_fromUtf8("pauseTaskButton"))
        self.gridLayout_9.addWidget(self.pauseTaskButton, 2, 2, 1, 1)
        self.killTaskButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.killTaskButton.setObjectName(_fromUtf8("killTaskButton"))
        self.gridLayout_9.addWidget(self.killTaskButton, 2, 5, 1, 1)
        self.editTaskButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.editTaskButton.setEnabled(False)
        self.editTaskButton.setObjectName(_fromUtf8("editTaskButton"))
        self.gridLayout_9.addWidget(self.editTaskButton, 3, 5, 1, 1)
        self.resetTaskButton = QtGui.QPushButton(self.groupBox_subTaskOptions)
        self.resetTaskButton.setObjectName(_fromUtf8("resetTaskButton"))
        self.gridLayout_9.addWidget(self.resetTaskButton, 3, 2, 1, 1)
        self.gridLayout_taskList.addWidget(self.groupBox_subTaskOptions, 3, 0, 1, 2)
        self.groupBox_search = QtGui.QGroupBox(self.layoutWidget_3)
        self.groupBox_search.setObjectName(_fromUtf8("groupBox_search"))
        self.gridLayout_10 = QtGui.QGridLayout(self.groupBox_search)
        self.gridLayout_10.setObjectName(_fromUtf8("gridLayout_10"))
        self.taskIDLineEdit = QtGui.QLineEdit(self.groupBox_search)
        self.taskIDLineEdit.setObjectName(_fromUtf8("taskIDLineEdit"))
        self.gridLayout_10.addWidget(self.taskIDLineEdit, 0, 0, 1, 1)
        self.advancedSearchButton = QtGui.QPushButton(self.groupBox_search)
        self.advancedSearchButton.setEnabled(False)
        self.advancedSearchButton.setObjectName(_fromUtf8("advancedSearchButton"))
        self.gridLayout_10.addWidget(self.advancedSearchButton, 0, 1, 1, 1)
        self.gridLayout_taskList.addWidget(self.groupBox_search, 3, 2, 1, 2)
        self.gridLayout_11.addWidget(self.splitter_jobList, 0, 0, 1, 1)
        self.tabWidget.addTab(self.jobListTab, _fromUtf8(""))
        self.jobsTab = QtGui.QWidget()
        self.jobsTab.setObjectName(_fromUtf8("jobsTab"))
        self.gridLayout_5 = QtGui.QGridLayout(self.jobsTab)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.scrollArea_recentTasks = QtGui.QScrollArea(self.jobsTab)
        self.scrollArea_recentTasks.setWidgetResizable(True)
        self.scrollArea_recentTasks.setObjectName(_fromUtf8("scrollArea_recentTasks"))
        self.scrollAreaWidgetContents_recentTasks = QtGui.QWidget()
        self.scrollAreaWidgetContents_recentTasks.setGeometry(QtCore.QRect(0, 0, 1250, 576))
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
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        FarmView.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(FarmView)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        FarmView.setStatusBar(self.statusbar)

        self.retranslateUi(FarmView)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(FarmView)

    def retranslateUi(self, FarmView):
        FarmView.setWindowTitle(_translate("FarmView", "FarmView", None))
        self.fetchButton.setText(_translate("FarmView", "Fetch", None))
        self.onlineThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Allow this node to accept render tasks</p></body></html>", None))
        self.onlineThisNodeButton.setText(_translate("FarmView", "Online", None))
        self.offlineThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Don\'t allow this node to accept any new jobs (it will still finish what it\'s working on)</p></body></html>", None))
        self.offlineThisNodeButton.setText(_translate("FarmView", "Offline", None))
        self.getOffThisNodeButton.setToolTip(_translate("FarmView", "<html><head/><body><p>Tell this node to stop the current job, put it back on the job board, and don\'t accept any more.</p></body></html>", None))
        self.getOffThisNodeButton.setText(_translate("FarmView", "Get Off!", None))
        self.nodeNameLabelLabel.setText(_translate("FarmView", "Node name:", None))
        self.nodeStatusLabelLabel.setText(_translate("FarmView", "Node status:", None))
        self.taskIDLabelLabel.setText(_translate("FarmView", "Task ID:", None))
        self.nodeVersionLabelLabel.setText(_translate("FarmView", "Version:", None))
        self.nodeVersionLabelLabel_4.setText(_translate("FarmView", "Min Priority:", None))
        self.nodeVersionLabelLabel_3.setText(_translate("FarmView", "Capabilities:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thisNodeTab), _translate("FarmView", "This Node", None))
        self.onlineRenderNodesButton.setText(_translate("FarmView", "Online", None))
        self.offlineRenderNodesButton.setText(_translate("FarmView", "Offline", None))
        self.getOffRenderNodesButton.setText(_translate("FarmView", "Get Off!", None))
        self.renderNodeTable.setSortingEnabled(True)
        item = self.renderNodeTable.horizontalHeaderItem(0)
        item.setText(_translate("FarmView", "þ", None))
        item = self.renderNodeTable.horizontalHeaderItem(1)
        item.setText(_translate("FarmView", "Host", None))
        item = self.renderNodeTable.horizontalHeaderItem(2)
        item.setText(_translate("FarmView", "Status", None))
        item = self.renderNodeTable.horizontalHeaderItem(3)
        item.setText(_translate("FarmView", "Task ID", None))
        item = self.renderNodeTable.horizontalHeaderItem(4)
        item.setText(_translate("FarmView", "Project", None))
        item = self.renderNodeTable.horizontalHeaderItem(5)
        item.setText(_translate("FarmView", "Capabilities", None))
        item = self.renderNodeTable.horizontalHeaderItem(6)
        item.setText(_translate("FarmView", "Version", None))
        item = self.renderNodeTable.horizontalHeaderItem(7)
        item.setText(_translate("FarmView", "Last heartbeat", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.renderNodesTab), _translate("FarmView", "Render Nodes", None))
        self.jobTable.setSortingEnabled(True)
        item = self.jobTable.horizontalHeaderItem(0)
        item.setText(_translate("FarmView", "Job ID", None))
        item = self.jobTable.horizontalHeaderItem(1)
        item.setText(_translate("FarmView", "Status", None))
        item = self.jobTable.horizontalHeaderItem(2)
        item.setText(_translate("FarmView", "Priority", None))
        item = self.jobTable.horizontalHeaderItem(3)
        item.setText(_translate("FarmView", "Owner", None))
        item = self.jobTable.horizontalHeaderItem(4)
        item.setText(_translate("FarmView", "Tasks", None))
        item = self.jobTable.horizontalHeaderItem(5)
        item.setText(_translate("FarmView", "Job Name", None))
        self.jobTableLabel.setText(_translate("FarmView", "Job List:", None))
        self.groupBox_jobOptions.setTitle(_translate("FarmView", "Job Options", None))
        self.myFilterCheckbox.setText(_translate("FarmView", "Filter My Jobs", None))
        self.filterJobButton.setText(_translate("FarmView", "Filters...", None))
        self.testFramesButton.setText(_translate("FarmView", "Start Test Frames...", None))
        self.startJobButton.setText(_translate("FarmView", "Start Job", None))
        self.pauseJobButton.setText(_translate("FarmView", "Pause Job", None))
        self.resetJobButton.setText(_translate("FarmView", "Reset Job", None))
        self.editJobButton.setText(_translate("FarmView", "Edit Job...", None))
        self.killJobButton.setText(_translate("FarmView", "Kill Job", None))
        self.taskTableLabel.setText(_translate("FarmView", "Task List (job: none selected)", None))
        self.taskTable.setSortingEnabled(True)
        item = self.taskTable.horizontalHeaderItem(0)
        item.setText(_translate("FarmView", "Task ID", None))
        item = self.taskTable.horizontalHeaderItem(1)
        item.setText(_translate("FarmView", "Frame", None))
        item = self.taskTable.horizontalHeaderItem(2)
        item.setText(_translate("FarmView", "Host", None))
        item = self.taskTable.horizontalHeaderItem(3)
        item.setText(_translate("FarmView", "Status", None))
        item = self.taskTable.horizontalHeaderItem(4)
        item.setText(_translate("FarmView", "Start Time", None))
        item = self.taskTable.horizontalHeaderItem(5)
        item.setText(_translate("FarmView", "End Time", None))
        item = self.taskTable.horizontalHeaderItem(6)
        item.setText(_translate("FarmView", "Duration", None))
        item = self.taskTable.horizontalHeaderItem(7)
        item.setText(_translate("FarmView", "Exit Code", None))
        item = self.taskTable.horizontalHeaderItem(8)
        item.setText(_translate("FarmView", "Reqs", None))
        self.groupBox_subTaskOptions.setTitle(_translate("FarmView", "Subtask Options", None))
        self.loadLogButton.setText(_translate("FarmView", "Load Log File", None))
        self.startTaskButton.setText(_translate("FarmView", "Start Task", None))
        self.pauseTaskButton.setText(_translate("FarmView", "Pause Task", None))
        self.killTaskButton.setText(_translate("FarmView", "Kill Task", None))
        self.editTaskButton.setText(_translate("FarmView", "Edit Task...", None))
        self.resetTaskButton.setText(_translate("FarmView", "Reset Task", None))
        self.groupBox_search.setTitle(_translate("FarmView", "Search", None))
        self.taskIDLineEdit.setPlaceholderText(_translate("FarmView", "Type TaskID, press Enter", None))
        self.advancedSearchButton.setText(_translate("FarmView", "Advanced...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jobListTab), _translate("FarmView", "Job List", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.jobsTab), _translate("FarmView", "Recent Tasks", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    FarmView = QtGui.QMainWindow()
    ui = Ui_FarmView()
    ui.setupUi(FarmView)
    FarmView.show()
    sys.exit(app.exec_())

