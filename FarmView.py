"""The software for managing jobs, tasks, and nodes."""
#Standard
import os
import re
import sys
import time
import fnmatch
import datetime
import functools
import webbrowser
from socket import error as socketerror

#Third Party
from MySQLdb import Error as sqlerror
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from Setups.WidgetFactories import *
from CompiledUI.UI_FarmView import Ui_FarmView
from Dialogs.TaskSearchDialog import TaskSearchDialog
from Dialogs.JobFilterDialog import JobFilterDialog
from Dialogs.NodeEditorDialog import NodeEditorDialog
from Dialogs.DetailedDialog import DetailedDialog
from Dialogs.MessageBoxes import aboutBox, yesNoBox, intBox, strBox

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
from Setups.Threads import workerSignalThread
import Utilities.Utils as Utils
import Utilities.TaskUtils as TaskUtils
import Utilities.JobUtils as JobUtils
import Utilities.NodeUtils as NodeUtils

#Parts taken from Cogswell's Project Hydra by David Gladstein and Aaron Cohn

#------------------------------------------------------------------------------#
#--------------------------------Farm View-------------------------------------#
#------------------------------------------------------------------------------#

class FarmView(QMainWindow, Ui_FarmView):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        self.thisNodeName = Utils.myHostName()
        logger.info("This host is {0}".format(self.thisNodeName))

        #My UI Setup Functions
        self.setupTables()
        self.connectButtons()

        #Enable this node buttons
        self.thisNodeButtonsEnabled = True

        #Get user
        self.username = Utils.getDbInfo()[2]

        #Globals
        self.filters = None
        self.userFilter = False
        self.showArchivedFilter = False

        self.statusMsg = ""

        self.lastJTUpdate = False
        self.currentJobSel = None
        self.newestJobID = 0

        self.autoUpdateThread = workerSignalThread("run", 10)
        QObject.connect(self.autoUpdateThread, SIGNAL("run"), self.doUpdate)

        #Partial applications for convenience
        self.sqlErrorBox = (
            functools.partial(
                aboutBox,
                parent = self,
                title = "Error",
                msg = "There was a problem while trying to fetch info"
                " from the database. Check the FarmView log file for"
                " more details about the error."))
        self.noneCheckedBox = (
            functools.partial(
                aboutBox,
                parent = self,
                title = "None checked",
                msg = "No nodes have been selected. Use the check boxes"
                " to make a selection from the table."))

        self.nodeDoesNotExistBox = (
            functools.partial(
                aboutBox,
                parent = self,
                title = "Notice",
                msg = "Information about this node cannot be displayed because "
                "it is not registered on the render farm. You may continue to "
                "use Farm View, but it must be restarted after this node is "
                "registered if you wish to see this node's information."))

        self.doFetch()
        if self.thisNodeExists:
            self.autoUpdateThread.start()
        else:
            self.autoUpdateCheckbox.setCheckState(0)
            self.autoUpdateCheckbox.setEnabled(False)

    def closeEvent(self, event):
        event.accept()
        sys.exit(0)


    #---------------------------------------------------------------------#
    #--------------------------UI SETUP FUNCTIONS-------------------------#
    #---------------------------------------------------------------------#
    def setupTables(self):
        # Column widths on the render node table
        self.renderNodeTable.setColumnWidth(0, 200)     #Host
        self.renderNodeTable.setColumnWidth(1, 70)      #Status
        self.renderNodeTable.setColumnWidth(2, 70)      #Task ID
        self.renderNodeTable.setColumnWidth(3, 70)      #Min Priority
        self.renderNodeTable.setColumnWidth(4, 100)     #Online Time
        self.renderNodeTable.setColumnWidth(5, 100)      #Offline Time
        self.renderNodeTable.setColumnWidth(6, 110)     #Heartbeat
        self.renderNodeTable.setColumnWidth(7, 110)     #Version
        self.renderNodeTable.setColumnWidth(8, 110)     #Capabilities

        #Column widths on jobTable
        self.jobTable.setColumnWidth(0, 60)         #Job ID
        self.jobTable.setColumnWidth(1, 60)         #Priority
        self.jobTable.setColumnWidth(2, 60)         #Status
        self.jobTable.setColumnWidth(4, 80)         #Owner
        self.jobTable.setColumnWidth(4, 60)         #Tasks
        self.jobTable.sortItems(0, order = Qt.DescendingOrder)

        # Column widths on the taskTable
        self.taskTable.setColumnWidth(0, 60)        #ID
        self.taskTable.setColumnWidth(1, 60)        #Priority
        self.taskTable.setColumnWidth(2, 60)        #Frame
        self.taskTable.setColumnWidth(3, 100)       #Host
        self.taskTable.setColumnWidth(4, 60)        #Status
        self.taskTable.setColumnWidth(5, 120)       #Start Time
        self.taskTable.setColumnWidth(6, 120)       #End Time
        self.taskTable.setColumnWidth(7, 120)       #Duration
        self.taskTable.setColumnWidth(8, 120)       #Code

        #Set Job List splitter size
        #These numbers are really high so that they work proportionally
        #The 10000 makes it so that the 8500 is 85%
        self.splitter_jobList.setSizes([8500, 10000])

        #Get the global column count for later
        self.taskTableCols = self.taskTable.columnCount()

        self.jobTable.setAlternatingRowColors(True)
        self.taskTable.setAlternatingRowColors(True)
        self.renderNodeTable.setAlternatingRowColors(True)

    def connectButtons(self):
        #Connect tab switch data update
        self.tabWidget.currentChanged.connect(self.doUpdate)
        #Connect buttons in This Node tab
        self.fetchButton.clicked.connect(self.doFetch)
        self.onlineThisNodeButton.clicked.connect(self.onlineThisNodeHandler)
        self.offlineThisNodeButton.clicked.connect(self.offlineThisNodeHandler)
        self.getOffThisNodeButton.clicked.connect(self.getOffThisNodeHandler)
        self.updateButton.clicked.connect(self.doUpdate)
        self.autoUpdateCheckbox.stateChanged.connect(self.autoUpdateHandler)
        self.editThisNodeButton.clicked.connect(self.nodeEditorHandler)

        #Connect basic filter checkboxKeys
        self.archivedCheckBox.stateChanged.connect(self.archivedFilterActionHandler)
        self.userFilterCheckbox.stateChanged.connect(self.userFilterActionHandler)

        #Connect actions in Job View
        self.jobTable.cellClicked.connect(self.jobCellClickedHandler)

        #Connect Context Menus
        self.centralwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.centralwidget.customContextMenuRequested.connect(self.centralContextHandler)

        self.jobTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.jobTable.customContextMenuRequested.connect(self.jobContextHandler)

        self.taskTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.taskTable.customContextMenuRequested.connect(self.taskContextHandler)

        self.renderNodeTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.renderNodeTable.customContextMenuRequested.connect(self.nodeContextHandler)

    def centralContextHandler(self):
        def addItem(name, handler, statusTip):
            action = QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            self.centralMenu.addAction(action)
            return action

        self.centralMenu = QMenu(self)

        QObject.connect(self.centralMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        addItem("Soft Update",
                self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update",
                self.doFetch,
                "Update all of the latest information from the Database")
        self.centralMenu.addSeparator()
        onAct = addItem("Online This Node",
                        self.onlineThisNodeHandler,
                        "Online This Node")
        offAct = addItem("Offline This Node",
                        self.offlineThisNodeHandler,
                        "Wait for the current job to finish then offline this node")
        getAct = addItem("Get Off This Node!",
                        self.getOffThisNodeHandler,
                        "Kill the current task and offline this node immediately")

        if not self.thisNodeButtonsEnabled:
            onAct.setEnabled(False)
            offAct.setEnabled(False)
            getAct.setEnabled(False)

        self.centralMenu.popup(QCursor.pos())

    def revealDetailedHandler(self, qtTable, qtIdx, qtRows, sqlTable, sqlWhere):
        dataList = []
        for row in qtRows:
            if type(row) == int:
                data_id = int(qtTable.item(row, 0).text())
            else:
                data_id = row
            [data] = sqlTable.secureFetch(sqlWhere, (data_id))
            dataList.append(data)

        DetailedDialog.create(dataList)

    #---------------------------------------------------------------------#
    #----------------------------JOB HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def jobContextHandler(self):
        def addItem(name, handler, statusTip):
            action = QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            self.jobMenu.addAction(action)
            return action

        self.jobMenu = QMenu(self)
        #self.jobMenu.setTearOffEnabled(True)

        QObject.connect(self.jobMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        addItem("Soft Update",
                self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update",
                self.doFetch,
                "Update all of the latest information from the Database")
        self.jobMenu.addSeparator()
        addItem("Start Jobs",
                self.startJobHandler,
                "Start all jobs selected in Job List")
        addItem("Pause Jobs",
                self.pauseJobHandler,
                "Pause all jobs selected in Job List")
        addItem("Kill Jobs",
                self.killJobHandler,
                "Kill all jobs selected in Job List")
        addItem("Reset Jobs",
                self.resetJobHandler,
                "Reset all jobs selected in Job List")
        addItem("Start Test Frames...",
                self.callTestFrameBox,
                "Open a dialog to start the first X frames in each job "
                "selected in the Job List")
        self.jobMenu.addSeparator()
        addItem("Archive/Unarchive Jobs",
                self.toggleArchiveHandler,
                "Toggle the Archived status on each job selected in he Job List")
        addItem("Reset Node Limit on Jobs",
                self.resetNodeManagementHandler,
                "Reset the number of tasks which are ready to match the limit "
                "of the number of concurant tasks.")
        addItem("Reveal Detailed Data...",
                self.revealJobDetailedHandler,
                "Opens a dialog window the detailed data for the selected jobs.")
        self.jobMenu.addSeparator()
        #setJobPriorityHandler
        addItem("Set Job Priority...",
                self.setJobPriorityHandler, "Set priority on each job selected "
                "in the Job List")
        editJob = addItem("Edit Job...",
                            self.doNothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)
        self.jobMenu.addSeparator()

        userFilterAction = addItem("Only Show My Jobs",
                                    self.userFilterContextHandler,
                                    "Only show the jobs belonging to the "
                                    "current user")
        userFilterAction.setCheckable(True)
        if self.userFilter:
            userFilterAction.setChecked(True)

        archivedFilterAction = addItem("Show Archived Jobs",
                                        self.archivedFilterContextHandler,
                                        "Show jobs which have been archived")
        archivedFilterAction.setCheckable(True)
        if self.showArchivedFilter:
            archivedFilterAction.setChecked(True)

        addItem("Filters...",
                self.filterJobHandler,
                "Open filters dialog to select which types of jobs are shown "
                "in the Job List")
        self.jobMenu.popup(QCursor.pos())

    def userFilterContextHandler(self):
        if self.userFilter:
            self.userFilterCheckbox.setChecked(0)
        else:
            self.userFilterCheckbox.setChecked(2)
        self.initJobTable()
        self.resetStatusBar()

    def archivedFilterContextHandler(self):
        if self.showArchivedFilter:
            self.archivedCheckBox.setChecked(0)
        else:
            self.archivedCheckBox.setChecked(2)
        self.initJobTable()
        self.resetStatusBar()

    def userFilterActionHandler(self):
        if self.userFilter:
            self.userFilter = False
            self.userFilterCheckbox.setChecked(0)
        else:
            self.userFilter = True
            self.userFilterCheckbox.setChecked(2)
        self.initJobTable()

    def archivedFilterActionHandler(self):
        if self.showArchivedFilter:
            self.showArchivedFilter = False
            self.archivedCheckBox.setChecked(0)
        else:
            self.showArchivedFilter = True
            self.archivedCheckBox.setChecked(2)
        self.initJobTable()

    def jobCommandBuilder(self, update = False):
        command = "WHERE"
        if self.filters != None:
            checkboxKeys = ["C", "E", "F", "K", "R", "S", "U"]
            users = self.filters["owner"].split(",")
            names = self.filters["name"].split(",")
            statuses = self.filters["status"]
            limit = self.filters["limit"]
            if users[0] != "":
                command += " owner = '{0}'".format(users[0])
                for user in users[1:]:
                    command += " OR owner = '{0}'".format(user)
            if names[0] != "":
                if command != "WHERE":
                    command += " AND"
                command += " niceName LIKE '{0}'".format(names[0])
                for name in names[1:]:
                    command += " OR niceName LIKE '{0}'".format(name)
            if False in statuses:
                idx = 0
                for i in range(len(statuses)):
                    if not statuses[i]:
                        if command != "WHERE" and idx == 0:
                            command += " AND"
                        if idx == 0:
                            command += " job_status <> '{0}'".format(checkboxKeys[i])
                            idx += 1
                        else:
                            command += " AND job_status <> '{0}'".format(checkboxKeys[i])
                            idx += 1

        if command.find("owner = ") < 0:
            if self.userFilter:
                if command != "WHERE":
                    command += " AND"
                command += " owner = '{0}'".format(self.username)
            if not self.showArchivedFilter:
                if command != "WHERE":
                    command += " AND"
                command += " archived = 0"

        if update:
            if command != "WHERE":
                command += " AND"
            command += " id > '{0}'".format(self.newestJobID)

        if self.filters != None:
            command += " LIMIT 0,{0}".format(limit)

        if command == "WHERE":
            command = ""

        return command

    def initJobTable(self):
        self.jobTable.setSortingEnabled(False)
        command = self.jobCommandBuilder()
        try:
            jobs = hydra_jobboard.fetch(command)
            self.jobTable.setRowCount(len(jobs))
            for row, job in enumerate(jobs):
                self.insertJobTableItem(job, row)
            labelText = "Job List"
            if self.filters:
                labelText += " (Filtered)"
            if self.userFilter:
                labelText += " (This User Only)"
            if not self.showArchivedFilter:
                labelText += " (No Archived Jobs)"
            self.jobTableLabel.setText(labelText + ":")
        except sqlerror as err:
            logger.debug(str(err))
            aboutBox(self, "SQL error", str(err))
        if jobs:
            self.newestJobID = max([job.id for job in jobs])
        self.jobTable.setSortingEnabled(True)

    def updateJobTable(self):
        #Update job statuses
        rows = self.jobTable.rowCount()
        try:
            with transaction() as t:
                query = "SELECT id, tasksComplete, tasksTotal, job_status FROM "
                query += "hydra_jobboard WHERE archived = '0'"
                t.cur.execute(query)
                jobData = t.cur.fetchall()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()

        jobDict = {int(job_id):[int(tasksComplete),
                                int(tasksTotal),
                                str(job_status)] for job_id,
                                                    tasksComplete,
                                                    tasksTotal,
                                                    job_status in jobData}
        for row in range(rows):
            try:
                thisJob_id = int(self.jobTable.item(row, 0).text())
                tasksComplete, tasksTotal, job_status = jobDict[thisJob_id]
                if tasksTotal > 0:
                    percent = "{0:.0%}".format(float(tasksComplete / tasksTotal))
                    taskString  = "{0} ({1}/{2})".format(percent,
                                                        tasksComplete,
                                                        tasksTotal)
                else:
                    taskString = "0% (0/0)"
                self.jobTable.setItem(row, 2, TableWidgetItem(str(niceNames[job_status])))
                self.jobTable.item(row, 2).setBackgroundColor(niceColors[job_status])
                self.jobTable.setItem(row, 4, TableWidgetItem(taskString))
            except KeyError:
                logger.debug("Skipping {0} on JT Update".format(thisJob_id))

        #Add new jobs
        self.jobTable.setSortingEnabled(False)
        command = self.jobCommandBuilder(True)
        try:
            newJobs = hydra_jobboard.fetch(command)
            for job in newJobs:
                self.jobTable.insertRow(0)
                self.insertJobTableItem(job, 0)
        except sqlerror as err:
            logger.debug(str(err))
            aboutBox(self, "SQL error", str(err))
        if newJobs:
            self.newestJobID = max([job.id for job in newJobs])
        self.jobTable.setSortingEnabled(True)

    def insertJobTableItem(self, job, row):
        if job.tasksTotal > 0:
            percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
            taskString  = "{0} ({1}/{2})".format(percent,
                                                job.tasksComplete,
                                                job.tasksTotal)
        else:
            taskString = "0% (0/0)"
        self.jobTable.setItem(row, 0, TableWidgetItem_int(str(job.id)))
        self.jobTable.setItem(row, 1, TableWidgetItem_int(str(job.priority)))
        self.jobTable.setItem(row, 2, TableWidgetItem_int(str(niceNames[job.job_status])))
        self.jobTable.item(row, 2).setBackgroundColor(niceColors[job.job_status])
        self.jobTable.setItem(row, 3, TableWidgetItem(str(job.owner)))
        self.jobTable.setItem(row, 4, TableWidgetItem(taskString))
        self.jobTable.setItem(row, 5, TableWidgetItem(str(job.niceName)))
        if job.owner == self.username:
            self.jobTable.item(row, 3).setFont(QFont('Segoe UI', 8, QFont.DemiBold))
        if job.archived == 1:
            self.jobTable.item(row, 0).setBackgroundColor(QColor(220,220,220))
            self.jobTable.item(row, 1).setBackgroundColor(QColor(220,220,220))
            self.jobTable.item(row, 3).setBackgroundColor(QColor(220,220,220))
            self.jobTable.item(row, 4).setBackgroundColor(QColor(220,220,220))
            self.jobTable.item(row, 5).setBackgroundColor(QColor(220,220,220))

    def updateJobRow(self, job, row, tasks):
        try:
            job_id = job.id
            JobUtils.updateJobTaskCount(job_id, tasks = tasks, commit = True)
            pos = row
            if job.tasksTotal > 0:
                percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
                taskString  = "{0} ({1}/{2})".format(percent,
                                                    job.tasksComplete,
                                                    job.tasksTotal)
            else:
                taskString = "0% (0/0)"
            self.jobTable.setItem(pos, 0, TableWidgetItem_int(str(job.id)))
            self.jobTable.setItem(pos, 1, TableWidgetItem_int(str(job.priority)))
            self.jobTable.setItem(pos, 2, TableWidgetItem_int(str(niceNames[job.job_status])))
            self.jobTable.item(pos, 2).setBackgroundColor(niceColors[job.job_status])
            self.jobTable.setItem(pos, 3, TableWidgetItem(str(job.owner)))
            self.jobTable.setItem(pos, 4, TableWidgetItem(taskString))
            self.jobTable.setItem(pos, 5, TableWidgetItem(str(job.niceName)))
            if job.archived == 1:
                self.jobTable.item(pos, 0).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 1).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 3).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 4).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 5).setBackgroundColor(QColor(220,220,220))
            if job.owner == self.username:
                self.jobTable.item(pos, 3).setFont(QFont('Segoe UI', 8, QFont.DemiBold))
        except sqlerror as err:
            logger.error(str(err))
            aboutBox(self, "SQL error", str(err))

    def jobTableHandler(self):
        self.resetStatusBar()
        rows = self.jobTable.selectionModel().selectedRows()
        if len(rows) < 1:
            aboutBox(self,
                    "Selection Error",
                    "Please select something from the Job Table and try again.")
            return None
        return [item.row() for item in rows]

    def startJobHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            JobUtils.startJob(job_id)
        self.initJobTable()
        self.jobCellClickedHandler(rows[-1])
        self.jobTable.setCurrentCell(rows[-1], 0)

    def killJobHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really kill the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    response = JobUtils.killJob(job_id)
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if not response:
                    aboutBox(self,
                            "Error",
                            "One or more nodes couldn't kill their tasks.")
                self.updateJobTable()
                JobUtils.manageNodeLimit(job_id)
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def pauseJobHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really pause the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    response = False
                    if JobUtils.killJob(job_id, "U"):
                        response = True
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if response:
                    aboutBox(self,
                            "Error",
                            "One or more nodes couldn't kill their tasks.")
                self.initJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def resetJobHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    response = JobUtils.resetJob(job_id, "U")
                    if response:
                        msg = "Could not reset task(s) under job {0} becase of "
                        "error(s) communicating with their host(s)".format(job_id)
                        aboutBox(self,
                                title = "Reset Job Error",
                                msg = msg)
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.initJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def resetNodeManagementHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        cStr = "Are you sure you want to reset node managment on the selected Job?\n"
        cStr += "This will hold all Tasks above the max node count set on the Job."
        choice = yesNoBox(self, "Confirm", cStr)
        if choice == QMessageBox.Yes:
            for row in rows:
                job_id = int(self.jobTable.item(row, 0).text())
                JobUtils.setupNodeLimit(job_id)

        self.initJobTable()
        self.jobCellClickedHandler(rows[-1])
        self.jobTable.setCurrentCell(rows[-1], 0)

    def setJobPriorityHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            job_priority = int(self.jobTable.item(row, 1).text())
            msgString = "Priority for job {0}:".format(job_id)
            reply = intBox(self, "Set Job Priority", msgString , job_priority)
            if reply[1]:
                JobUtils.prioritizeJob(job_id, reply[0])
            else:
                logger.info("prioritizeJob skipped on {0}".format(job_id))
        self.initJobTable()
        self.jobTable.setCurrentCell(rows[-1], 0)

    def toggleArchiveHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        choice = yesNoBox(self,
                        "Confirm",
                        "Really archive or unarchive the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                commandList = []
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    [job] = hydra_jobboard.secureFetch("WHERE id = %s",(job_id))
                    if job.archived == 1:
                        new = 0
                    else:
                        new = 1
                    job_command = "UPDATE hydra_jobboard SET archived = %s WHERE id = %s"
                    task_command = "UPDATE hydra_taskboard SET archived = %s WHERE job_id = %s"
                    commandList.append(job_command.format(new, job_id))
                    commandList.append(task_command.format(new, job_id))

                with transaction() as t:
                    t.cur.execute(job_command, (new, job_id))
                    t.cur.execute(task_command, (new, job_id))

            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.initJobTable()

    def revealJobDetailedHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        self.revealDetailedHandler(self.jobTable, 0, rows, hydra_jobboard, "WHERE id = %s")

    #---------------------------------------------------------------------#
    #---------------------------TASK HANDLERS-----------------------------#
    #---------------------------------------------------------------------#
    def taskContextHandler(self):
        def addItem(name, handler, statusTip):
            action = QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            self.taskMenu.addAction(action)

        self.taskMenu = QMenu(self)

        QObject.connect(self.taskMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        addItem("Soft Update", self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update", self.doFetch,
                "Update all of the latest information from the Database")
        self.taskMenu.addSeparator()
        addItem("Start Tasks", self.startTaskHandler,
                "Start all tasks selected in the Task List")
        addItem("Pause Tasks", self.pauseTaskHandler,
                "Pause all tasks selected in the Task List")
        addItem("Kill Tasks", self.killTaskHandler,
                "Kill all tasks selected in the Task List")
        addItem("Reset Tasks", self.resetTaskHandler,
                "Reset all tasks selected in the Task List")
        self.taskMenu.addSeparator()
        addItem("Reveal Detailed Data...", self.revealTaskDetailedHandler,
                "Opens a dialog window the detailed data for the selected tasks.")
        addItem("Load LogFile", self.loadLogHandler,
                "Load the log file for all tasks selected in the Task List")
        self.taskMenu.popup(QCursor.pos())

    def initTaskTable(self, job_id, row):
        [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id))
        self.currentJobSel = job.id
        sString = "Task List (Job ID: {0}) (Node Limit: {1})".format(str(job_id),
                                                                    int(job.maxNodes))
        self.taskTableLabel.setText(sString)
        try:
            tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id))
            self.taskTable.setRowCount(len(tasks))
            for pos, task in enumerate(tasks):
                #Calcuate time difference
                tdiff = None
                if task.endTime:
                    tdiff = task.endTime - task.startTime
                elif task.startTime:
                    tdiff = datetime.datetime.now().replace(microsecond=0) - task.startTime
                #Populate the taskTable
                #Remove first and last "%", replace with ", "
                reqsString = str(task.requirements)[1:-1].replace("%", ", ")
                self.taskTable.setItem(pos, 0, TableWidgetItem_int(str(task.id)))
                self.taskTable.setItem(pos, 1, TableWidgetItem_int(str(task.priority)))
                self.taskTable.setItem(pos, 2, TableWidgetItem_int(str(task.startFrame)))
                self.taskTable.setItem(pos, 3, TableWidgetItem(str(task.host)))
                self.taskTable.setItem(pos, 4, TableWidgetItem(str(niceNames[task.status])))
                self.taskTable.item(pos, 4).setBackgroundColor(niceColors[task.status])
                self.taskTable.setItem(pos, 5, TableWidgetItem_dt(str(task.startTime)))
                self.taskTable.setItem(pos, 6, TableWidgetItem_dt(str(task.endTime)))
                self.taskTable.setItem(pos, 7, TableWidgetItem_dt(str(tdiff)))
                self.taskTable.setItem(pos, 8, TableWidgetItem_int(str(task.exitCode)))
                self.taskTable.setItem(pos, 9, TableWidgetItem_int(reqsString))

            self.updateJobRow(job, row, tasks)

        except sqlerror as err:
            aboutBox(self, "SQL Error", str(err))

    def updateTaskTable(self):
        if self.currentJobSel:
            #Update here
            pass

    def jobCellClickedHandler(self, row):
        item = self.jobTable.item(row, 0)
        job_id = int(item.text())
        self.initTaskTable(job_id, row)

    def reloadTaskTable(self):
        row = self.jobTable.selectionModel().selectedRows()[0].row()
        self.jobCellClickedHandler(row)

    def taskTableHandler(self):
        self.resetStatusBar()
        rows = self.taskTable.selectionModel().selectedRows()
        if len(rows) < 1:
            msg = "Please select something from the Job Table and try again."
            aboutBox(self, "Selection Error", msg)
            return None
        return [item.row() for item in rows]

    def startTaskHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        for row in rows:
            task_id = int(self.taskTable.item(row, 0).text())
            TaskUtils.startTask(task_id)
        self.reloadTaskTable()

    def resetTaskHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                response = TaskUtils.resetTask(task_id, "U")
                if response:
                    msg = "Unable to reset task {0} because there was an error communicating with it's host.".format(task_id)
                    aboutBox(self, "Reset Task Error", msg)
            self.reloadTaskTable()

    def callTestFrameBox(self):
        try:
            rows = self.jobTableHandler()
            if not rows:
                return
            row = rows[0]
            reply = intBox(self, "StartTestFrames", "Start X Test Frames?", 10)
            if reply[1]:
                job_id = int(self.jobTable.item(row, 0).text())
                logger.info("Starting {0} test frames on job_id {1}".format(reply[0], job_id))
                tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id))
                for task in tasks[0:reply[0]]:
                    TaskUtils.startTask(task.id)
                logger.info("Test Tasks Started!")
                with transaction() as t:
                    [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id))
                    job.job_status = "S"
                    job.update(t)
                self.initJobTable()
                self.jobCellClickedHandler(row)
                self.jobTable.setCurrentCell(row, 0)
            else:
                logger.info("No test tasks started.")
        except IndexError:
            aboutBox(self, "Error", "Make a slection in the job table to continue...")

    def killTaskHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really kill selected tasks?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                try:
                    killed = TaskUtils.killTask(task_id)
                    if not killed:
                        aboutBox(self,
                                "Error",
                                "Task couldn't be killed for some reason.")
                except socketerror as err:
                    logger.error(str(err))
                    aboutBox(self, "Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.error(str(err))
                    aboutBox(self, "SQL Error", str(err))
        [job] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id))
        JobUtils.updateJobTaskCount(job.job_id, tasks = None, commit = True)
        JobUtils.manageNodeLimit(job.job_id)
        self.reloadTaskTable()

    def pauseTaskHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really pause selected tasks?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                try:
                    killed = TaskUtils.killTask(task_id, "U")
                    if not killed:
                        aboutBox(self,
                                "Error",
                                "Task couldn't be killed for some reason.")
                except socketerror as err:
                    logger.error(str(err))
                    aboutBox(self, "Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.error(str(err))
                    aboutBox(self, "SQL Error", str(err))
        self.reloadTaskTable()

    def loadLogHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        if len(rows) > 1:
            choice = yesNoBox(self,
                            "Open logs?",
                            "Note, this will open a text editor for EACH task "
                            "selected. Continue?")
            if choice == QMessageBox.Yes:
                for row in rows:
                    task_id = int(self.taskTable.item(row, 0).text())
                    [taskOBJ] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id))
                    loadLog(taskOBJ)
        else:
            task_id = int(self.taskTable.item(rows[0], 0).text())
            [taskOBJ] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id))
            loadLog(taskOBJ)

    def advancedSearchHandler(self):
        results = TaskSearchDialog.create()
        logger.error("Not Implemeted!")
        print results

    def filterJobHandler(self):
        self.filters = JobFilterDialog.create(self.filters)
        #logger.debug(self.filters)
        logger.info(self.jobCommandBuilder())
        self.initJobTable()

    def revealTaskDetailedHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        self.revealDetailedHandler(self.taskTable, 0, rows, hydra_taskboard, "WHERE id = %s")

    def searchByTaskID(self):
        """Given a task id, finds the job, selects it in the job table, and
        displays the tasks for that job, including the one searched for. Does
        nothing if task id doesn't exist."""
        pass
        #TODO: Fix this

    #---------------------------------------------------------------------#
    #---------------------------NODE HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def nodeContextHandler(self):
        def addItem(name, handler, statusTip):
            action = QAction(name, self)
            action.setStatusTip(statusTip)
            action.triggered.connect(handler)
            self.nodeMenu.addAction(action)
            return action

        self.nodeMenu = QMenu(self)

        QObject.connect(self.nodeMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        addItem("Soft Update",
                self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update",
                self.doFetch,
                "Update all of the latest information from the Database")
        self.nodeMenu.addSeparator()
        addItem("Online Nodes",
                self.onlineRenderNodesHandler,
                "Online all checked nodes")
        addItem("Offline Nodes",
                self.offlineRenderNodesHandler,
                "Offline all checked nodes without killing their current task")
        addItem("Get Off Nodes",
                self.getOffRenderNodesHandler,
                "Kill task then offline all checked nodes")
        self.nodeMenu.addSeparator()
        addItem("Select All Nodes",
                self.selectAllNodesHandler,
                "Check all nodes in the Node Table")
        addItem("Deselect All Node",
                self.selectNoneNodesHandler,
                "Uncheck all ndoes in the Node Table")
        addItem("Select by Host Name...",
                self.selectByHostHandler,
                "Open a dialog to check nodes based on their host name")
        self.nodeMenu.addSeparator()
        addItem("Reveal Detailed Data...", self.revealNodeDetailedHandler,
                "Opens a dialog window the detailed data for the selected nodes.")
        addItem("Edit Node...",
                self.nodeEditorTableHandler,
                "Open a dialog to edit selected node's attributes. WIP.")

        self.nodeMenu.popup(QCursor.pos())


    def initRenderNodeTable(self, nodes):
        self.renderNodeTable.setSortingEnabled(False)
        self.renderNodeTable.setRowCount(len(nodes))
        for row, node in enumerate(nodes):
            self.renderNodeTable.setItem(row, 0, TableWidgetItem(str(node.host)))
            self.renderNodeTable.setItem(row, 1, TableWidgetItem(str(niceNames[node.status])))
            self.renderNodeTable.item(row, 1).setBackgroundColor(niceColors[node.status])
            self.renderNodeTable.setItem(row, 2, TableWidgetItem(str(node.task_id)))
            self.renderNodeTable.setItem(row, 3, TableWidgetItem(str(node.minPriority)))
            if node.onlineTime and node.offlineTime:
                onlineTimeWidget = TableWidgetItem(str(node.onlineTime))
                offlineTimeWidget = TableWidgetItem(str(node.offlineTime))
                self.renderNodeTable.setItem(row, 4, onlineTimeWidget)
                self.renderNodeTable.setItem(row, 5, offlineTimeWidget)
            else:
                self.renderNodeTable.setItem(row, 4, TableWidgetItem("Manual Control"))
                self.renderNodeTable.setItem(row, 5, TableWidgetItem("Manual Control"))
            nodeVersion  = getSoftwareVersionText(node.software_version)
            self.renderNodeTable.setItem(row, 6, TableWidgetItem_dt(node.pulse))
            self.renderNodeTable.setItem(row, 7, TableWidgetItem(str(nodeVersion)))
            self.renderNodeTable.setItem(row, 8, TableWidgetItem(str(node.capabilities)))
            if node.host == self.thisNodeName:
                self.renderNodeTable.item(row, 0).setFont(QFont('Segoe UI', 8, QFont.DemiBold))

        self.renderNodeTable.setSortingEnabled(True)

    def updateRenderNodeTable(self):
        rows = self.renderNodeTable.rowCount()
        try:
            with transaction() as t:
                query = "SELECT host, status, task_id, pulse FROM hydra_rendernode"
                t.cur.execute(query)
                nodeData = t.cur.fetchall()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()

        nodeDict = {node:[status,
                            task_id,
                            pulse] for node,
                                        status,
                                        task_id,
                                        pulse in nodeData}
        for row in range(rows):
            nodeName = str(self.renderNodeTable.item(row, 0).text())
            status, task_id, pulse = nodeDict[nodeName]
            self.renderNodeTable.setItem(row, 1, TableWidgetItem(str(niceNames[status])))
            self.renderNodeTable.item(row, 1).setBackgroundColor(niceColors[status])
            self.renderNodeTable.setItem(row, 2, TableWidgetItem(str(task_id)))
            self.renderNodeTable.setItem(row, 6, TableWidgetItem_dt(pulse))

    def renderNodeTableHandler(self):
        self.resetStatusBar()
        rows = self.renderNodeTable.selectionModel().selectedRows()
        if len(rows) < 1:
            aboutBox(self,
                    "Selection Error",
                    "Please select something from the Render Node Table and try again.")
            return None
        rows = [item.row() for item in rows]
        nodes = [str(self.renderNodeTable.item(row, 0).text()) for row in rows]
        return nodes

    def onlineRenderNodesHandler(self):
        """For all nodes with boxes checked in the render nodes table, changes
        status to online."""#TODO: UPDATE DOCSTRING
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes? <br>" + str(hosts))

        if choice != QMessageBox.Yes:
            aboutBox(self, "Aborted", "No action taken.")
            return

        with transaction() as t:
            #Maybe skip the rows check
            rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            for node_row in rendernode_rows:
                if node_row.host in hosts:
                    NodeUtils.onlineNode(node_row)
        self.updateRenderNodeTable()

    def offlineRenderNodesHandler(self):
        """For all nodes with boxes checked in the render nodes table, changes
        status to offline if idle, or pending if started."""
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to offline"
                          " these nodes? <br>" + str(hosts))

        if choice != QMessageBox.Yes:
            aboutBox(self, "Aborted", "No action taken.")
            return

        with transaction() as t:
            rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            for node_row in rendernode_rows:
                if node_row.host in hosts:
                    NodeUtils.offlineNode(node_row)
        self.doFetch()

    def getOffRenderNodesHandler(self):
        """For all nodes with boxes checked in the render nodes table, changes
        status to offline if idle, or pending if started, and attempts to kill
        any task that is running on each node."""
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "<B>WARNING</B>: All progress on"
                          " current tasks will be lost for the selected"
                          " render nodes. Are you sure you want to stop these"
                          " nodes? <br>" + str(hosts))

        if choice != QMessageBox.Yes:
            aboutBox(self, "Aborted", "No action taken.")
            return

        with transaction() as t:
            rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            for thisNode in rendernode_rows:
                if thisNode.host in hosts:
                    NodeUtils.offlineNode(thisNode)
                    if thisNode.task_id:
                        task_id = thisNode.task_id
                        try:
                            response = TaskUtils.killTask(task_id, "R")
                            if not response:
                                logger.warning("Problem killing task durring GetOff")
                                aboutBox(self,
                                        "Error",
                                        "There was a problem killing the task during GetOff!")
                            else:
                                aboutBox(self, "Success", "Job was reset, node offlined.")
                        except socketerror:
                            logger.error(socketerror.message)
                            aboutBox(self, "Error", "There was a problem communicating"
                                     " with the render node software. Either it's not"
                                     " running, or it has become unresponsive.")
                    else:
                        aboutBox(self, "Success", "No job was found on node, node offlined")

        self.doFetch()

    def nodeEditorTableHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return
        elif len(hosts) > 1:
            choice = yesNoBox(self, "Confirm", "Are you sure you want to edit "
                              "multiple nodes? A box will open for each node "
                              "checked.")

            if choice == QMessageBox.No:
                aboutBox(self, "Abort", "No action taken.")

            else:
                for host in hosts:
                    self.nodeEditor(host)
        else:
            self.nodeEditor(hosts[0])

    def nodeEditor(self, nodeName):
        nodeExists = True
        if nodeExists:
            [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (nodeName))
            comps = thisNode.capabilities.split(" ")
            if thisNode.onlineTime and thisNode.offlineTime:
                sTimeData = thisNode.onlineTime.split(":")
                sTimeData = [int(t) for t in sTimeData]
                startTime = datetime.time(sTimeData[0], sTimeData[1], sTimeData[2])
                eTimeData = thisNode.offlineTime.split(":")
                eTimeData = [int(t) for t in eTimeData]
                endTime = datetime.time(eTimeData[0], eTimeData[1], eTimeData[2])
            else:
                startTime = None
                endTime = None
            defaults = {"node" : thisNode.host,
                        "priority" : thisNode.minPriority,
                        "startTime" : startTime,
                        "endTime" : endTime,
                        "comps" : comps}
            edits = NodeEditorDialog.create(defaults)
            #logger.debug(edits)
            #TODO: Secure this
            if edits:
                query = "UPDATE hydra_rendernode"
                query += " SET minPriority = '{0}'".format(edits["priority"])
                if edits["startTime"] and edits["endTime"]:
                    query += ", onlineTime = '{0}'".format(edits["startTime"])
                    query += ", offlineTime = '{0}'".format(edits["endTime"])
                else:
                    query += ", onlineTime = NULL"
                    query += ", offlineTime = NULL"
                query += ", capabilities = '{0}'".format(edits["comps"])
                query += " WHERE host = '{0}'".format(nodeName)
                #logger.debug(query)
                with transaction() as t:
                    t.cur.execute(query)

    def revealNodeDetailedHandler(self):
        rows = self.renderNodeTableHandler()
        if not rows:
            return
        self.revealDetailedHandler(self.renderNodeTable, 0, rows, hydra_rendernode, "WHERE host = %s")

    def selectAllNodesHandler(self):
        rows = self.renderNodeTable.rowCount()
        colCount = self.renderNodeTable.columnCount() - 1
        rows = [x for x in range(rows)]
        #QTableWidgetSelectionRange(Top,Left,Bottom,Right)
        for row in rows:
            mySel = QTableWidgetSelectionRange(row, 0 , row, colCount)
            self.renderNodeTable.setRangeSelected(mySel, True)

    def selectNoneNodesHandler(self):
        self.renderNodeTable.clearSelection()

    def selectByHostHandler(self):
        reply = strBox(self, "Select By Host Name", "Host (using * as wildcard):")
        if reply[1]:
            colCount = self.renderNodeTable.columnCount() - 1
            searchString = str(reply[0])
            rows = self.renderNodeTable.rowCount()
            for rowIndex in range(0, rows):
                item = str(self.renderNodeTable.item(rowIndex, 0).text())
                if fnmatch.fnmatch(item, searchString):
                    mySel = QTableWidgetSelectionRange(rowIndex, 0 , rowIndex, colCount)
                    self.renderNodeTable.setRangeSelected(mySel, True)
                    logger.info("Selecting {0} matched with {1}".format(item, searchString))

    #---------------------------------------------------------------------#
    #----------------------THIS NODE BUTTON HANDLERS----------------------#
    #---------------------------------------------------------------------#

    def autoUpdateHandler(self):
        """Toggles Auto Updater
        Note that this is run AFTER the CheckState is changed so when we do
        .isChecked() it's looking for the state after it has been checked."""
        if not self.autoUpdateCheckbox.isChecked():
            self.autoUpdateThread.terminate()
        else:
            self.autoUpdateThread.start()

    def onlineThisNodeHandler(self):
        """Changes the local render node's status to online if it was offline,
        goes back to started if it was pending offline."""
        #Get most current info from the database
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()
            return

        if thisNode:
            NodeUtils.onlineNode(thisNode)

        self.doFetch()

    def offlineThisNodeHandler(self):
        """Changes the local render node's status to offline if it was idle,
        pending if it was working on something."""
        #Get the most current info from the database
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()
            return

        if thisNode:
            NodeUtils.offlineNode(thisNode)

        self.doFetch()

    def getOffThisNodeHandler(self):
        """Offlines the node and sends a message to the render node server
        running on localhost to kill its current task(task will be
        resubmitted)"""
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.error(str(err))
            self.sqlErrorBox()
            return

        choice = yesNoBox(self, "Confirm", "All progress on the current job"
                          " will be lost. Are you sure you want to stop it?")

        if choice != QMessageBox.Yes:
            aboutBox(self, "Abort", "No action taken.")

        else:
            if thisNode:
                NodeUtils.offlineNode(thisNode)
                if thisNode.task_id:
                    task_id = thisNode.task_id
                    try:
                        response = TaskUtils.killTask(task_id)
                        TaskUtils.startTask(task_id)
                        if not response:
                            logger.warning("Problem killing task durring GetOff")
                            aboutBox(self,
                                    "Error",
                                    "There was a problem killing the task during GetOff!")
                        else:
                            aboutBox(self, "Success", "Job was reset, node offlined.")
                    except socketerror:
                        logger.error(socketerror.message)
                        aboutBox(self, "Error", "There was a problem communicating"
                                 " with the render node software. Either it's not"
                                 " running, or it has become unresponsive.")
                else:
                    aboutBox(self, "Success", "No job was found on node, node offlined")
                self.doFetch()

    def nodeEditorHandler(self):
        if self.thisNodeExists:
            self.nodeEditor(self.thisNodeName)

    #---------------------------------------------------------------------#
    #--------------------------UPDATE HANDLERS----------------------------#
    #---------------------------------------------------------------------#

    def doFetch(self):
        """Aggregate method for updating all of the widgets."""
        try:
            #Node setup and updaters
            self.thisNodeExists = False
            #TODO: Secure?
            allNodes = hydra_rendernode.fetch(order = "ORDER BY host")
            logger.info(allNodes)
            thisNode = None
            for node in allNodes:
                if node.host == self.thisNodeName:
                    thisNode = node

            if thisNode:
                self.thisNodeExists = True

            if self.thisNodeExists:
                #self.updateThisNodeInfo(thisNode)
                pass
            else:
                self.nodeDoesNotExistBox()
                self.setThisNodeButtonsEnabled(False)

            self.initRenderNodeTable(allNodes)
            self.updateStatusBar(thisNode)

            #self.updateRenderJobGrid()

            self.initJobTable()
        except sqlerror as err:
            self.autoUpdateCheckbox.setCheckState(0)
            logger.error(str(err))
            self.sqlErrorBox()

    def doUpdate(self):
        curTab = self.tabWidget.currentIndex()
        try:
            [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (self.thisNodeName))
            self.updateStatusBar(thisNode)
            if curTab == 0:
                #Job List
                self.updateJobTable()
                self.updateTaskTable()
            elif curTab == 1:
                #Render Node
                self.updateRenderNodeTable()
            elif curTab == 2:
                #Recent Jobs
                self.updateRenderJobGrid()
            elif curTab == 3:
                #This Node
                if self.thisNodeExists:
                    self.updateThisNodeInfo(thisNode)
        except sqlerror as err:
            self.autoUpdateCheckbox.setCheckState(0)
            logger.error(str(err))
            self.sqlErrorBox()

    def updateThisNodeInfo(self, thisNode):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        self.nodeNameLabel.setText(thisNode.host)
        self.nodeStatusLabel.setText(niceNames[thisNode.status])
        if thisNode.task_id:
            self.taskIDLabel.setText(str(thisNode.task_id))
        else:
            self.taskIDLabel.setText("None")
        self.nodeVersionLabel.setText(getSoftwareVersionText(thisNode.software_version))
        self.minPriorityLabel.setText(str(thisNode.minPriority))
        self.capabilitiesLabel.setText(thisNode.capabilities)
        if thisNode.onlineTime and thisNode.offlineTime:
            self.onlineTimeLabel.setText(str(thisNode.onlineTime))
            self.offlineTimeLabel.setText(str(thisNode.offlineTime))
        else:
            self.onlineTimeLabel.setText("Manual Control")
            self.offlineTimeLabel.setText("Manual Control")
        self.pulseLabel.setText(str(thisNode.pulse))

    def updateRenderJobGrid(self):
        columns = [
            labelFactory('id'),
            labelFactory('owner'),
            labelFactory('niceName'),
            labelFactory('taskFile'),
            labelFactory('baseCMD'),
            labelFactory('startFrame'),
            labelFactory('endFrame'),
            labelFactory('execName'),
            labelFactory('phase'),
            labelFactory('requirements'),
            labelFactory('job_status'),
            labelFactory('maxNodes'),
            labelFactory('creationTime')
        ]
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT %s"
        records = hydra_jobboard.secureFetch(command, (self.limitSpinBox.value()))

        clearLayout(self.taskGrid)
        setupDataGrid(records, columns, self.taskGrid)

    def updateStatusBar(self, thisNode):
        with transaction() as t:
            t.cur.execute ("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        #logger.debug("Counts = " + str(counts))
        countString = ", ".join (["{0} {1}".format(count, niceNames[status]) for (count, status) in counts])
        if thisNode:
            countString += ", {0} {1}".format(thisNode.host, niceNames[thisNode.status])
        time = datetime.datetime.now().strftime("%H:%M")
        msg = "{0} as of {1}".format(countString, time)
        self.statusMsg = msg
        self.statusbar.showMessage(self.statusMsg)

    def setThisNodeButtonsEnabled(self, choice):
        """Enables or disables buttons on This Node tab"""
        self.onlineThisNodeButton.setEnabled(choice)
        self.offlineThisNodeButton.setEnabled(choice)
        self.getOffThisNodeButton.setEnabled(choice)
        self.thisNodeButtonsEnabled = choice

    def doNothing(self):
        pass

    def resetStatusBar(self):
        self.statusbar.showMessage(self.statusMsg)

#------------------------------------------------------------------------#
#---------------------------EXTERNAL FUNCTIONS---------------------------#
#------------------------------------------------------------------------#

def getSoftwareVersionText(sw_ver):
    """Given the software_version attribute of a hydra_rendernode row, returns
    a string suitable for display purposes."""

    #Get RenderNodeMain version number if exists
    if sw_ver:
        #Case 1: executable in a versioned directory
        v = re.search("rendernodemain-dist-([0-9]+)", sw_ver, re.IGNORECASE)
        if v:
            return v.group(1)

        #Case 2: source code file
        elif re.search("rendernodemain.py$", sw_ver, re.IGNORECASE):
            return "Dev"

        #Case 3: no freakin' clue
        return "Unkown_Dev"

    else:
        return "None"

def getCheckedItems(table, itemColumn, checkBoxColumn):
    """Given a table with a column of check boxes in it, returns a list of
    the items in itemColumn which have a checked box in the same row."""

    nRows = table.rowCount()
    checks = list()
    for rowIndex in range(0, nRows):
        item = str(table.item(rowIndex, itemColumn).text())
        checkState = table.item(rowIndex, checkBoxColumn).checkState()
        if checkState:
            checks.append(item)
    return checks

def setupDataGrid(records, columns, grid):
    """Populate a data grid. "colums" is a list of widget factory objects."""
    #Build the header row
    for(column, attr) in enumerate(columns):
        item = grid.itemAtPosition(0, column)
        if item:
            grid.removeItem(item)
            item.widget().hide()
        grid.addWidget(attr.headerWidget(), 0, column)

    #Build the data rows
    for(row, record) in enumerate(records):
        for(column, attr) in enumerate(columns):
            item = grid.itemAtPosition(row + 1, column)
            if item:
                grid.removeItem(item)
                item.widget().hide()
            grid.addWidget(attr.dataWidget(record),row + 1, column,)

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())

