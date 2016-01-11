#Standard
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QObject, SIGNAL

#Hydra
from UI_JobFilter import Ui_jobFilterDialog

class JobFilterDialog(QDialog, Ui_jobFilterDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        #Connect Buttons
        QObject.connect(self.cancelButton, SIGNAL("clicked()"), 
                        self.cancelButtonHandler)
        QObject.connect(self.okButton, SIGNAL("clicked()"),
                        self.okButtonHandler)
        QObject.connect(self.resetButton, SIGNAL("clicked()"),
                        self.resetTaskButtonHandler)
        QObject.connect(self.statusToggleButton, SIGNAL("clicked()"),
                        self.statusToggleButtonHandler)
                        
        #Set globals
        self.doSearch = False
        self.checkboxList = [self.crashedCheckbox, self.errorCheckbox,
                            self.finishedCheckbox, self.killedCheckbox,
                            self.pausedCheckbox, self.readyCheckbox,
                            self.startedCheckbox]
        self.checkboxKeys = ["C", "E", "F", "K", "U", "R", "S"]
        
    def getValues(self):
        checkboxDict = {}
        for i in range(len(self.checkboxList)):
            checkboxDict[self.checkboxKeys[i]] = self.checkboxList[i].isChecked()
        owner = str(self.ownerLineEdit.text())
        name = str(self.nameLineEdit.text())
        limit = int(self.limitSpinBox.value())
        return {"status":checkboxDict, "owner":owner, "name":name, "limit":limit}
        
    def statusToggleButtonHandler(self):
        for checkbox in self.checkboxList:
            checkbox.setCheckState(2)
        
    def resetTaskButtonHandler(self):
        self.statusToggleButtonHandler()
        self.ownerLineEdit.setText("")
        self.nameLineEdit.setText("")
        self.limitSpinBox.setValue(100)  
    
    def cancelButtonHandler(self):
        self.close()
        return False
    
    def okButtonHandler(self):
        self.doSearch = True
        self.close()
    
    @classmethod
    def create(cls):
        dialog = JobFilterDialog()
        dialog.exec_()
        if dialog.doSearch:
            return dialog.getValues()
