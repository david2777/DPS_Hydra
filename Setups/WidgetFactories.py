#Standard
import functools

#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Setups.LoggingSetup import logger

class widgetFactory():
    """A widget building class intended to be subclassed for building particular
    types of widgets. 'name' must be the name of a database column."""

    def __init__(self, name, intention = None):
        self.name = name
        self.intention = intention

    def headerWidget(self):
        """Makes a label for the header row of the display."""

        return QLabel('<b>' + self.name + '</b>')

    def data(self, record):

        return str(getattr(record, self.name))

    def dataWidget(self, record):
        """Create a QWidget instance and return a reference to it. To make a
        widget, given a record, extract the named attribute from the record
        with the data method, and use that as the widget's text/data."""

        raise NotImplementedError

class labelFactory(widgetFactory):
    """A label widget factory. The object's name is the name of a database
    column."""

    def dataWidget(self, record):
        return QLabel(self.data(record))

class lineEditFactory(widgetFactory):
    """like labelFactory, but makes a read-only text field instead of a
    label."""

    def dataWidget(self, record):
        w = QLineEdit()
        w.setText(self.data(record))
        w.setReadOnly(True)
        return w

class buttonFactory(widgetFactory):
    def dataWidget(self, record):
        b = QPushButton(self.name)
        if self.intention == None:
            QObject.connect(b, SIGNAL("clicked()"), self.doNothing)

        else:
            handler = functools.partial(self.intention, record)
            QObject.connect(b, SIGNAL("clicked()"), handler)

        return b

    def doNothing(self):
        pass

class getOffButton(widgetFactory):
    """As above, but makes a specialized button to implement the GetOff
    function."""

    def dataWidget (self, record):
        w = QPushButton(self.name)
        #The click handler is the doGetOff method, but with the record
        #Argument already supplied. it's called a "partial application".
        handler = functools.partial(self.doGetOff, record=record)

        QObject.connect(w, SIGNAL("clicked()"), handler)
        return w

    def doGetOff(self, record):
        logger.info('GetOff! {0}'.format(record.host))

class WidgetForTable:
    def setIntoTable(self, table, row, column):
        table.setCellWidget(row, column, self)

class LabelForTable(QLabel, WidgetForTable): pass

class TableWidgetItem(QTableWidgetItem):
    def setIntoTable(self, table, row, column):
        table.setItem(row, column, self)

class TableWidgetItem_check(TableWidgetItem):
    def __init__(self):
        TableWidgetItem.__init__(self)
        self.setCheckState(Qt.Unchecked)

class TableWidgetItem_int(QTableWidgetItem):
    """A QTableWidgetItem which holds integer data and sorts it properly."""
    def __init__(self, stringValue):
        QTableWidgetItem.__init__(self, stringValue)

    def __lt__(self, other):
        return int(self.text()) < int(other.text())

class TableWidgetItem_dt(TableWidgetItem):
    """A QTableWidgetItem which holds datetime.datetime data and sorts it properly."""
    def __init__(self, dtValue):
        QTableWidgetItem.__init__(self, str(dtValue))
        self.dtValue = dtValue

    def __lt__(self, other):
        if self.dtValue and other.dtValue:
            return self.dtValue < other.dtValue
        elif self.dtValue and not other.dtValue:
            return True
        else:
            return False
