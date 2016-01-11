#Standard
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QObject, SIGNAL

#Hydra
from UI_JobFilter import Ui_jobFilterDialog

class JobFilterDialog(QDialog, Ui_jobFilterDialog):
    def __init__(self, defaults, parent=None):
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
        #Order matters! Keys should be alphabetical.
        self.checkboxList = [self.crashedCheckbox, self.errorCheckbox,
                            self.finishedCheckbox, self.killedCheckbox,
                            self.readyCheckbox, self.startedCheckbox,
                            self.pausedCheckbox]
        self.checkboxKeys = ["C", "E", "F", "K", "R", "S", "U"]
        
        if defaults != None:
            self.ownerLineEdit.setText(defaults["owner"])
            self.nameLineEdit.setText(defaults["name"])
            self.limitSpinBox.setValue(defaults["limit"])
            cbxList = defaults["status"]
            for i in range(len(self.checkboxList)):
                if cbxList[i]:
                    self.checkboxList[i].setCheckState(2)
                else:
                    self.checkboxList[i].setCheckState(0)
            
            
        
    def getValues(self):
        checkboxList = []
        for i in range(len(self.checkboxList)):
            checkboxList.append(self.checkboxList[i].isChecked())
        owner = str(self.ownerLineEdit.text())
        name = str(self.nameLineEdit.text())
        limit = int(self.limitSpinBox.value())
        return {"status":checkboxList, "owner":owner, "name":name, "limit":limit}
        
    def statusToggleButtonHandler(self):
        for checkbox in self.checkboxList:
            checkbox.setCheckState(2)
        
    def resetTaskButtonHandler(self):
        self.statusToggleButtonHandler()
        self.ownerLineEdit.setText("")
        self.nameLineEdit.setText("")
        self.limitSpinBox.setValue(100)  
        self.close()
        return None
    
    def cancelButtonHandler(self):
        self.close()
    
    def okButtonHandler(self):
        self.doSearch = True
        self.close()
    
    @classmethod
    def create(cls, defaults):
        dialog = JobFilterDialog(defaults)
        dialog.exec_()
        if dialog.doSearch:
            return dialog.getValues()