def loadLog(record):
    logFile = record.logFile
    if logFile:
        logFile = os.path.abspath(logFile)
        lSplit = logFile.split("\\")
        lSplit[0] = "\\\\{0}".format(record.host)
        logFile = "\\".join(lSplit)
        logFile = os.path.abspath(logFile)
        if os.path.exists(logFile):
            logger.info("Opening Log File @ {0}".format(str(logFile)))
            webbrowser.open(logFile)
        else:
            aboutBox("Invalid Log File Path",
                    "Invalid log file path for task: {0}".format(record.id))
            logger.error("Invalid log file path for task: {0}".format(record.id))
            logger.error(logFile)
    else:
        aboutBox("No Log on File",
                "No log on file for task: {0}\nJob was probably never started or was recently reset.".format(record.id))
        logger.warning("No log file on record for task: {0}".format(record.id))

niceColors = {PAUSED: QColor(240,230,200),      #Light Orange
             READY: QColor(255,255,255),        #White
             FINISHED: QColor(200,240,200),     #Light Green
             KILLED: QColor(240,200,200),       #Light Red
             CRASHED: QColor(220,90,90),        #Dark Red
             STARTED: QColor(200,220,240),      #Light Blue
             ERROR: QColor(220,90,90),          #Red
             MANAGED: QColor(240,230,200),      #Light Orange
             IDLE: QColor(255,255,255),         #White
             OFFLINE: QColor(220,220,220),      #Gray
             PENDING: QColor(240,230,200),      #Orange
             TIMEOUT: QColor(220,90,90),        #Dark Red
             }

#------------------------------------------------------------------------#
#----------------------------------MAIN----------------------------------#
#------------------------------------------------------------------------#

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FarmView()
    window.show()
    retcode = app.exec_()
    sys.exit(retcode)
