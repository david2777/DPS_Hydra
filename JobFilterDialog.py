#Standard
from PyQt4.QtGui import QDialog
from PyQt4.QtCore import QObject, SIGNAL

#Hydra
from UI_JobFilter import Ui_jobFilterDialog

class JobFilterDialog(QDialog, Ui_jobFilterDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.doSearch = False
        QObject.connect(self.cancelButton, SIGNAL("clicked()"), 
                        self.cancelButtonHandler)
        QObject.connect(self.okButton, SIGNAL("clicked()"),
                        self.okButtonHandler)
        QObject.connect(self.resetButton, SIGNAL("clicked()"),
                        self.resetTaskButtonHandler)
        QObject.connect(self.statusToggleButton, SIGNAL("clicked()"),
                        self.statusToggleButtonHandler)
        
    def getValues(self):
        return "Values go here!"
        
    def statusToggleButtonHandler(self):
        print "Nothing"
        
    def resetTaskButtonHandler(self):
        print "Reseting..."
    
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
