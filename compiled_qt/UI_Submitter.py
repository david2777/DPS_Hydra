# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_Submitter.ui'
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(506, 351)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.standardTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.standardTab.sizePolicy().hasHeightForWidth())
        self.standardTab.setSizePolicy(sizePolicy)
        self.standardTab.setObjectName(_fromUtf8("standardTab"))
        self.formLayout = QtGui.QFormLayout(self.standardTab)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(6)
        self.formLayout.setHorizontalSpacing(6)
        self.formLayout.setVerticalSpacing(8)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.niceNameLabel = QtGui.QLabel(self.standardTab)
        self.niceNameLabel.setObjectName(_fromUtf8("niceNameLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.niceNameLabel)
        self.niceNameLineEdit = QtGui.QLineEdit(self.standardTab)
        self.niceNameLineEdit.setText(_fromUtf8(""))
        self.niceNameLineEdit.setObjectName(_fromUtf8("niceNameLineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.niceNameLineEdit)
        self.projectNameLabel = QtGui.QLabel(self.standardTab)
        self.projectNameLabel.setObjectName(_fromUtf8("projectNameLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.projectNameLabel)
        self.projectNameLineEdit = QtGui.QLineEdit(self.standardTab)
        self.projectNameLineEdit.setObjectName(_fromUtf8("projectNameLineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.projectNameLineEdit)
        self.renderLayersLabel = QtGui.QLabel(self.standardTab)
        self.renderLayersLabel.setObjectName(_fromUtf8("renderLayersLabel"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.renderLayersLabel)
        self.renderLayersLineEdit = QtGui.QLineEdit(self.standardTab)
        self.renderLayersLineEdit.setObjectName(_fromUtf8("renderLayersLineEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.renderLayersLineEdit)
        self.line_2 = QtGui.QFrame(self.standardTab)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.line_2)
        self.startFrameLabel = QtGui.QLabel(self.standardTab)
        self.startFrameLabel.setObjectName(_fromUtf8("startFrameLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.startFrameLabel)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.standardTab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 3, 1, 1)
        self.startSpinBox = QtGui.QSpinBox(self.standardTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.startSpinBox.sizePolicy().hasHeightForWidth())
        self.startSpinBox.setSizePolicy(sizePolicy)
        self.startSpinBox.setAccelerated(True)
        self.startSpinBox.setMinimum(1)
        self.startSpinBox.setMaximum(99999)
        self.startSpinBox.setObjectName(_fromUtf8("startSpinBox"))
        self.gridLayout.addWidget(self.startSpinBox, 0, 0, 1, 1)
        self.sepLabel = QtGui.QLabel(self.standardTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sepLabel.sizePolicy().hasHeightForWidth())
        self.sepLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.sepLabel.setFont(font)
        self.sepLabel.setScaledContents(False)
        self.sepLabel.setWordWrap(False)
        self.sepLabel.setObjectName(_fromUtf8("sepLabel"))
        self.gridLayout.addWidget(self.sepLabel, 0, 1, 1, 1)
        self.testFramesSpinBox = QtGui.QSpinBox(self.standardTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.testFramesSpinBox.sizePolicy().hasHeightForWidth())
        self.testFramesSpinBox.setSizePolicy(sizePolicy)
        self.testFramesSpinBox.setAccelerated(True)
        self.testFramesSpinBox.setMinimum(1)
        self.testFramesSpinBox.setMaximum(999)
        self.testFramesSpinBox.setProperty("value", 10)
        self.testFramesSpinBox.setObjectName(_fromUtf8("testFramesSpinBox"))
        self.gridLayout.addWidget(self.testFramesSpinBox, 0, 4, 1, 1)
        self.endSpinBox = QtGui.QSpinBox(self.standardTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endSpinBox.sizePolicy().hasHeightForWidth())
        self.endSpinBox.setSizePolicy(sizePolicy)
        self.endSpinBox.setAccelerated(True)
        self.endSpinBox.setMinimum(1)
        self.endSpinBox.setMaximum(99999)
        self.endSpinBox.setObjectName(_fromUtf8("endSpinBox"))
        self.gridLayout.addWidget(self.endSpinBox, 0, 2, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.gridLayout)
        self.line_6 = QtGui.QFrame(self.standardTab)
        self.line_6.setFrameShape(QtGui.QFrame.HLine)
        self.line_6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_6.setObjectName(_fromUtf8("line_6"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.SpanningRole, self.line_6)
        self.phasesLabel = QtGui.QLabel(self.standardTab)
        self.phasesLabel.setObjectName(_fromUtf8("phasesLabel"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.phasesLabel)
        self.phaseLayout = QtGui.QHBoxLayout()
        self.phaseLayout.setObjectName(_fromUtf8("phaseLayout"))
        self.testCheckBox = QtGui.QCheckBox(self.standardTab)
        self.testCheckBox.setChecked(True)
        self.testCheckBox.setObjectName(_fromUtf8("testCheckBox"))
        self.phaseLayout.addWidget(self.testCheckBox)
        self.finalCheckBox = QtGui.QCheckBox(self.standardTab)
        self.finalCheckBox.setChecked(True)
        self.finalCheckBox.setObjectName(_fromUtf8("finalCheckBox"))
        self.phaseLayout.addWidget(self.finalCheckBox)
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.phaseLayout)
        self.line_3 = QtGui.QFrame(self.standardTab)
        self.line_3.setLineWidth(2)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.formLayout.setWidget(9, QtGui.QFormLayout.SpanningRole, self.line_3)
        self.jobTypeLabel = QtGui.QLabel(self.standardTab)
        self.jobTypeLabel.setObjectName(_fromUtf8("jobTypeLabel"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.LabelRole, self.jobTypeLabel)
        self.requirementsLabel = QtGui.QLabel(self.standardTab)
        self.requirementsLabel.setObjectName(_fromUtf8("requirementsLabel"))
        self.formLayout.setWidget(11, QtGui.QFormLayout.LabelRole, self.requirementsLabel)
        self.reqsGrid = QtGui.QGridLayout()
        self.reqsGrid.setObjectName(_fromUtf8("reqsGrid"))
        self.formLayout.setLayout(11, QtGui.QFormLayout.FieldRole, self.reqsGrid)
        self.jobTypeComboBox = QtGui.QComboBox(self.standardTab)
        self.jobTypeComboBox.setObjectName(_fromUtf8("jobTypeComboBox"))
        self.formLayout.setWidget(10, QtGui.QFormLayout.FieldRole, self.jobTypeComboBox)
        self.taskStyleLabel = QtGui.QLabel(self.standardTab)
        self.taskStyleLabel.setObjectName(_fromUtf8("taskStyleLabel"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.LabelRole, self.taskStyleLabel)
        self.taskStyleLayout = QtGui.QHBoxLayout()
        self.taskStyleLayout.setObjectName(_fromUtf8("taskStyleLayout"))
        self.multiTaskRadio = QtGui.QRadioButton(self.standardTab)
        self.multiTaskRadio.setChecked(True)
        self.multiTaskRadio.setObjectName(_fromUtf8("multiTaskRadio"))
        self.taskStyleLayout.addWidget(self.multiTaskRadio)
        self.singleTaskRadio = QtGui.QRadioButton(self.standardTab)
        self.singleTaskRadio.setObjectName(_fromUtf8("singleTaskRadio"))
        self.taskStyleLayout.addWidget(self.singleTaskRadio)
        self.formLayout.setLayout(8, QtGui.QFormLayout.FieldRole, self.taskStyleLayout)
        self.tabWidget.addTab(self.standardTab, _fromUtf8(""))
        self.advancedTab = QtGui.QWidget()
        self.advancedTab.setObjectName(_fromUtf8("advancedTab"))
        self.formLayout_2 = QtGui.QFormLayout(self.advancedTab)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.sceneLabel = QtGui.QLabel(self.advancedTab)
        self.sceneLabel.setObjectName(_fromUtf8("sceneLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.sceneLabel)
        self.sceneLayout = QtGui.QGridLayout()
        self.sceneLayout.setObjectName(_fromUtf8("sceneLayout"))
        self.sceneButton = QtGui.QPushButton(self.advancedTab)
        self.sceneButton.setObjectName(_fromUtf8("sceneButton"))
        self.sceneLayout.addWidget(self.sceneButton, 0, 1, 1, 1)
        self.sceneLineEdit = QtGui.QLineEdit(self.advancedTab)
        self.sceneLineEdit.setObjectName(_fromUtf8("sceneLineEdit"))
        self.sceneLayout.addWidget(self.sceneLineEdit, 0, 0, 1, 1)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.FieldRole, self.sceneLayout)
        self.projLabel = QtGui.QLabel(self.advancedTab)
        self.projLabel.setObjectName(_fromUtf8("projLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.projLabel)
        self.mayaProjLayout = QtGui.QGridLayout()
        self.mayaProjLayout.setObjectName(_fromUtf8("mayaProjLayout"))
        self.projButton = QtGui.QPushButton(self.advancedTab)
        self.projButton.setObjectName(_fromUtf8("projButton"))
        self.mayaProjLayout.addWidget(self.projButton, 0, 1, 1, 1)
        self.projLineEdit = QtGui.QLineEdit(self.advancedTab)
        self.projLineEdit.setReadOnly(False)
        self.projLineEdit.setObjectName(_fromUtf8("projLineEdit"))
        self.mayaProjLayout.addWidget(self.projLineEdit, 0, 0, 1, 1)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.FieldRole, self.mayaProjLayout)
        self.startStatusLabel = QtGui.QLabel(self.advancedTab)
        self.startStatusLabel.setObjectName(_fromUtf8("startStatusLabel"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.startStatusLabel)
        self.startStatusLayout = QtGui.QHBoxLayout()
        self.startStatusLayout.setObjectName(_fromUtf8("startStatusLayout"))
        self.startStatusRadioButton = QtGui.QRadioButton(self.advancedTab)
        self.startStatusRadioButton.setChecked(True)
        self.startStatusRadioButton.setObjectName(_fromUtf8("startStatusRadioButton"))
        self.startStatusLayout.addWidget(self.startStatusRadioButton)
        self.pauseStatusRadioButton = QtGui.QRadioButton(self.advancedTab)
        self.pauseStatusRadioButton.setObjectName(_fromUtf8("pauseStatusRadioButton"))
        self.startStatusLayout.addWidget(self.pauseStatusRadioButton)
        self.formLayout_2.setLayout(3, QtGui.QFormLayout.FieldRole, self.startStatusLayout)
        self.line = QtGui.QFrame(self.advancedTab)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.formLayout_2.setWidget(4, QtGui.QFormLayout.SpanningRole, self.line)
        self.priorityLabel = QtGui.QLabel(self.advancedTab)
        self.priorityLabel.setObjectName(_fromUtf8("priorityLabel"))
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.LabelRole, self.priorityLabel)
        self.prioritySpinBox = QtGui.QSpinBox(self.advancedTab)
        self.prioritySpinBox.setMinimum(-100)
        self.prioritySpinBox.setMaximum(99999)
        self.prioritySpinBox.setProperty("value", 50)
        self.prioritySpinBox.setObjectName(_fromUtf8("prioritySpinBox"))
        self.formLayout_2.setWidget(6, QtGui.QFormLayout.FieldRole, self.prioritySpinBox)
        self.executableLabel = QtGui.QLabel(self.advancedTab)
        self.executableLabel.setObjectName(_fromUtf8("executableLabel"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.LabelRole, self.executableLabel)
        self.executableComboBox = QtGui.QComboBox(self.advancedTab)
        self.executableComboBox.setObjectName(_fromUtf8("executableComboBox"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.FieldRole, self.executableComboBox)
        self.cmdLabel = QtGui.QLabel(self.advancedTab)
        self.cmdLabel.setObjectName(_fromUtf8("cmdLabel"))
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.LabelRole, self.cmdLabel)
        self.cmdLineEdit = QtGui.QLineEdit(self.advancedTab)
        self.cmdLineEdit.setText(_fromUtf8(""))
        self.cmdLineEdit.setObjectName(_fromUtf8("cmdLineEdit"))
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.FieldRole, self.cmdLineEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.maxNodesP1Label = QtGui.QLabel(self.advancedTab)
        self.maxNodesP1Label.setObjectName(_fromUtf8("maxNodesP1Label"))
        self.horizontalLayout.addWidget(self.maxNodesP1Label)
        self.maxNodesP1SpinBox = QtGui.QSpinBox(self.advancedTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxNodesP1SpinBox.sizePolicy().hasHeightForWidth())
        self.maxNodesP1SpinBox.setSizePolicy(sizePolicy)
        self.maxNodesP1SpinBox.setMaximum(500)
        self.maxNodesP1SpinBox.setProperty("value", 1)
        self.maxNodesP1SpinBox.setObjectName(_fromUtf8("maxNodesP1SpinBox"))
        self.horizontalLayout.addWidget(self.maxNodesP1SpinBox)
        self.maxNodesP2Label = QtGui.QLabel(self.advancedTab)
        self.maxNodesP2Label.setObjectName(_fromUtf8("maxNodesP2Label"))
        self.horizontalLayout.addWidget(self.maxNodesP2Label)
        self.maxNodesP2SpinBox = QtGui.QSpinBox(self.advancedTab)
        self.maxNodesP2SpinBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.maxNodesP2SpinBox.sizePolicy().hasHeightForWidth())
        self.maxNodesP2SpinBox.setSizePolicy(sizePolicy)
        self.maxNodesP2SpinBox.setMaximum(500)
        self.maxNodesP2SpinBox.setProperty("value", 0)
        self.maxNodesP2SpinBox.setObjectName(_fromUtf8("maxNodesP2SpinBox"))
        self.horizontalLayout.addWidget(self.maxNodesP2SpinBox)
        self.formLayout_2.setLayout(10, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.testNodesLabel = QtGui.QLabel(self.advancedTab)
        self.testNodesLabel.setObjectName(_fromUtf8("testNodesLabel"))
        self.formLayout_2.setWidget(10, QtGui.QFormLayout.LabelRole, self.testNodesLabel)
        self.timeoutLabel = QtGui.QLabel(self.advancedTab)
        self.timeoutLabel.setObjectName(_fromUtf8("timeoutLabel"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.LabelRole, self.timeoutLabel)
        self.timeoutSpinbox = QtGui.QSpinBox(self.advancedTab)
        self.timeoutSpinbox.setSuffix(_fromUtf8(""))
        self.timeoutSpinbox.setMaximum(999)
        self.timeoutSpinbox.setProperty("value", 170)
        self.timeoutSpinbox.setObjectName(_fromUtf8("timeoutSpinbox"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.FieldRole, self.timeoutSpinbox)
        self.frameDirLabel = QtGui.QLabel(self.advancedTab)
        self.frameDirLabel.setObjectName(_fromUtf8("frameDirLabel"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.frameDirLabel)
        self.frameDirLayout = QtGui.QGridLayout()
        self.frameDirLayout.setObjectName(_fromUtf8("frameDirLayout"))
        self.frameDirLineEdit = QtGui.QLineEdit(self.advancedTab)
        self.frameDirLineEdit.setObjectName(_fromUtf8("frameDirLineEdit"))
        self.frameDirLayout.addWidget(self.frameDirLineEdit, 0, 0, 1, 1)
        self.frameDirButton = QtGui.QPushButton(self.advancedTab)
        self.frameDirButton.setObjectName(_fromUtf8("frameDirButton"))
        self.frameDirLayout.addWidget(self.frameDirButton, 0, 1, 1, 1)
        self.formLayout_2.setLayout(2, QtGui.QFormLayout.FieldRole, self.frameDirLayout)
        self.tabWidget.addTab(self.advancedTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.submitButton = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.submitButton.sizePolicy().hasHeightForWidth())
        self.submitButton.setSizePolicy(sizePolicy)
        self.submitButton.setObjectName(_fromUtf8("submitButton"))
        self.verticalLayout.addWidget(self.submitButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.niceNameLabel.setBuddy(self.niceNameLineEdit)
        self.renderLayersLabel.setBuddy(self.renderLayersLineEdit)
        self.startFrameLabel.setBuddy(self.startSpinBox)
        self.phasesLabel.setBuddy(self.testCheckBox)
        self.priorityLabel.setBuddy(self.prioritySpinBox)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.niceNameLineEdit, self.projectNameLineEdit)
        MainWindow.setTabOrder(self.projectNameLineEdit, self.renderLayersLineEdit)
        MainWindow.setTabOrder(self.renderLayersLineEdit, self.startSpinBox)
        MainWindow.setTabOrder(self.startSpinBox, self.endSpinBox)
        MainWindow.setTabOrder(self.endSpinBox, self.testFramesSpinBox)
        MainWindow.setTabOrder(self.testFramesSpinBox, self.testCheckBox)
        MainWindow.setTabOrder(self.testCheckBox, self.finalCheckBox)
        MainWindow.setTabOrder(self.finalCheckBox, self.tabWidget)
        MainWindow.setTabOrder(self.tabWidget, self.sceneLineEdit)
        MainWindow.setTabOrder(self.sceneLineEdit, self.sceneButton)
        MainWindow.setTabOrder(self.sceneButton, self.projLineEdit)
        MainWindow.setTabOrder(self.projLineEdit, self.projButton)
        MainWindow.setTabOrder(self.projButton, self.startStatusRadioButton)
        MainWindow.setTabOrder(self.startStatusRadioButton, self.pauseStatusRadioButton)
        MainWindow.setTabOrder(self.pauseStatusRadioButton, self.prioritySpinBox)
        MainWindow.setTabOrder(self.prioritySpinBox, self.timeoutSpinbox)
        MainWindow.setTabOrder(self.timeoutSpinbox, self.executableComboBox)
        MainWindow.setTabOrder(self.executableComboBox, self.cmdLineEdit)
        MainWindow.setTabOrder(self.cmdLineEdit, self.maxNodesP1SpinBox)
        MainWindow.setTabOrder(self.maxNodesP1SpinBox, self.maxNodesP2SpinBox)
        MainWindow.setTabOrder(self.maxNodesP2SpinBox, self.submitButton)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Submitter Main", None))
        self.niceNameLabel.setText(_translate("MainWindow", "Job Name:", None))
        self.niceNameLineEdit.setPlaceholderText(_translate("MainWindow", "Name for the Job", None))
        self.projectNameLabel.setText(_translate("MainWindow", "Project Name:", None))
        self.projectNameLineEdit.setPlaceholderText(_translate("MainWindow", "Project Name (For Organization in FarmView)", None))
        self.renderLayersLabel.setText(_translate("MainWindow", "Render Layers:", None))
        self.renderLayersLineEdit.setPlaceholderText(_translate("MainWindow", "Render,Layers,Seperated,With,Commas", None))
        self.startFrameLabel.setText(_translate("MainWindow", "FrameRange:", None))
        self.label.setText(_translate("MainWindow", " By Frame(Test): ", None))
        self.sepLabel.setText(_translate("MainWindow", " - ", None))
        self.phasesLabel.setText(_translate("MainWindow", "Phases:", None))
        self.testCheckBox.setText(_translate("MainWindow", "Test Phase", None))
        self.finalCheckBox.setText(_translate("MainWindow", "Final Phase", None))
        self.jobTypeLabel.setText(_translate("MainWindow", "Job Type:", None))
        self.requirementsLabel.setText(_translate("MainWindow", "Requirements:", None))
        self.taskStyleLabel.setText(_translate("MainWindow", "Task Style:", None))
        self.multiTaskRadio.setText(_translate("MainWindow", "Multi Task", None))
        self.singleTaskRadio.setText(_translate("MainWindow", "Single Task", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.standardTab), _translate("MainWindow", "Standard", None))
        self.sceneLabel.setText(_translate("MainWindow", "Scene:", None))
        self.sceneButton.setText(_translate("MainWindow", "Browse", None))
        self.sceneLineEdit.setPlaceholderText(_translate("MainWindow", "Scene File", None))
        self.projLabel.setText(_translate("MainWindow", "Maya Proj:", None))
        self.projButton.setText(_translate("MainWindow", "Browse", None))
        self.projLineEdit.setPlaceholderText(_translate("MainWindow", "Project Directory", None))
        self.startStatusLabel.setText(_translate("MainWindow", "Start Status:", None))
        self.startStatusRadioButton.setText(_translate("MainWindow", "Ready", None))
        self.pauseStatusRadioButton.setText(_translate("MainWindow", "Paused", None))
        self.priorityLabel.setText(_translate("MainWindow", "Priority:", None))
        self.executableLabel.setText(_translate("MainWindow", "Executable:", None))
        self.cmdLabel.setText(_translate("MainWindow", "CMD:", None))
        self.cmdLineEdit.setPlaceholderText(_translate("MainWindow", "Anything entered here will be included in the CMD", None))
        self.maxNodesP1Label.setText(_translate("MainWindow", "Phase 01:", None))
        self.maxNodesP2Label.setText(_translate("MainWindow", "Phase 02:", None))
        self.testNodesLabel.setText(_translate("MainWindow", "Max Nodes:", None))
        self.timeoutLabel.setText(_translate("MainWindow", "Timeout:", None))
        self.frameDirLabel.setText(_translate("MainWindow", "Frame Dir:", None))
        self.frameDirLineEdit.setPlaceholderText(_translate("MainWindow", "Frame Directory", None))
        self.frameDirButton.setText(_translate("MainWindow", "Browse", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.advancedTab), _translate("MainWindow", "Advanced", None))
        self.submitButton.setText(_translate("MainWindow", "Submit", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

