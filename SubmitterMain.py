"""The software used for submitting jobs to the DB. Gather data, creates and
submits job tickets to the database."""
#Standard
import sys
import os
import getopt

#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from CompiledUI.UI_Submitter import Ui_MainWindow

#Hydra
import Constants
from Setups.MySQLSetup import db_username, hydra_capabilities, hydra_executable
from Setups.LoggingSetup import logger
from Dialogs.MessageBoxes import aboutBox, yesNoBox
from Setups.JobTicket import UberJobTicket
import Utilities.JobUtils as JobUtils

class SubmitterMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        #Built-in UI Setup
        self.setupUi(self)

        #Setup the UI with my fuctions
        self.setupGlobals()
        self.hookupButtons()
        self.populateReqs()
        self.populateExecs()
        self.setupForms()

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)

    #------------------------------------------------------------------------#
    #---------------------------UI Setup Functions---------------------------#
    #------------------------------------------------------------------------#

    def setupGlobals(self):
        #Scene file should be first sys.argv
        try:
            self.scene = sys.argv[1]
            self.scene = self.scene.replace('\\', '/')
        except IndexError:
            self.scene = ""

        #Get the -flag args
        try:
            opts = getopt.getopt(sys.argv[2:],"s:e:n:p:r:x:m:c:q:")[0]
        except getopt.GetoptError:
            logger.error("Bad Opt!")
            aboutBox(self, title = "Bad Opt!", msg = "One of the command line options you entered was invalid.\n"+
                "\nPlease remove any unkown opts and try again.")
            sys.exit(2)

        #Defaults
        defName = self.scene.split("/")[-1]
        self.settingsDict = {"-s":101,      #Start Frame (Int)
                            "-e":101,       #End Frame (Int)
                            "-n":defName,   #Nice Name (Str)
                            "-p":"",        #Proj (Str)
                            "-r":"",        #Render Layers (Str,Sep,By,Comma)
                            "-x":"",        #Executabe (Str)
                            "-m":"",        #CMD (Str)
                            "-c":"",        #Compatabilities (Str,Sep,By,Comma)
                            "-q":"",        #Project Name (Str)
                            }

        #Apply the -flag args
        opts = dict(opts)
        keys = list(opts.keys())
        for key in keys:
            self.settingsDict[key] = opts[key]
            logger.info("Setting Key '{0}' with opt: '{1}'".format(key, str(opts[key])))

        #Fix paths
        self.settingsDict["-p"] = self.settingsDict["-p"].replace('\\', '/')
        #Fix Compatabilities
        self.settingsDict["-c"] = self.settingsDict["-c"].split(",")
        #Add underscores to niceName
        self.settingsDict["-n"] = self.settingsDict["-n"].replace(" ", "_")

    def hookupButtons(self):
            QObject.connect(self.submitButton, SIGNAL("clicked()"),
                            self.submitButtonHandler)
            QObject.connect(self.testCheckBox, SIGNAL("stateChanged(int)"),
                            self.toggleTestBoxes)
            QObject.connect(self.finalCheckBox, SIGNAL("stateChanged(int)"),
                            self.toggleFinalBoxes)
            QObject.connect(self.sceneButton, SIGNAL("clicked()"),
                            self.sceneButtonHandler)
            QObject.connect(self.projButton, SIGNAL("clicked()"),
                            self.projButtonHandler)

    def populateReqs(self):
        #Get requirements master list from the DB
        #Hardcoded for now
        requirements = hydra_capabilities.fetch()
        requirements = [req.name for req in requirements]
        self.reqChecks = []
        col = 0
        row = 0
        for item in requirements:
            c = QCheckBox(item)
            self.reqsGrid.addWidget(c, row, col)
            if col == 2:
                row += 1
                col = 0
            else:
                col += 1

            #Set args passed from Maya to the Reqs
            if item in self.settingsDict["-c"]:
                c.setCheckState(2)

            self.reqChecks.append(c)

    def populateExecs(self):
        #Get execs
        #Stored in Constants for now
        execs = hydra_executable.fetch()
        execs.reverse()

        for execute in execs:
            newItem = self.executableComboBox.addItem(execute.name)

        #Set the executeable to the value passed from Maya
        index = self.executableComboBox.findText(self.settingsDict["-x"])
        if index > 0:
            self.executableComboBox.setCurrentIndex(index)

    def setupForms(self):
        self.sceneLineEdit.setText(self.scene)
        self.projLineEdit.setText(self.settingsDict["-p"])
        self.niceNameLineEdit.setText(self.settingsDict["-n"])
        self.startSpinBox.setValue(int(float(self.settingsDict["-s"])))
        self.endSpinBox.setValue(int(float(self.settingsDict["-e"])))
        self.renderLayersLineEdit.setText(self.settingsDict["-r"])
        self.cmdLineEdit.setText(self.settingsDict["-m"])
        self.projectNameLineEdit.setText(self.settingsDict["-q"])

    #------------------------------------------------------------------------#
    #----------------------------Button Handlers-----------------------------#
    #------------------------------------------------------------------------#

    def submitButtonHandler(self):
        #TODO:Error check this data!
        #Getting data in same order as JobTicket
        execName = str(self.executableComboBox.currentText())
        baseCMD = str(self.cmdLineEdit.text())
        startFrame = int(self.startSpinBox.value())
        endFrame = int(self.endSpinBox.value())
        byFrame = int(self.testFramesSpinBox.value())
        taskFile = str(self.sceneLineEdit.text())
        priority = int(self.prioritySpinBox.value())
        phase = 0 #Placeholder, set this later when building the commands
        jobStatus = self.getJobStatus()
        niceName = str(self.niceNameLineEdit.text())
        owner = db_username
        compatabilityList = self.getReqs()
        maxNodesP1 = int(self.maxNodesP1SpinBox.value())
        maxNodesP2 = int(self.maxNodesP2SpinBox.value())
        timeout = int(self.timeoutSpinbox.value())
        projectName = str(self.projectNameLineEdit.text())

        #Stuff not in JobTicket
        renderLayers = str(self.renderLayersLineEdit.text()).replace(" ", "")
        if renderLayers != "":
            baseCMD += " -rl {0}".format(renderLayers)

        proj = str(self.projLineEdit.text())
        if len(proj) < 5:
            aboutBox(self, title = "Please set Project Directory!", msg = "Project Directory must be more than 5 characters long.")
            logger.error("Please set Project Directory! Project Directory must be more than 5 characters long.")
            return
        else:
            baseCMD += " -proj {0}".format(proj)

        #Error Checking
        if len(baseCMD) > 1000:
            aboutBox(self, title = "baseCMD too long!", msg = "baseCMD must be less than 1000 characters!")
            logger.error("baseCMD too long! baseCMD must be less than 1000 characters!")
            return
        if startFrame > endFrame:
            aboutBox(self, title = "startFrame is greater than endFrame!", msg = "startFrame must be less than the endFrame!")
            logger.error("startFrame is greater than endFrame!")
            return
        if startFrame > 65535 or endFrame > 65535 or startFrame < 0 or endFrame < 0:
            aboutBox(self, title = "Frame range out of range!", msg = "Start/End frames must be between 0 and 65535!")
            logger.error("Frame range out of range! Start/End frames must be between 0 and 65535!")
            return
        if byFrame > 255 or byFrame < 0:
            aboutBox(self, title = "byFrame out of range!", msg = "byFrame must be between 0 and 255!")
            logger.error("byFrame out of range! byFrame must be between 0 and 255!")
            return
        if len(taskFile) > 255 or len(taskFile) < 5:
            aboutBox(self, title = "taskFile out of range!", msg = "taskFile must be greater than 5 and less than 255 characters")
            logger.error("taskFile out of range! taskFile path must be greater than 5 and less than 255 characters!")
            return
        if priority > 255 or priority < 0:
            aboutBox(self, title = "Priority out of range!", msg = "Priority must be between 0 and 255!")
            logger.error("Priority out of range! Priority must be between 0 and 255!")
            return
        if len(niceName) > 60 or len(niceName) < 1:
            aboutBox(self, title = "NiceName out of range!", msg = "NiceName must be more than 1 and less than 60 characters!")
            logger.error("NiceName out of range! NiceName must be more than 1 and less than 60 characters!")
            return
        if len(owner) > 45:
            aboutBox(self, title = "Owner out of range!", msg = "Owner must be less than 45 characters!")
            logger.error("Owner out of range! Owner must be less than 45 characters!")
            return
        if len(projectName) > 60:
            aboutBox(self, title = "Project Name out of range!", msg = "Project name must be less than 60 characters!")
            return

        if projectName == "":
            projectName = "UnkownProject"

        phase01Status = False
        if self.testCheckBox.isChecked():
            logger.info("Building Phase 01")
            #Phase specific overrides
            phase = 1
            niceNameOverride = "{0}_Test".format(niceName)
            baseCMDOverride = baseCMD + " -x 640 -y 360"
            priorityOverride = int(priority * 1.25)
            phase01Ticket = UberJobTicket(execName,
                                            baseCMDOverride,
                                            startFrame,
                                            endFrame,
                                            byFrame,
                                            taskFile,
                                            priorityOverride,
                                            phase,
                                            jobStatus,
                                            niceNameOverride,
                                            owner,
                                            compatabilityList,
                                            maxNodesP1,
                                            timeout,
                                            projectName)

            p1_job_id = phase01Ticket.doSubmit()
            if jobStatus == "R":
                JobUtils.setupNodeLimit(p1_job_id)
            logger.info("Phase 01 submitted with id: {0}".format(p1_job_id))
            phase01Status = True

        if self.finalCheckBox.isChecked():
            logger.info("Building Phase 02")
            #Phase specific overrides
            phase = 2
            niceNameOverride = "{0}_Final".format(niceName)
            byFrameOverride = 1
            if phase01Status:
                jobStatusOverride = "U"
            else:
                jobStatusOverride = jobStatus
            phase02Ticket = UberJobTicket(execName,
                                            baseCMD,
                                            startFrame,
                                            endFrame,
                                            byFrameOverride,
                                            taskFile,
                                            priority,
                                            phase,
                                            jobStatusOverride,
                                            niceNameOverride,
                                            owner,
                                            compatabilityList,
                                            maxNodesP2,
                                            timeout,
                                            projectName)

            p2_job_id = phase02Ticket.doSubmit()
            if jobStatusOverride == "R":
                JobUtils.setupNodeLimit(p2_job_id)
            logger.info("Phase 02 submitted with id: {0}".format(p2_job_id))

        self.submitButton.setEnabled(False)
        self.submitButton.setText("Job Submitted! Please close window.")
        #aboutBox(self, title = "Submitted!", msg = "Job and Tasks have been submitted!\nCheck FarmView to view the status of your Jobs!")

    def browseFileButtonHandler(self, QTTarget, startDir, caption, fileFilter):
        returnDir = QFileDialog.getOpenFileName(
            parent = self,
            caption = caption,
            directory = startDir,
            filter = fileFilter)
        if returnDir:
            if fileFilter == "workspace.mel;;All Files(*)":
                # remove "workspace.mel" from the end of the path
                returnDir = str(returnDir).split('/')
                returnDir.pop()
                returnDir = '/'.join(returnDir) + '/'

            QTTarget.setText(returnDir)
            return returnDir

        else:
            return False

    def sceneButtonHandler(self):
        currentDir = str(self.sceneLineEdit.text())
        startDir = None
        if len(currentDir) == 0:
            projDir = str(self.projLineEdit.text())
            if len(projDir) == 0:
                startDir = os.getcwd()
            else:
                startDir = projDir
        else:
            startDir = currentDir

        sceneFile = self.browseFileButtonHandler(self.sceneLineEdit,
                                                startDir,
                                                "Find maya scene file...",
                                                "Maya Files (*.ma *.mb);;All Files(*)")
        if sceneFile and str(self.niceNameLineEdit.text()) == "":
            defName = sceneFile.split("/")[-1]
            self.niceNameLineEdit.setText(defName)

    def projButtonHandler(self):
        currentDir = str(self.projLineEdit.text())
        startDir = None
        if len(currentDir) == 0:
            sceneDir = str(self.sceneLineEdit.text())
            if len(sceneDir) == 0:
                startDir = os.getcwd()
            else:
                sceneDir = str(sceneDir).split('/')
                sceneDir.pop()
                sceneDir.pop()
                sceneDir = '/'.join(sceneDir) + '/'
                startDir = sceneDir
        else:
            startDir = currentDir
        self.browseFileButtonHandler(self.projLineEdit,
                                    startDir,
                                    "Find maya workspace.mel in project directory...",
                                    "workspace.mel;;All Files(*)")

    def toggleTestBoxes(self):
        if self.testFramesSpinBox.isEnabled():
            self.testFramesSpinBox.setEnabled(False)
            self.maxNodesP1SpinBox.setEnabled(False)
        else:
            self.testFramesSpinBox.setEnabled(True)
            self.maxNodesP1SpinBox.setEnabled(True)

    def toggleFinalBoxes(self):
        if self.maxNodesP2SpinBox.isEnabled():
            self.maxNodesP2SpinBox.setEnabled(False)
        else:
            self.maxNodesP2SpinBox.setEnabled(True)
    #------------------------------------------------------------------------#
    #----------------------------Get/Modify Data-----------------------------#
    #------------------------------------------------------------------------#

    def getReqs(self):
        reqList = []
        for check in self.reqChecks:
            if check.isChecked():
                reqList.append(str(check.text()))

        #Job Ticket takes a list and sorts and formats it
        return reqList

    def getJobStatus(self):
        if self.startStatusRadioButton.isChecked():
            return "R"
        else:
            return "U"

if __name__ == '__main__':
    try:
        sys.argv[1]
    except IndexError:
        sys.argv.append("")

    app = QApplication(sys.argv)

    window = SubmitterMain()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
