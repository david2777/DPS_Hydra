#Standard
import sys
import getopt

#QT
from PyQt4.QtGui import *
from PyQt4.QtCore import *
#HydraQT
from UI_Submitter import Ui_MainWindow

#Hydra
from LoggingSetup import logger
from MessageBoxes import aboutBox, yesNoBox
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
            opts = getopt.getopt(sys.argv[2:],"s:e:n:p:r:x:m:c")[0]
        except getopt.GetoptError:
            logger.error("Bad Opt!")
            aboutBox(title = "Bad Opt!", msg = "One of the command line options you entered was invalid.\n"+
                "Valid Opts inlude -s (startFrame) -e (endFrame) -n (niceName) and -p (mayaProject)."+
                "\nPlease remove any unkown opts and try again.")
            sys.exit(2)

        #Defaults
        self.settingsDict = {"-s":101,
                            "-e":101,
                            "-n":self.scene.split("/")[-1],
                            "-p":"",
                            "-r":"",
                            "-x":"",
                            "-m":"",
                            "-c":"",
                            }

        #Apply the -flag args
        opts = dict(opts)
        keys = list(opts.keys())
        for key in keys:
            self.settingsDict[key] = opts[key]
            logger.debug("Setting Key %s with opt %s" % (key, str(opts[key])))

        #Fix paths
        self.settingsDict["-p"] = self.settingsDict["-p"].replace('\\', '/')

    def hookupButtons(self):
            QObject.connect(self.submitButton, SIGNAL("clicked()"),
                            self.submitButtonHandler)
            QObject.connect(self.testCheckBox, SIGNAL("stateChanged(int)"),
                            self.toggleTestBoxes)

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
            self.reqChecks.append(c)

    def populateExecs(self):
        #Get execs
        #Stored in Constants for now
        execsDict = Constants.EXECUTEABLES
        execs = list(execsDict.keys())
        execs.sort()
        execs.reverse()

        for item in execs:
            name = Constants.EXECUTEABLENAMES[item]
            self.executableComboBox.addItem(name)

    def setupForms(self):
        self.sceneLineEdit.setText(self.scene)
        self.projLineEdit.setText(self.settingsDict["-p"])
        self.niceNameLineEdit.setText(self.settingsDict["-n"])
        self.startSpinBox.setValue(eval(self.settingsDict["-s"]))
        self.endSpinBox.setValue(eval(self.settingsDict["-e"]))
        self.renderLayersLineEdit.setText(self.settingsDict["-r"])
        self.cmdLineEdit.setText(self.settingsDict["-m"])

    #------------------------------------------------------------------------#
    #----------------------------Button Handlers-----------------------------#
    #------------------------------------------------------------------------#

    def submitButtonHandler(self):
        if self.testCheckBox.isChecked():
            print "Phase 01"
        if self.finalCheckBox.isChecked():
            print "Phase 02"

        print self.settingsDict

    def toggleTestBoxes(self):
        if self.testFramesSpinBox.isEnabled():
            self.testFramesSpinBox.setEnabled(False)
            self.testNodesSpinBox.setEnabled(False)
        else:
            self.testFramesSpinBox.setEnabled(True)
            self.testNodesSpinBox.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SubmitterMain()

    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
