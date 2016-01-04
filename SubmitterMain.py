#Standard
import sys
import os
import getopt

#QT
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#HydraQT
from UI_Submitter import Ui_MainWindow

#Hydra
from MySQLSetup import db_username
from LoggingSetup import logger
from MessageBoxes import aboutBox, yesNoBox
from JobTicket import UberJobTicket
import JobUtils
import Constants


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
            opts = getopt.getopt(sys.argv[2:],"s:e:n:p:r:x:m:c:")[0]
        except getopt.GetoptError:
            logger.error("Bad Opt!")
            aboutBox(title = "Bad Opt!", msg = "One of the command line options you entered was invalid.\n"+
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
                            }

        #Apply the -flag args
        opts = dict(opts)
        keys = list(opts.keys())
        for key in keys:
            self.settingsDict[key] = opts[key]
            logger.debug("Setting Key '%s' with opt: %s" % (key, str(opts[key])))

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
        requirements = ["Redshift", "VRay", "MentalRay", "Photoshop", "RenderMan", "SOuP", "Houdini", "Fusion"]
        requirements.sort()
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
        execsDict = Constants.EXECUTEABLES
        execs = list(execsDict.keys())
        execs.sort()
        execs.reverse()

        for name in execs:
            newItem = self.executableComboBox.addItem(name)
            
        #Set the executeable to the value passed from Maya
        index = self.executableComboBox.findText(self.settingsDict["-x"])
        if index > 0:
            self.executableComboBox.setCurrentIndex(index)

    def setupForms(self):
        self.sceneLineEdit.setText(self.scene)
        self.projLineEdit.setText(self.settingsDict["-p"])
        self.niceNameLineEdit.setText(self.settingsDict["-n"])
        self.startSpinBox.setValue(int(self.settingsDict["-s"]))
        self.endSpinBox.setValue(int(self.settingsDict["-e"]))
        self.renderLayersLineEdit.setText(self.settingsDict["-r"])
        self.cmdLineEdit.setText(self.settingsDict["-m"])

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
        testNodesP1 = int(self.testNodesP1SpinBox.value())
        testNodesP2 = int(self.testNodesP2SpinBox.value())
        
        renderLayers = str(self.renderLayersLineEdit.text()).replace(" ", "")
        if renderLayers != "":
            baseCMD += " -rl %s" % renderLayers
        
        
        if self.testCheckBox.isChecked():
            logger.info("Building Phase 01")
            #Phase specific overrides
            phase = 1
            niceNameOverride = "%s_Phase01" % niceName
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
                                            testNodesP1)
        
            p1_job_id = phase01Ticket.doSubmit()
            if jobStatus == "R":
                JobUtils.setupNodeLimit(p1_job_id)
            logger.info("Phase 01 submitted with id: %d" % p1_job_id)
            phase01Status = True
            
        if self.finalCheckBox.isChecked():
            logger.info("Building Phase 02")
            #Phase specific overrides
            phase = 2
            niceNameOverride = "%s_Phase02" % niceName
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
                                            testNodesP2)
        
            p2_job_id = phase02Ticket.doSubmit()
            if jobStatusOverride == "R":
                JobUtils.setupNodeLimit(p2_job_id)
            logger.info("Phase 02 submitted with id: %d" % p2_job_id)
        
        self.submitButton.setEnabled(False)
        self.submitButton.setText("Job Submitted! Please close window.")    
        #aboutBox(title = "Submitted!", msg = "Job and Tasks have been submitted!\nCheck FarmView to view the status of your Jobs!")
    
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
            self.testNodesP1SpinBox.setEnabled(False)
        else:
            self.testFramesSpinBox.setEnabled(True)
            self.testNodesP1SpinBox.setEnabled(True)
    
    def toggleFinalBoxes(self):
        if self.testNodesP2SpinBox.isEnabled():
            self.testNodesP2SpinBox.setEnabled(False)
        else:
            self.testNodesP2SpinBox.setEnabled(True)
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
