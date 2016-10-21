"""Some useful message boxes to be use in FarmView and SubmitterMain."""
#Doesn't like Qt classes
#pylint: disable=E0611
#Third Party
from PyQt4.QtGui import QMessageBox, QInputDialog

def aboutBox(parent, title="About", msg="This is a sample about box."):
    """Creates a message box with an OK button, suitable for displaying short
    messages to the user."""
    QMessageBox.about(parent, title, msg)

def warningBox(parent, title="Warning!", msg="This is a sample warning!"):
    """Creates a message box with an OK button and a yellow yeild sign, suitable
    for displaying short errors/warning messages to the user."""
    return QMessageBox.warning(parent, title, msg)

def yesNoBox(parent, title="Yes/No?", msg="This is a sample yes/no dialog."):
    """Creates a message box with Yes and No buttons. Returns QMessageBox.Yes
    if the user clicked Yes, or QMessageBox.No otherwise."""
    return QMessageBox.question(parent, title, msg,
        buttons=(QMessageBox.Yes | QMessageBox.No),
        defaultButton=QMessageBox.Yes)

def intBox(parent, title="IntBox", msg="This is a sample int dialog.", default=0):
    """Makes a box for getting ints"""
    return QInputDialog.getInt(parent, title, msg, default)

def strBox(parent, title="StrBox", msg="This is a sample StrBox."):
    """Makes a box for getting strings"""
    return QInputDialog.getText(parent, title, msg)

def SQLErrorBox(parent):
    """A convience function that makes a box with the SQL error information"""
    msgString = "There was a problem while trying to fetch info from the database. Check the log file for more details about the error."
    return QMessageBox.warning(parent, "SQL Error", msgString)
