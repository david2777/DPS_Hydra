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
        MainWindow.resize(448, 298)
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
        self.tab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayout = QtGui.QFormLayout(self.tab)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setMargin(6)
        self.formLayout.setHorizontalSpacing(6)
        self.formLayout.setVerticalSpacing(8)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.niceNameLabel = QtGui.QLabel(self.tab)
        self.niceNameLabel.setObjectName(_fromUtf8("niceNameLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.niceNameLabel)
        self.niceNameLineEdit = QtGui.QLineEdit(self.tab)
        self.niceNameLineEdit.setText(_fromUtf8(""))
        self.niceNameLineEdit.setObjectName(_fromUtf8("niceNameLineEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.niceNameLineEdit)
        self.renderLayersLabel = QtGui.QLabel(self.tab)
        self.renderLayersLabel.setObjectName(_fromUtf8("renderLayersLabel"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.renderLayersLabel)
        self.renderLayersLineEdit = QtGui.QLineEdit(self.tab)
        self.renderLayersLineEdit.setObjectName(_fromUtf8("renderLayersLineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.renderLayersLineEdit)
        self.line_2 = QtGui.QFrame(self.tab)
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.SpanningRole, self.line_2)
        self.startFrameLabel = QtGui.QLabel(self.tab)
        self.startFrameLabel.setObjectName(_fromUtf8("startFrameLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.startFrameLabel)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 3, 1, 1)
        self.startSpinBox = QtGui.QSpinBox(self.tab)
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
        self.sepLabel = QtGui.QLabel(self.tab)
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
        self.testFramesSpinBox = QtGui.QSpinBox(self.tab)
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
        self.endSpinBox = QtGui.QSpinBox(self.tab)
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
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.gridLayout)
        self.line_6 = QtGui.QFrame(self.tab)
        self.line_6.setFrameShape(QtGui.QFrame.HLine)
        self.line_6.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_6.setObjectName(_fromUtf8("line_6"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.SpanningRole, self.line_6)
        self.phasesLabel = QtGui.QLabel(self.tab)
        self.phasesLabel.setObjectName(_fromUtf8("phasesLabel"))
        self.formLayout.setWidget(5, QtGui.QFormLayout.LabelRole, self.phasesLabel)
        self.phaseLayout = QtGui.QHBoxLayout()
        self.phaseLayout.setObjectName(_fromUtf8("phaseLayout"))
        self.testCheckBox = QtGui.QCheckBox(self.tab)
        self.testCheckBox.setChecked(True)
        self.testCheckBox.setObjectName(_fromUtf8("testCheckBox"))
        self.phaseLayout.addWidget(self.testCheckBox)
        self.finalCheckBox = QtGui.QCheckBox(self.tab)
        self.finalCheckBox.setChecked(True)
        self.finalCheckBox.setObjectName(_fromUtf8("finalCheckBox"))
        self.phaseLayout.addWidget(self.finalCheckBox)
        self.autocompCheckBox = QtGui.QCheckBox(self.tab)
        self.autocompCheckBox.setEnabled(False)
        self.autocompCheckBox.setObjectName(_fromUtf8("autocompCheckBox"))
        self.phaseLayout.addWidget(self.autocompCheckBox)
        self.legoLayersCheckBox = QtGui.QCheckBox(self.tab)
        self.legoLayersCheckBox.setEnabled(False)
        self.legoLayersCheckBox.setObjectName(_fromUtf8("legoLayersCheckBox"))
        self.phaseLayout.addWidget(self.legoLayersCheckBox)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.phaseLayout)
        self.line_3 = QtGui.QFrame(self.tab)
        self.line_3.setLineWidth(2)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.SpanningRole, self.line_3)
        self.requirementsLabel = QtGui.QLabel(self.tab)
        self.requirementsLabel.setObjectName(_fromUtf8("requirementsLabel"))
        self.formLayout.setWidget(7, QtGui.QFormLayout.LabelRole, self.requirementsLabel)
        self.reqsGrid = QtGui.QGridLayout()
        self.reqsGrid.setObjectName(_fromUtf8("reqsGrid"))
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.reqsGrid)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.formLayout_2 = QtGui.QFormLayout(self.tab_2)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.sceneLabel = QtGui.QLabel(self.tab_2)
        self.sceneLabel.setObjectName(_fromUtf8("sceneLabel"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.sceneLabel)
        self.sceneLayout = QtGui.QGridLayout()
        self.sceneLayout.setObjectName(_fromUtf8("sceneLayout"))
        self.sceneButton = QtGui.QPushButton(self.tab_2)
        self.sceneButton.setObjectName(_fromUtf8("sceneButton"))
        self.sceneLayout.addWidget(self.sceneButton, 0, 1, 1, 1)
        self.sceneLineEdit = QtGui.QLineEdit(self.tab_2)
        self.sceneLineEdit.setObjectName(_fromUtf8("sceneLineEdit"))
        self.sceneLayout.addWidget(self.sceneLineEdit, 0, 0, 1, 1)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.FieldRole, self.sceneLayout)
        self.projLabel = QtGui.QLabel(self.tab_2)
        self.projLabel.setObjectName(_fromUtf8("projLabel"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.projLabel)
        self.mayaProjLayout = QtGui.QGridLayout()
        self.mayaProjLayout.setObjectName(_fromUtf8("mayaProjLayout"))
        self.projButton = QtGui.QPushButton(self.tab_2)
        self.projButton.setObjectName(_fromUtf8("projButton"))
        self.mayaProjLayout.addWidget(self.projButton, 0, 1, 1, 1)
        self.projLineEdit = QtGui.QLineEdit(self.tab_2)
        self.projLineEdit.setReadOnly(True)
        self.projLineEdit.setObjectName(_fromUtf8("projLineEdit"))
        self.mayaProjLayout.addWidget(self.projLineEdit, 0, 0, 1, 1)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.FieldRole, self.mayaProjLayout)
        self.startStatusLabel_2 = QtGui.QLabel(self.tab_2)
        self.startStatusLabel_2.setObjectName(_fromUtf8("startStatusLabel_2"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.startStatusLabel_2)
        self.startStatusLayout = QtGui.QHBoxLayout()
        self.startStatusLayout.setObjectName(_fromUtf8("startStatusLayout"))
        self.startStatusRadioButton = QtGui.QRadioButton(self.tab_2)
        self.startStatusRadioButton.setChecked(True)
        self.startStatusRadioButton.setObjectName(_fromUtf8("startStatusRadioButton"))
        self.startStatusLayout.addWidget(self.startStatusRadioButton)
        self.startStatusLabel = QtGui.QRadioButton(self.tab_2)
        self.startStatusLabel.setObjectName(_fromUtf8("startStatusLabel"))
        self.startStatusLayout.addWidget(self.startStatusLabel)
        self.formLayout_2.setLayout(2, QtGui.QFormLayout.FieldRole, self.startStatusLayout)
        self.line = QtGui.QFrame(self.tab_2)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.SpanningRole, self.line)
        self.priorityLabel = QtGui.QLabel(self.tab_2)
        self.priorityLabel.setObjectName(_fromUtf8("priorityLabel"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.LabelRole, self.priorityLabel)
        self.prioritySpinBox = QtGui.QSpinBox(self.tab_2)
        self.prioritySpinBox.setMinimum(-100)
        self.prioritySpinBox.setMaximum(99999)
        self.prioritySpinBox.setProperty("value", 50)
        self.prioritySpinBox.setObjectName(_fromUtf8("prioritySpinBox"))
        self.formLayout_2.setWidget(5, QtGui.QFormLayout.FieldRole, self.prioritySpinBox)
        self.executableLabel = QtGui.QLabel(self.tab_2)
        self.executableLabel.setObjectName(_fromUtf8("executableLabel"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.LabelRole, self.executableLabel)
        self.executableComboBox = QtGui.QComboBox(self.tab_2)
        self.executableComboBox.setObjectName(_fromUtf8("executableComboBox"))
        self.formLayout_2.setWidget(7, QtGui.QFormLayout.FieldRole, self.executableComboBox)
        self.cmdLabel = QtGui.QLabel(self.tab_2)
        self.cmdLabel.setObjectName(_fromUtf8("cmdLabel"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.LabelRole, self.cmdLabel)
        self.cmdLineEdit = QtGui.QLineEdit(self.tab_2)
        self.cmdLineEdit.setText(_fromUtf8(""))
        self.cmdLineEdit.setObjectName(_fromUtf8("cmdLineEdit"))
        self.formLayout_2.setWidget(8, QtGui.QFormLayout.FieldRole, self.cmdLineEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.testNodesP1Label = QtGui.QLabel(self.tab_2)
        self.testNodesP1Label.setObjectName(_fromUtf8("testNodesP1Label"))
        self.horizontalLayout.addWidget(self.testNodesP1Label)
        self.testNodesP1SpinBox = QtGui.QSpinBox(self.tab_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.testNodesP1SpinBox.sizePolicy().hasHeightForWidth())
        self.testNodesP1SpinBox.setSizePolicy(sizePolicy)
        self.testNodesP1SpinBox.setMaximum(500)
        self.testNodesP1SpinBox.setProperty("value", 1)
        self.testNodesP1SpinBox.setObjectName(_fromUtf8("testNodesP1SpinBox"))
        self.horizontalLayout.addWidget(self.testNodesP1SpinBox)
        self.testNodesP2Label = QtGui.QLabel(self.tab_2)
        self.testNodesP2Label.setObjectName(_fromUtf8("testNodesP2Label"))
        self.horizontalLayout.addWidget(self.testNodesP2Label)
        self.testNodesP2SpinBox = QtGui.QSpinBox(self.tab_2)
        self.testNodesP2SpinBox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.testNodesP2SpinBox.sizePolicy().hasHeightForWidth())
        self.testNodesP2SpinBox.setSizePolicy(sizePolicy)
        self.testNodesP2SpinBox.setMaximum(500)
        self.testNodesP2SpinBox.setProperty("value", 0)
        self.testNodesP2SpinBox.setObjectName(_fromUtf8("testNodesP2SpinBox"))
        self.horizontalLayout.addWidget(self.testNodesP2SpinBox)
        self.formLayout_2.setLayout(9, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.testNodesLabel = QtGui.QLabel(self.tab_2)
        self.testNodesLabel.setObjectName(_fromUtf8("testNodesLabel"))
        self.formLayout_2.setWidget(9, QtGui.QFormLayout.LabelRole, self.testNodesLabel)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
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

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Submitter Main", None))
        self.niceNameLabel.setText(_translate("MainWindow", "Job Name:", None))
        self.niceNameLineEdit.setPlaceholderText(_translate("MainWindow", "Nice Name for the Job", None))
        self.renderLayersLabel.setText(_translate("MainWindow", "Render Layers:", None))
        self.renderLayersLineEdit.setPlaceholderText(_translate("MainWindow", "Render,Layers,Seperated,With,Commas", None))
        self.startFrameLabel.setText(_translate("MainWindow", "FrameRange:", None))
        self.label.setText(_translate("MainWindow", " By Frame(Test): ", None))
        self.sepLabel.setText(_translate("MainWindow", " - ", None))
        self.phasesLabel.setText(_translate("MainWindow", "Phases:", None))
        self.testCheckBox.setText(_translate("MainWindow", "Test Phase", None))
        self.finalCheckBox.setText(_translate("MainWindow", "Final Phase", None))
        self.autocompCheckBox.setText(_translate("MainWindow", "Auto Comp", None))
        self.legoLayersCheckBox.setText(_translate("MainWindow", "LEGO Layers", None))
        self.requirementsLabel.setText(_translate("MainWindow", "Requirements:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Standard", None))
        self.sceneLabel.setText(_translate("MainWindow", "Scene:", None))
        self.sceneButton.setText(_translate("MainWindow", "Browse", None))
        self.sceneLineEdit.setPlaceholderText(_translate("MainWindow", "Scene File", None))
        self.projLabel.setText(_translate("MainWindow", "Maya Proj:", None))
        self.projButton.setText(_translate("MainWindow", "Browse", None))
        self.projLineEdit.setPlaceholderText(_translate("MainWindow", "Project Directory", None))
        self.startStatusLabel_2.setText(_translate("MainWindow", "Start Status:", None))
        self.startStatusRadioButton.setText(_translate("MainWindow", "Ready", None))
        self.startStatusLabel.setText(_translate("MainWindow", "Paused", None))
        self.priorityLabel.setText(_translate("MainWindow", "Priority:", None))
        self.executableLabel.setText(_translate("MainWindow", "Executable:", None))
        self.cmdLabel.setText(_translate("MainWindow", "CMD:", None))
        self.cmdLineEdit.setPlaceholderText(_translate("MainWindow", "Anything entered here will be included in the CMD", None))
        self.testNodesP1Label.setText(_translate("MainWindow", "Phase 01:", None))
        self.testNodesP2Label.setText(_translate("MainWindow", "Phase 02:", None))
        self.testNodesLabel.setText(_translate("MainWindow", "Test Nodes:", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Advanced", None))
        self.submitButton.setText(_translate("MainWindow", "Submit", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

