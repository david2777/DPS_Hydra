"""Some useful message boxes to be use in FarmView and SubmitterMain."""
#Standard
from PyQt4.QtGui import QMessageBox, QInputDialog

#Original Author: Aaron Cohn
#Taken from Cogswell's Project Hydra

def aboutBox(parent=None, title="", msg=""):
    """Creates a message box with an OK button, suitable for displaying short
    messages to the user."""
    QMessageBox.about(parent, title, msg)

def yesNoBox(parent=None, title="", msg=""):
    """Creates a message box with Yes and No buttons. Returns QMessageBox.Yes
    if the user clicked Yes, or QMessageBox.No otherwise."""
    return QMessageBox.question(parent, title, msg,
        buttons=(QMessageBox.Yes | QMessageBox.No),
        defaultButton=QMessageBox.Yes)

def intBox(parent = None, title="", msg="", default = 0):
    """Makes a box for getting ints"""
    return(QInputDialog.getInt(parent, title, msg, default))

def strBox(parent = None, title="", msg=""):
    """Makes a box for getting strings"""
    return(QInputDialog.getText(parent, title, msg))
