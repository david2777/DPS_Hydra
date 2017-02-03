"""The software used for submitting jobs to the DB. Gather data, creates and
submits job tickets to the database."""
#Standard
import sys
import os
import getopt

#Third Party
from PyQt4 import QtGui, QtCore

#Hydra Qt
from compiled_qt.UI_Submitter import Ui_MainWindow

#Hydra
import hydra.hydra_sql as sql
from hydra.logging_setup import logger
from dialogs_qt.MessageBoxes import aboutBox
from utils.hydra_utils import findResource

#pylint: disable=E1101

class SubmitterMain(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        #Built-in UI Setup
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(findResource("assets/SubmitterMain.png")))

        #Setup the UI with my fuctions
        self.setup_globals()
        self.hookup_buttons()
        self.populate_reqs()
        self.populate_execs()
        self.populate_job_types()
        self.setup_forms()

    @staticmethod
    def closeEvent(event):
        event.accept()
        sys.exit(0)

    #------------------------------------------------------------------------#
    #---------------------------UI Setup Functions---------------------------#
    #------------------------------------------------------------------------#

    def setup_globals(self):
        #Scene file should be first sys.argv
        try:
            self.scene = sys.argv[1]
            self.scene = self.scene.replace('\\', '/')
        except IndexError:
            self.scene = ""

        #Get the -flag args
        try:
            opts = getopt.getopt(sys.argv[2:], "s:e:n:p:l:x:m:d:c:q:t:")[0]
        except getopt.GetoptError:
            logger.error("Bad Opt!")
            aboutBox(self, "Bad Opt!", "One of the command line options you entered was invalid.\n"+
                "\nPlease remove any unkown opts and try again.")
            sys.exit(2)

        #Defaults
        defName = self.scene.split("/")[-1]
        self.settingsDict = {"-s":101,      #Start Frame (Int)
                            "-e":101,       #End Frame (Int)
                            "-n":defName,   #Nice Name (Str)
                            "-p":"",        #Proj (Str)
                            "-l":"",        #Render Layers (Str,Sep,By,Comma)
                            "-x":"",        #Executabe (Str)
                            "-m":"",        #CMD (Str)
                            "-d":"",        #RenderDirectory (Str)
                            "-c":"",        #Compatabilities (Str,Sep,By,Comma)
                            "-q":"",        #Project Name (Str)
                            "-t":"",        #Job Type (Str)
                            }

        #Apply the -flag args
        optsDict = dict(opts)
        keys = list(optsDict.keys())
        for key in keys:
            self.settingsDict[key] = optsDict[key]
            logger.debug("Setting Key '%s' with opt: '%s'", key, str(optsDict[key]))

        #Fix paths
        self.settingsDict["-p"] = self.settingsDict["-p"].replace('\\', '/')
        self.settingsDict["-d"] = self.settingsDict["-d"].replace('\\', '/')
        #Fix Compatabilities
        self.settingsDict["-c"] = self.settingsDict["-c"].split(",")
        #Add underscores to niceName
        self.settingsDict["-n"] = self.settingsDict["-n"].replace(" ", "_")

    def hookup_buttons(self):
        self.submitButton.clicked.connect(self.submit_button_handler)
        self.testCheckBox.stateChanged.connect(self.toggle_test_boxes)
        self.finalCheckBox.stateChanged.connect(self.toggle_final_boxes)
        self.sceneButton.clicked.connect(self.scene_button_handler)
        self.projButton.clicked.connect(self.proj_button_handler)
        self.frameDirButton.clicked.connect(self.frame_dir_button_handler)
        self.jobTypeComboBox.currentIndexChanged.connect(self.job_type_switcher)

    def populate_reqs(self):
        #Get requirements master list from the DB
        requirements = sql.hydra_capabilities.fetch(multiReturn=True)
        requirements = [req.name for req in requirements]
        self.reqChecks = []
        col = 0
        row = 0
        for item in requirements:
            c = QtGui.QCheckBox(item)
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

    def populate_execs(self):
        #Get execs
        execs = sql.hydra_executable.fetch(multiReturn=True, cols=["name"])
        execs.reverse()

        for execute in execs:
            self.executableComboBox.addItem(execute.name)

        #Set the executeable to the value passed from Maya
        index = self.executableComboBox.findText(self.settingsDict["-x"])
        if index > 0:
            self.executableComboBox.setCurrentIndex(index)

    def populate_job_types(self):
        types = sql.hydra_jobtypes.fetch(multiReturn=True, cols=["type"])
        types.reverse()

        for t in types:
            self.jobTypeComboBox.addItem(t.type)

        index = self.jobTypeComboBox.findText(self.settingsDict["-t"])
        if index > 0:
            self.jobTypeComboBox.setCurrentIndex(index)

    def setup_forms(self):
        self.sceneLineEdit.setText(self.scene)
        self.projLineEdit.setText(self.settingsDict["-p"])
        self.niceNameLineEdit.setText(self.settingsDict["-n"])
        self.startSpinBox.setValue(int(float(self.settingsDict["-s"])))
        self.endSpinBox.setValue(int(float(self.settingsDict["-e"])))
        self.renderLayersLineEdit.setText(self.settingsDict["-l"])
        self.cmdLineEdit.setText(self.settingsDict["-m"])
        self.projectNameLineEdit.setText(self.settingsDict["-q"])
        self.frameDirLineEdit.setText(self.settingsDict["-d"])

    #------------------------------------------------------------------------#
    #----------------------------Button Handlers-----------------------------#
    #------------------------------------------------------------------------#

    def submit_button_handler(self):

        #######################################################################
        #TODO: Rework this to work with multiple job types
        #######################################################################

        #Getting data in same order as JobTicket
        execName = str(self.executableComboBox.currentText())
        baseCMD = str(self.cmdLineEdit.text())
        startFrame = int(self.startSpinBox.value())
        endFrame = int(self.endSpinBox.value())
        byFrame = int(self.testFramesSpinBox.value())
        taskFile = str(self.sceneLineEdit.text())
        priority = int(self.prioritySpinBox.value())
        phase = 0 #Placeholder, set this later when building the commands
        jobStatus = self.get_job_status()
        niceName = str(self.niceNameLineEdit.text())
        owner = sql.transaction().db_username
        compatabilityList = self.get_reqs()
        maxNodesP1 = int(self.maxNodesP1SpinBox.value())
        maxNodesP2 = int(self.maxNodesP2SpinBox.value())
        timeout = int(self.timeoutSpinbox.value())
        projectName = str(self.projectNameLineEdit.text())
        renderLayers = str(self.renderLayersLineEdit.text()).replace(" ", "")
        jobType = str(self.jobTypeComboBox.currentText())
        proj = str(self.projLineEdit.text())
        frameDir = str(self.frameDirLineEdit.text())

        #Error Checking
        if startFrame > endFrame:
            aboutBox(self, "startFrame is greater than endFrame!", "startFrame must be less than the endFrame!")
            logger.error("startFrame is greater than endFrame!")
            return

        if projectName == "":
            projectName = "UnkownProject"

        if jobType not in ["BatchFile", "FusionComp"]:
            baseCMD += " -proj {0}".format(proj)

        phase01Status = False
        if self.testCheckBox.isChecked():
            logger.info("Building Phase 01")
            #Phase specific overrides
            phase = 1
            #This is cool at least for now because anything with a phase one SHOULD be a Maya Job
            baseCMDOverride = baseCMD + " -x 640 -y 360"

            phase01 = submit_job(niceName, projectName, owner, jobStatus,
                                compatabilityList, execName, baseCMDOverride,
                                startFrame, endFrame, byFrame, renderLayers,
                                taskFile, int(priority * 1.25), phase, maxNodesP1,
                                timeout, 10, jobType, frameDir)

            logger.info("Phase 01 submitted with id: %s", phase01.id)

            phase01Status = True

        if self.finalCheckBox.isChecked():
            logger.info("Building Phase 02")
            #Phase specific overrides
            frameRange = range(startFrame, endFrame + 1)
            phase02Frames = frameRange[:10]
            phase03Frames = frameRange[10:]

            if jobType == "FusionComp":
                phase02Frames = frameRange
                phase03Frames = []

            byFrame = 1
            if phase01Status:
                jobStatusOverride = sql.PAUSED
            else:
                jobStatusOverride = jobStatus

            phase = 2
            phase02 = submit_job(niceName, projectName, owner, jobStatusOverride,
                                compatabilityList, execName, baseCMD, phase02Frames[0],
                                phase02Frames[-1], byFrame, renderLayers, taskFile, priority,
                                phase, maxNodesP2, timeout, 10, jobType, frameDir)

            logger.info("Phase 02 submitted with id: %s", phase02.id)

            if phase03Frames:
                logger.info("Building Phase 03")
                phase = 3
                phase03 = submit_job(niceName, projectName, owner, sql.PAUSED,
                                    compatabilityList, execName, baseCMD, phase03Frames[0],
                                    phase03Frames[-1], byFrame, renderLayers, taskFile, priority,
                                    phase, maxNodesP2, timeout, 10, jobType, frameDir)

                logger.info("Phase 03 submitted with id: %s", phase03.id)


        self.submitButton.setEnabled(False)
        self.submitButton.setText("Job Submitted! Please close window.")
        #aboutBox(self, "Submitted!", "Your jobs have been submitted!\nCheck FarmView to view the status of your Jobs!")

    def browse_file_button_handler(self, QTTarget, startDir, caption, fileFilter):
        returnDir = QtGui.QFileDialog.getOpenFileName(self, caption, startDir, fileFilter)
        if returnDir:
            returnDir = str(returnDir)
            if returnDir.endswith(".mel"):
                returnDir, _ = os.path.split(returnDir)
            QTTarget.setText(returnDir)
            return returnDir

        else:
            return False

    def browse_directory_button_handler(self, QTTarget, startDir, caption):
        returnDir = QtGui.QFileDialog.getExistingDirectory(self, caption, startDir)
        if returnDir:
            QTTarget.setText(returnDir)
            return returnDir
        else:
            return None

    def scene_button_handler(self):
        currentDir = str(self.sceneLineEdit.text())
        startDir = None
        if not currentDir:
            projDir = str(self.projLineEdit.text())
            if not projDir:
                startDir = os.getcwd()
            else:
                startDir = projDir
        else:
            startDir = currentDir

        sceneFile = self.browse_file_button_handler(self.sceneLineEdit,
                                                startDir,
                                                "Find scene file...",
                                                "All Files(*);;Maya Files (*.ma *.mb);;Batch File (*.bat);;Fusion Comp (*.comp)")
        if sceneFile and str(self.niceNameLineEdit.text()) == "":
            defName = sceneFile.split("/")[-1]
            self.niceNameLineEdit.setText(defName)

    def proj_button_handler(self):
        currentDir = str(self.projLineEdit.text())
        startDir = None
        if not currentDir:
            sceneDir = str(self.sceneLineEdit.text())
            if not sceneDir:
                startDir = os.getcwd()
            else:
                startDir = sceneDir
        else:
            startDir = currentDir
        self.browse_file_button_handler(self.projLineEdit,
                                    startDir,
                                    "Find maya workspace.mel in project directory...",
                                    "workspace.mel;;All Files(*)")

    def frame_dir_button_handler(self):
        currentDir = str(self.frameDirLineEdit.text())
        startDir = None
        if not currentDir:
            projDir = str(self.projLineEdit.text())
            if not projDir:
                startDir = os.getcwd()
            else:
                startDir = projDir
        else:
            startDir = currentDir
        self.browse_directory_button_handler(self.frameDirLineEdit, startDir,
                                    "Select the directory where you want your frames to be rendered...")

    def toggle_test_boxes(self):
        if self.testFramesSpinBox.isEnabled():
            self.testFramesSpinBox.setEnabled(False)
            self.maxNodesP1SpinBox.setEnabled(False)
        else:
            self.testFramesSpinBox.setEnabled(True)
            self.maxNodesP1SpinBox.setEnabled(True)

    def toggle_final_boxes(self):
        if self.maxNodesP2SpinBox.isEnabled():
            self.maxNodesP2SpinBox.setEnabled(False)
        else:
            self.maxNodesP2SpinBox.setEnabled(True)

    def job_type_switcher(self):
        jobType = str(self.jobTypeComboBox.currentText())

        #Re-enable everything
        allWidgets = [self.renderLayersLineEdit, self.startSpinBox, self.endSpinBox,
                        self.testFramesSpinBox, self.testCheckBox, self.finalCheckBox,
                        self.sceneLineEdit, self.sceneButton, self.projLineEdit,
                        self.frameDirLineEdit, self.frameDirButton, self.projButton,
                        self.executableComboBox, self.maxNodesP1SpinBox, self.maxNodesP2SpinBox]

        _ = [x.setEnabled(True) for x in allWidgets]

        #Disable anything we don't want
        batchDisable = [self.renderLayersLineEdit, self.startSpinBox, self.endSpinBox,
                        self.testFramesSpinBox, self.testCheckBox, self.finalCheckBox,
                        self.projLineEdit, self.projButton, self.frameDirLineEdit,
                        self.frameDirButton, self.executableComboBox, self.maxNodesP2SpinBox]

        fusionDisable = [self.renderLayersLineEdit, self.testFramesSpinBox, self.testCheckBox,
                            self.finalCheckBox, self.executableComboBox, self.maxNodesP2SpinBox,
                            self.projLineEdit, self.projButton, self.frameDirLineEdit,
                            self.frameDirButton]

        if jobType == "BatchFile":
            self.testCheckBox.setCheckState(0)
            self.finalCheckBox.setCheckState(2)
            _ = [x.setEnabled(False) for x in batchDisable]
            wildcard = "none"

        elif jobType == "FusionComp":
            self.testCheckBox.setCheckState(0)
            self.finalCheckBox.setCheckState(2)
            _ = [x.setEnabled(False) for x in fusionDisable]
            wildcard = "fusion*"

        elif jobType == "Maya_Render":
            wildcard = "mayaRender_*"

        else:
            wildcard = "qwertyuiop"

        i = self.executableComboBox.findText(wildcard, QtCore.Qt.MatchWildcard)
        if i > 0:
            self.executableComboBox.setCurrentIndex(i)
    #------------------------------------------------------------------------#
    #----------------------------Get/Modify Data-----------------------------#
    #------------------------------------------------------------------------#

    def get_reqs(self):
        reqList = []
        for check in self.reqChecks:
            if check.isChecked():
                reqList.append(str(check.text()))

        return ",".join(sorted(reqList))

    def get_job_status(self):
        if self.startStatusRadioButton.isChecked():
            return "R"
        else:
            return "U"

def submit_job(niceName, projectName, owner, status, requirements, execName,
                baseCMD, startFrame, endFrame, byFrame, renderLayers, taskFile,
                priority, phase, maxNodes, timeout, maxAttempts, jobType, frameDir):
    """A simple function for submitting a job to the jobBoard"""
    niceName = "{0}_PHASE{1:02d}".format(niceName, phase)

    if jobType == "BatchFile":
        renderLayers = "Batch"
        startFrame = 1
        endFrame = 1
        execName = "none"
        maxNodes = 1

    elif jobType == "FusionComp":
        renderLayers = "Fusion"
        execName = "fusion"
        maxNodes = 1

    job = sql.hydra_jobboard(niceName=niceName, projectName=projectName,
                        owner=owner, status=status,
                        requirements=requirements, execName=execName,
                        baseCMD=baseCMD, startFrame=startFrame,
                        endFrame=endFrame, byFrame=byFrame,
                        renderLayers=renderLayers,
                        taskFile=taskFile, priority=priority, maxNodes=maxNodes,
                        timeout=timeout, maxAttempts=maxAttempts, jobType=jobType,
                        frameDirectory=frameDir)

    frameList = range(startFrame, (endFrame + 1))[::byFrame]
    frameList += [endFrame] if endFrame not in frameList else []

    with sql.transaction() as t:
        job.insert(trans=t)
        taskList = [sql.hydra_taskboard(job_id=job.id, status=status, priority=priority,
                                        startFrame=x, endFrame=x) for x in frameList]
        for task in taskList:
            task.insert(trans=t)

    return job

if __name__ == '__main__':
    try:
        sys.argv[1]
    except IndexError:
        sys.argv.append("")

    app = QtGui.QApplication(sys.argv)

    window = SubmitterMain()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
