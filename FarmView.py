#Standard
import sys
import os
import fnmatch
import webbrowser
from exceptions import NotImplementedError
import datetime
import functools
import re
from socket import error as socketerror

#3rd party
from MySQLdb import Error as sqlerror

#Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from UI_FarmView import Ui_FarmView
from TaskSearchDialog import TaskSearchDialog
from JobFilterDialog import JobFilterDialog

#Hydra
from MySQLSetup import *
from LoggingSetup import logger
from MessageBoxes import aboutBox, yesNoBox, intBox, strBox
import Utils
import TaskUtils
import JobUtils
import NodeUtils

#Parts taken from Cogswell's Project Hydra by David Gladstein and Aaron Cohn

class FarmView(QMainWindow, Ui_FarmView):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        #My UI Setup Functions
        self.setupTables()
        self.connectButtons()

        #Enable this node buttons
        self.thisNodeButtonsEnabled = True

        #Get user
        self.username = getDbInfo()[2]

        #Globals for filters
        self.filters = None
        self.userFilter = True
        self.showArchivedFilter = False
        
        self.statusMsg = ""

        #Partial applications for convenience
        self.sqlErrorBox = (
            functools.partial(aboutBox, parent=self, title="Error",
                        msg="There was a problem while trying to fetch info"
                        " from the database. Check the FarmView log file for"
                        " more details about the error."))
        self.noneCheckedBox = (
            functools.partial(aboutBox, parent=self, title="None checked",
                        msg= "No nodes have been selected. Use the check boxes"
                        " to make a selection from the table."))

        #And Hydra said "Let there be data"
        self.doFetch()
        #And there was data
        #And Hydra saw the data
        #And it was(hopefully) good


    #---------------------------------------------------------------------#
    #--------------------------UI SETUP FUNCTIONS-------------------------#
    #---------------------------------------------------------------------#
    def setupTables(self):
        # Column widths on the render node table
        self.renderNodeTable.setColumnWidth(0, 30)  # check boxes
        self.renderNodeTable.setColumnWidth(1, 200) # host
        self.renderNodeTable.setColumnWidth(2, 70)  # status
        self.renderNodeTable.setColumnWidth(3, 70)  # task id
        self.renderNodeTable.setColumnWidth(4, 110) # minPriority
        self.renderNodeTable.setColumnWidth(5, 200) # capabilities
        self.renderNodeTable.setColumnWidth(6, 80)  # version
        self.renderNodeTable.setColumnWidth(7, 110) # heartbeat

        #Column widths on jobTable
        self.jobTable.setColumnWidth(0, 60)         #Job ID
        self.jobTable.setColumnWidth(1, 60)         #Status
        self.jobTable.setColumnWidth(2, 60)         #Priority
        self.jobTable.setColumnWidth(4, 80)         #Tasks
        self.jobTable.sortItems(0, order = Qt.DescendingOrder)

        # Column widths on the taskTable
        self.taskTable.setColumnWidth(0, 60)        #ID
        self.taskTable.setColumnWidth(1, 60)        #Frame
        self.taskTable.setColumnWidth(2, 100)       #Host
        self.taskTable.setColumnWidth(3, 60)        #Status
        self.taskTable.setColumnWidth(4, 120)       #Start Time
        self.taskTable.setColumnWidth(5, 120)       #End Time
        self.taskTable.setColumnWidth(6, 120)       #Duration
        self.taskTable.setColumnWidth(7, 120)       #Code

        #Get the global column count for later
        self.taskTableCols = self.taskTable.columnCount()

    def connectButtons(self):
        #Connect buttons in This Node tab
        QObject.connect(self.fetchButton, SIGNAL("clicked()"), self.doFetch)
        QObject.connect(self.onlineThisNodeButton, SIGNAL("clicked()"),
                        self.onlineThisNodeButtonClicked)
        QObject.connect(self.offlineThisNodeButton, SIGNAL("clicked()"),
                        self.offlineThisNodeButtonClicked)
        QObject.connect(self.getOffThisNodeButton, SIGNAL("clicked()"),
                        self.getOffThisNodeButtonClicked)

        #Connect buttons in RenderNode tab
        QObject.connect(self.onlineRenderNodesButton, SIGNAL("clicked()"),
                        self.onlineRenderNodesButtonClicked)
        QObject.connect(self.offlineRenderNodesButton, SIGNAL("clicked()"),
                        self.offlineRenderNodesButtonClicked)
        QObject.connect(self.getOffRenderNodesButton, SIGNAL("clicked()"),
                        self.getOffRenderNodesButtonClicked)
        QObject.connect(self.selectAllNodesButton, SIGNAL("clicked()"),
                        self.selectAllNodesButtonHandler)
        QObject.connect(self.selectNoneNodesButton, SIGNAL("clicked()"),
                        self.selectNoneNodesButtonHandler)
        QObject.connect(self.selectByHostButton, SIGNAL("clicked()"),
                        self.selectByHostButtonHandler)
                        
        #Connect actions in Job View
        QObject.connect(self.jobTable, SIGNAL ("cellClicked(int,int)"),
                self.jobCellClickedHandler)
        
        #Connect Context Menus
        self.jobTable.setContextMenuPolicy(Qt.CustomContextMenu) 
        self.jobTable.customContextMenuRequested.connect(self.jobContextHandler)
        
        self.taskTable.setContextMenuPolicy(Qt.CustomContextMenu) 
        self.taskTable.customContextMenuRequested.connect(self.taskContextHandler)

    #---------------------------------------------------------------------#
    #-------------------------JOB BUTTON HANDLERS-------------------------#
    #---------------------------------------------------------------------#

    def doNothing(self):
        pass
        
    def resetStatusBar(self):
        self.statusbar.showMessage(self.statusMsg)

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
        
        addItem("Start Jobs", self.startJobButtonHandler, "Start all jobs selected in Job List")
        addItem("Pause Jobs", self.pauseJobButtonHandler, "Pause all jobs selected in Job List")
        addItem("Kill Jobs", self.killJobButtonHandler, "Kill all jobs selected in Job List")
        addItem("Reset Jobs", self.resetJobButtonHandler, "Reset all jobs selected in Job List")
        addItem("Start Test Frames...", self.callTestFrameBox, "Open a dialog to start the first X frames in each job selected in the Job List")
        self.jobMenu.addSeparator()
        addItem("Toggle Archive", self.toggleArchiveButtonHandler, "Toggle the Archived status on each job selected int he Job List")
        self.jobMenu.addSeparator()
        editJob = addItem("Edit Job...", self.doNothing, "Edit Job, WIP")
        editJob.setEnabled(False)
        self.jobMenu.addSeparator()
        
        userFilterAction = addItem("Only Show My Jobs", self.userFilterActionHandler, "Only show the jobs belonging to the current user")
        userFilterAction.setCheckable(True)
        if self.userFilter == True:
            userFilterAction.setChecked(True)
            
        archivedFilterAction = addItem("Show Archived Jobs", self.archivedFilterActionHandler, "Show jobs which have been archived")
        archivedFilterAction.setCheckable(True)
        if self.showArchivedFilter == True:
            archivedFilterAction.setChecked(True)
            
        addItem("Filters...", self.filterJobButtonHandler, "Open filters dialog to select which types of jobs are shown in the Job List")
        self.jobMenu.popup(QCursor.pos())
    
    def userFilterActionHandler(self):
        if self.userFilter == True:
            self.userFilter = False
        else:
            self.userFilter = True
        self.updateJobTable()

    def archivedFilterActionHandler(self):
        if self.showArchivedFilter == True:
            self.showArchivedFilter = False
        else:
            self.showArchivedFilter = True
        self.updateJobTable()
        
    def jobCommandBuilder(self):
        command = "WHERE"
        if self.filters != None:
            checkboxKeys = ["C", "E", "F", "K", "R", "S", "U"]
            users = self.filters["owner"].split(",")
            names = self.filters["name"].split(",")
            statuses = self.filters["status"]
            limit = self.filters["limit"]
            if users[0] != "":
                command += " owner = '%s'" % users[0]
                for user in users[1:]:
                    command += " OR owner = '%s'" % user
            if names[0] != "":
                if command != "WHERE":
                    command += " AND"
                command += " niceName LIKE '%s'" % names[0]
                for name in names[1:]:
                    command += " OR niceName LIKE '%s'" % name
            if False in statuses:
                idx = 0
                for i in range(len(statuses)):
                    if statuses[i] == False:
                        if command != "WHERE" and idx == 0:
                            command += " AND"
                        if idx == 0:
                            command += " job_status <> '%s'" % checkboxKeys[i]
                            idx += 1
                        else:
                            command += " AND job_status <> '%s'" % checkboxKeys[i]
                            idx += 1
        #TODO: Clean this up, have to check to see if owner is already in the
        #the query instead of just checking to see if the query is default
        if command == "WHERE":
            if self.userFilter:
                command += " owner = '%s'" % self.username
            if not self.showArchivedFilter:
                if command != "WHERE":
                    command += " AND"
                command += " archived = 0"

        if self.filters != None:
            command += " LIMIT 0,%d" % limit
            
        if command == "WHERE":
            command = ""
            
        return command


    def updateJobTable(self):
        self.jobTable.setSortingEnabled(False)
        command = self.jobCommandBuilder()
        try:
            jobs = hydra_jobboard.fetch(command)
            self.jobTable.setRowCount(len(jobs))
            for pos, job in enumerate(jobs):
                if job.totalTask > 0:
                    percent = "{0:.0%}".format(float(job.taskDone / job.totalTask))
                    taskString  = "%s (%d/%d)" % (percent, job.taskDone, job.totalTask)
                else:
                    taskString = "0% (0/0)"
                self.jobTable.setItem(pos, 0, TableWidgetItem_int(str(job.id)))
                self.jobTable.setItem(pos, 1, TableWidgetItem_int(str(niceNames[job.job_status])))
                self.jobTable.item(pos, 1).setBackgroundColor(niceColors[job.job_status])
                self.jobTable.setItem(pos, 2, TableWidgetItem_int(str(job.priority)))
                self.jobTable.setItem(pos, 3, TableWidgetItem(str(job.owner)))
                self.jobTable.setItem(pos, 4, TableWidgetItem(taskString))
                self.jobTable.setItem(pos, 5, TableWidgetItem(str(job.niceName)))
                if job.archived == 1:
                    self.jobTable.item(pos, 0).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 2).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 3).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 4).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 5).setBackgroundColor(QColor(220,220,220))
                if job.owner == self.username and self.userFilter == False:
                    self.jobTable.item(pos, 3).setBackgroundColor(QColor(225,240,225))
        except sqlerror as err:
            logger.debug(str(err))
            aboutBox(self, "SQL error", str(err))
        self.jobTable.setSortingEnabled(True)

    def updateJobRow(self, row):
        job_id = int(self.jobTable.item(row, 0).text())
        try:
            [job] = hydra_jobboard.fetch("WHERE id = '%d'" % job_id)
            pos = row
            if job.totalTask > 0:
                percent = "{0:.0%}".format(float(job.taskDone / job.totalTask))
                taskString  = "%s (%d/%d)" % (percent, job.taskDone, job.totalTask)
            else:
                taskString = "0% (0/0)"
            self.jobTable.setItem(pos, 0, TableWidgetItem_int(str(job.id)))
            self.jobTable.setItem(pos, 1, TableWidgetItem_int(str(niceNames[job.job_status])))
            self.jobTable.item(pos, 1).setBackgroundColor(niceColors[job.job_status])
            self.jobTable.setItem(pos, 2, TableWidgetItem_int(str(job.priority)))
            self.jobTable.setItem(pos, 3, TableWidgetItem(str(job.owner)))
            self.jobTable.setItem(pos, 4, TableWidgetItem(taskString))
            self.jobTable.setItem(pos, 5, TableWidgetItem(str(job.niceName)))
            if job.archived == 1:
                self.jobTable.item(pos, 0).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 2).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 3).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 4).setBackgroundColor(QColor(220,220,220))
                self.jobTable.item(pos, 5).setBackgroundColor(QColor(220,220,220))
            if job.owner == self.username and self.userFilter == False:
                self.jobTable.item(pos, 3).setBackgroundColor(QColor(225,240,225))
        except sqlerror as err:
            logger.debug(str(err))
            aboutBox(self, "SQL error", str(err))

    def jobTableHandler(self):
        self.resetStatusBar()
        rows = self.jobTable.selectionModel().selectedRows()
        if len(rows) < 1:
            aboutBox(title="Selection Error", msg = "Please select something from the Job Table and try again.")
            return None
        return [item.row() for item in rows]

    def startJobButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            JobUtils.startJob(job_id)
        self.updateJobTable()
        self.jobCellClickedHandler(rows[-1])
        self.jobTable.setCurrentCell(rows[-1], 0)

    def killJobButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really kill the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    no_errors = True
                    if not JobUtils.killJob(job_id):
                        no_errors = False
            except sqlerror as err:
                logger.debug(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if no_errors ==  False:
                    aboutBox(self, "Error", "One or more nodes couldn't kill their tasks.")
                self.updateJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def pauseJobButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really pause the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    no_errors = True
                    if not JobUtils.killJob(job_id, "U"):
                        no_errors = False
            except sqlerror as err:
                logger.debug(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if no_errors ==  False:
                    aboutBox(self, "Error", "One or more nodes couldn't kill their tasks.")
                self.updateJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def resetJobButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    tasks = hydra_taskboard.fetch("WHERE job_id = '%d'" % job_id)
                    for task in tasks:
                        TaskUtils.resetTask(task.id, "U")
            except sqlerror as err:
                logger.debug(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.updateJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)

    def setPriorityButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            JobUtils.prioritizeJob(job_id, self.prioritySpinBox.value())
        self.updateJobTable()
        self.jobTable.setCurrentCell(rows[-1], 0)

    def toggleArchiveButtonHandler(self):
        rows = self.jobTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really archive or unarchive the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                commandList = []
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    [job] = hydra_jobboard.fetch("WHERE id = '%d'" % job_id)
                    if job.archived == 1:
                        new = 0
                    else:
                        new = 1
                    job_command = "UPDATE hydra_jobboard SET archived = '%d' WHERE id = '%d'" % (new, job_id)
                    task_command = "UPDATE hydra_taskboard SET archived = '%d' WHERE job_id = '%d'" % (new, job_id)
                    commandList.append(job_command)
                    commandList.append(task_command)

                with transaction() as t:
                    for cmd in commandList:
                        t.cur.execute(cmd)

            except sqlerror as err:
                logger.debug(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.updateJobTable()
                self.jobCellClickedHandler(rows[-1])
                self.jobTable.setCurrentCell(rows[-1], 0)
    #---------------------------------------------------------------------#
    #------------------------TASK BUTTON HANDLERS-------------------------#
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
        
        addItem("Start Tasks", self.startTaskButtonHandler, "Start all tasks selected in the Task List")
        addItem("Pause Tasks", self.pauseTaskButtonHandler, "Pause all tasks selected in the Task List")
        addItem("Kill Tasks", self.killTaskButtonHandler, "Kill all tasks selected in the Task List")
        addItem("Reset Tasks", self.resetTaskButtonHandler, "Reset all tasks selected in the Task List")
        self.taskMenu.addSeparator()
        addItem("Load LogFile", self.loadLogButtonHandler, "Load the log file for all tasks selected in the Task List")
        self.taskMenu.popup(QCursor.pos())

    def updateTaskTable(self, job_id):
        self.taskTableLabel.setText("Task List (Job ID: " + str(job_id) + ")")
        try:
            tasks = hydra_taskboard.fetch("WHERE job_id = %d" % job_id)
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
                self.taskTable.setItem(pos, 1, TableWidgetItem_int(str(task.frame)))
                self.taskTable.setItem(pos, 2, TableWidgetItem(str(task.host)))
                self.taskTable.setItem(pos, 3, TableWidgetItem(str(niceNames[task.status])))
                self.taskTable.item(pos, 3).setBackgroundColor(niceColors[task.status])
                self.taskTable.setItem(pos, 4, TableWidgetItem_dt(str(task.startTime)))
                self.taskTable.setItem(pos, 5, TableWidgetItem_dt(str(task.endTime)))
                self.taskTable.setItem(pos, 6, TableWidgetItem_dt(str(tdiff)))
                self.taskTable.setItem(pos, 7, TableWidgetItem_int(str(task.exitCode)))
                self.taskTable.setItem(pos, 8, TableWidgetItem_int(reqsString))

        except sqlerror as err:
            aboutBox(self, "SQL Error", str(err))

    def jobCellClickedHandler(self, row):
        item = self.jobTable.item(row, 0)
        job_id = int(item.text())
        self.updateTaskTable(job_id)
        self.updateJobRow(row)

    def reloadTaskTable(self):
        row = self.jobTable.selectionModel().selectedRows()[0].row()
        self.jobCellClickedHandler(row)

    def taskTableHandler(self):
        self.resetStatusBar()
        rows = self.taskTable.selectionModel().selectedRows()
        if len(rows) < 1:
            aboutBox(title="Selection Error", msg = "Please select something from the Job Table and try again.")
            return None
        return [item.row() for item in rows]

    def startTaskButtonHandler(self):
        rows = self.taskTableHandler()
        if rows == None:
            return
        for row in rows:
            task_id = int(self.taskTable.item(row, 0).text())
            TaskUtils.startTask(task_id)
        self.reloadTaskTable()

    def resetTaskButtonHandler(self):
        rows = self.taskTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                TaskUtils.resetTask(task_id, "U")
            self.reloadTaskTable()

    def callTestFrameBox(self):
        try:
            rows = self.jobTableHandler()
            if rows == None:
                return
            row = rows[0]
            reply = intBox(self, "StartTestFrames", "Start X Test Frames?", 10)
            if reply[1]:
                job_id = int(self.jobTable.item(row, 0).text())
                logger.info("Starting %d test frames on job_id %d" % (reply[0], job_id))
                tasks = hydra_taskboard.fetch ("WHERE job_id = %d" % job_id)
                for task in tasks[0:reply[0]]:
                    TaskUtils.startTask(task.id)
                logger.info("Test Tasks Started!")
                with transaction() as t:
                    [job] = hydra_jobboard.fetch("WHERE id = '%d'" % job_id)
                    job.job_status = "S"
                    job.update(t)
                self.updateJobTable()
                self.jobCellClickedHandler(row)
                self.jobTable.setCurrentCell(row, 0)
            else:
                logger.info("No test tasks started.")
        except IndexError:
            aboutBox(self, "Error", "Make a slection in the job table to continue...")

    def killTaskButtonHandler(self):
        rows = self.taskTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really kill selected tasks?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                try:
                    killed = TaskUtils.killTask(task_id)
                    if not killed:
                        aboutBox(self, "Error", "Task couldn't be killed for ""some reason.")
                except socketerror as err:
                    logger.debug(str(err))
                    aboutBox(self, "Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.debug(str(err))
                    aboutBox(self, "SQL Error", str(err))
        self.reloadTaskTable()

    def pauseTaskButtonHandler(self):
        rows = self.taskTableHandler()
        if rows == None:
            return
        choice = yesNoBox(self, "Confirm", "Really pause selected tasks?")
        if choice == QMessageBox.Yes:
            for row in rows:
                task_id = int(self.taskTable.item(row, 0).text())
                try:
                    killed = TaskUtils.killTask(task_id, "U")
                    if not killed:
                        aboutBox(self, "Error", "Task couldn't be killed for ""some reason.")
                except socketerror as err:
                    logger.debug(str(err))
                    aboutBox(self, "Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.debug(str(err))
                    aboutBox(self, "SQL Error", str(err))
        self.reloadTaskTable()

    def loadLogButtonHandler(self):
        rows = self.taskTableHandler()
        if rows == None:
            return
        if len(rows) > 1:
            choice = yesNoBox(self, "Open logs?", "Note, this will open a text editor for EACH task selected. Continue?")
            if choice == QMessageBox.Yes:
                for row in rows:
                    task_id = int(self.taskTable.item(row, 0).text())
                    [taskOBJ] = hydra_taskboard.fetch("WHERE id = '%d'" % task_id)
                    loadLog(taskOBJ)
        else:
            task_id = int(self.taskTable.item(rows[0], 0).text())
            [taskOBJ] = hydra_taskboard.fetch("WHERE id = '%d'" % task_id)
            loadLog(taskOBJ)

    def advancedSearchButtonClicked(self):
        results = TaskSearchDialog.create()
        logger.error("Not Implemeted!")
        print results

    def filterJobButtonHandler(self):
        self.filters = JobFilterDialog.create(self.filters)
        #logger.debug(self.filters)
        logger.debug(self.jobCommandBuilder())
        self.updateJobTable()

    def searchByTaskID(self):
        """Given a task id, finds the job, selects it in the job table, and
        displays the tasks for that job, including the one searched for. Does
        nothing if task id doesn't exist."""

        #Retrieve job id by task id in the database
        task_id = str(self.taskIDLineEdit.text())
        if task_id:
            with transaction() as t:
                query = "SELECT job_id FROM hydra_taskboard WHERE id = %s"
                t.cur.execute(query % task_id)
                job_id = t.cur.fetchall()

                if not job_id:
                    aboutBox(self, "Error", "The given task ID does not "
                             "correspond to an existing job.")
                    return

                #Find item with matching job id in the table
                ((job_id,),) = job_id # unpack -- TODO: fix this hack?
                [item] = self.jobTable.findItems(str(job_id), Qt.MatchExactly)

                #Select the row and trigger the update for the task list
                self.jobTable.setCurrentItem(item)
                self.jobCellClickedHandler(item.row())
                [item] = self.taskTable.findItems(str(task_id), Qt.MatchExactly)
                self.taskTable.setCurrentItem(item)
        else:
            aboutBox(self, "Error", "No task ID was entered.")
            return

    #---------------------------------------------------------------------#
    #------------------------NODE BUTTON HANDLERS-------------------------#
    #---------------------------------------------------------------------#

    def onlineThisNodeButtonClicked(self):
        """Changes the local render node's status to online if it was offline,
        goes back to started if it was pending offline."""
        #Get most current info from the database
        thisNode = None
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.debug(str(err))
            self.sqlErrorBox()
            return

        if thisNode:
            NodeUtils.onlineNode(thisNode)

        self.doFetch()

    def offlineThisNodeButtonClicked(self):
        """Changes the local render node's status to offline if it was idle,
        pending if it was working on something."""
        #Get the most current info from the database
        thisNode = None
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.debug(str(err))
            self.sqlErrorBox()
            return

        if thisNode:
            NodeUtils.offlineNode(thisNode)

        self.doFetch()

    def getOffThisNodeButtonClicked(self):
        #TODO: TEST THIS FUNCTION
        """***UNTESTED***Offlines the node and sends a message to the render node server
        running on localhost to kill its current task(task will be
        resubmitted)"""
        thisNode = None
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.debug(str(err))
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
                            logger.debug("Problem killing task durring GetOff")
                            aboutBox(self, "Error", "There was a problem killing the task during GetOff!")
                        else:
                            aboutBox(self, "Success", "Job was reset, node offlined.")
                    except socketerror:
                        logger.debug(socketerror.message)
                        aboutBox(self, "Error", "There was a problem communicating"
                                 " with the render node software. Either it's not"
                                 " running, or it has become unresponsive.")
                else:
                    aboutBox(self, "Success", "No job was found on node, node offlined")
                self.doFetch()

    def onlineRenderNodesButtonClicked(self):
        """For all nodes with boxes checked in the render nodes table, changes
        status to online."""
        hosts = getCheckedItems(table=self.renderNodeTable, itemColumn=1, checkBoxColumn=0)
        if len(hosts) == 0:
            self.noneCheckedBox()
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes? <br>" + str(hosts))

        if choice != QMessageBox.Yes:
            aboutBox(self, "Aborted", "No action taken.")
            return

        with transaction() as t:
            rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            for node_row in rendernode_rows:
                if node_row.host in hosts:
                    NodeUtils.onlineNode(node_row)
        self.doFetch()

    def offlineRenderNodesButtonClicked(self):
        """For all nodes with boxes checked in the render nodes table, changes
        status to offline if idle, or pending if started."""
        hosts = getCheckedItems(table=self.renderNodeTable, itemColumn=1, checkBoxColumn=0)
        if len(hosts) == 0:
            self.noneCheckedBox()
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

    def getOffRenderNodesButtonClicked(self):
        #TODO:TEST FUNCTION!
        """***UNTESTED***For all nodes with boxes checked in the render nodes table, changes
        status to offline if idle, or pending if started, and attempts to kill
        any task that is running on each node."""

        hosts = getCheckedItems(table=self.renderNodeTable, itemColumn=1, checkBoxColumn=0)
        if len(hosts) == 0:
            self.noneCheckedBox()
            return

        choice = yesNoBox(self, "Confirm", "<B>WARNING</B>: All progress on"
                          " current tasks will be lost for the selected"
                          " render nodes. Are you sure you want to stop these"
                          " nodes? <br>" + str(hosts))

        if choice != QMessageBox.Yes:
            aboutBox(self, "Aborted", "No action taken.")
            return

        error = False
        notKilledList = list()
        with transaction() as t:
            rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            for thisNode in rendernode_rows:
                if thisNode.host in hosts:
                    NodeUtils.offlineNode(thisNode)
                    if thisNode.task_id:
                        task_id = thisNode.task_id
                        try:
                            response = TaskUtils.killTask(task_id)
                            TaskUtils.startTask(task_id)
                            if not response:
                                logger.debug("Problem killing task durring GetOff")
                                aboutBox(self, "Error", "There was a problem killing the task during GetOff!")
                            else:
                                aboutBox(self, "Success", "Job was reset, node offlined.")
                        except socketerror:
                            logger.debug(socketerror.message)
                            aboutBox(self, "Error", "There was a problem communicating"
                                     " with the render node software. Either it's not"
                                     " running, or it has become unresponsive.")
                    else:
                        aboutBox(self, "Success", "No job was found on node, node offlined")

        self.doFetch()

    def selectAllNodesButtonHandler(self):
        rows = self.renderNodeTable.rowCount()
        for rowIndex in range(0, rows):
            item = self.renderNodeTable.item(rowIndex, 0)
            item.setCheckState(Qt.Checked)

    def selectNoneNodesButtonHandler(self):
        rows = self.renderNodeTable.rowCount()
        for rowIndex in range(0, rows):
            item = self.renderNodeTable.item(rowIndex, 0)
            item.setCheckState(Qt.Unchecked)

    def selectByHostButtonHandler(self):
        reply = strBox(self, "Select By Host Name", "Host (using * as wildcard):")
        if reply[1]:
            searchString = str(reply[0])
            rows = self.renderNodeTable.rowCount()
            for rowIndex in range(0, rows):
                item = str(self.renderNodeTable.item(rowIndex, 1).text())
                if fnmatch.fnmatch(item, searchString):
                    self.renderNodeTable.item(rowIndex, 0).setCheckState(Qt.Checked)
                    logger.debug("Selecting %s matched with %s" % (item, searchString))

    #---------------------------------------------------------------------#
    #--------------------------UPDATE HANDLERS----------------------------#
    #---------------------------------------------------------------------#

    def doFetch(self):
        """Aggregate method for updating all of the widgets."""
        try:
            self.updateThisNodeInfo()
            self.updateRenderNodeTable()
            self.updateRenderTaskGrid()
            self.updateJobTable()
            self.updateStatusBar()
        except sqlerror as err:
            logger.debug(str(err))
            self.sqlErrorBox()

    def updateThisNodeInfo(self):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        #If the buttons are disabled, don't bother
        if not self.thisNodeButtonsEnabled:
            return

        #Get the most current info from the database
        thisNode = None
        try:
            thisNode = NodeUtils.getThisNodeData()
        except sqlerror as err:
            logger.debug(str(err))
            self.sqlErrorBox()

        if thisNode:
            #Update the labels
            self.nodeNameLabel.setText(thisNode.host)
            self.nodeStatusLabel.setText(niceNames[thisNode.status])
            self.updateTaskIDLabel(thisNode.task_id)
            self.nodeVersionLabel.setText(getSoftwareVersionText(thisNode.software_version))
            self.updateMinPriorityLabel(thisNode.minPriority)
            self.updateCapabilitiesLabel(thisNode.capabilities)

        else:
            QMessageBox.about(self, "Notice",
                "Information about this node cannot be displayed because it is"
                "not registered on the render farm. You may continue to use"
                " Farm View, but it must be restarted after this node is "
                "registered if you wish to see this node's information.")
            self.setThisNodeButtonsEnabled(False)

    def updateTaskIDLabel(self, task_id):
        if task_id:
            self.taskIDLabel.setText(str(task_id))
        else:
            self.taskIDLabel.setText("None")

    def updateMinPriorityLabel(self, minPriority):
        self.minPriorityLabel.setText(str(minPriority))

    def updateCapabilitiesLabel(self, capabilities):
        self.capabilitiesLabel.setText(capabilities)

    def updateRenderNodeTable(self):
        #Clear the table(note: this is done to avoid duplication of items)
        self.renderNodeTable.clearContents()
        self.renderNodeTable.setRowCount(0)

        #Prevent rows from being sorted while table is populating
        self.renderNodeTable.setSortingEnabled(False)

        rows = hydra_rendernode.fetch(order="order by host")
        self.renderNodeTable.setRowCount(len(rows))
        columns = [
            lambda o: TableWidgetItem_check(),
            lambda o: TableWidgetItem(str(o.host)),
            lambda o: TableWidgetItem(str(niceNames[o.status])),
            lambda o: TableWidgetItem(str(o.task_id)),
            lambda o: TableWidgetItem(str(o.minPriority)),
            lambda o: TableWidgetItem(str(o.capabilities)),
            lambda o: TableWidgetItem(
                                getSoftwareVersionText(o.software_version)),
            lambda o: TableWidgetItem_dt(o.pulse),
            ]
        for(rowIndex, row) in enumerate(rows):
            for(columnIndex, columnFun) in enumerate(columns):
                columnFun(row).setIntoTable(self.renderNodeTable,
                                              rowIndex, columnIndex)

        self.renderNodeTable.setSortingEnabled(True)

    def updateRenderTaskGrid(self):
        columns = [
            labelFactory('id'),
            labelFactory('status'),
            buttonFactory('logFile', loadLog),
            labelFactory('host'),
            labelFactory('command'),
            labelFactory('startTime'),
            labelFactory('endTime'),
            labelFactory('exitCode')]
        records = (hydra_taskboard.fetch(order = "order by id desc",
        limit = self.limitSpinBox.value()))

        for task in records:
            if task.logFile:
                if task.host:
                    task.logFile = task.logFile.replace("C:", "\\\\" + task.host)

        setup(records, columns, self.taskGrid)


    def updateStatusBar(self):
        with transaction() as t:
            t.cur.execute ("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        thisNode = NodeUtils.getThisNodeData()
        logger.debug("Counts = " + str(counts))
        countString = ", ".join (["%d %s" % (count, niceNames[status])
                                  for(count, status) in counts])
        countString += ", %s %s" % (thisNode.host, niceNames[thisNode.status])
        time = datetime.datetime.now().strftime ("%H:%M")
        msg = "%s as of %s" % (countString, time)
        self.statusMsg = msg
        self.statusbar.showMessage(self.statusMsg)

    def setThisNodeButtonsEnabled(self, choice):
        """Enables or disables buttons on This Node tab"""
        self.onlineThisNodeButton.setEnabled(choice)
        self.offlineThisNodeButton.setEnabled(choice)
        self.getOffThisNodeButton.setEnabled(choice)
        self.thisNodeButtonsEnabled = choice

#------------------------------------------------------------------------#
#---------------------------EXTERNAL FUNCTIONS---------------------------#
#------------------------------------------------------------------------#

def getSoftwareVersionText(sw_ver):
    """Given the software_version attribute of a hydra_rendernode row, returns
    a string suitable for display purposes."""

    #Get RenderNodeMain version number if exists
    if sw_ver:

        #Case 1: executable in a versioned directory
        v = re.search("rendernodemain-dist-([0-9]+)", sw_ver,
                        re.IGNORECASE)
        if v:
            return v.group(1)

        #Case 2: source code file
        elif re.search("rendernodemain.py$", sw_ver, re.IGNORECASE):
            return "Development source"

        #Case 3: no freakin' clue
        return sw_ver

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

def setup(records, columns, grid):
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

def loadLog(record):
    logFile = record.logFile
    if logFile:
        logFile = os.path.abspath(logFile)
        if os.path.exists(logFile):
            logger.debug("Opening Log File @ %s" % str(logFile))
            webbrowser.open(logFile)
        else:
            aboutBox(title = "Invalid Log File Path", msg = "Invalid log file path for task: %d" % record.id)
            logger.error("Invalid log file path for task: %d" % record.id)
    else:
        aboutBox(title = "No Log on File", msg = "No log on file for task: %d\nJob was probably never started or was recently reset." % record.id)
        logger.info("No log file on record for task: %d" % record.id)


#------------------------------------------------------------------------#
#-------------------------------UI CLASSES-------------------------------#
#------------------------------------------------------------------------#

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

class versionLabelFactory(widgetFactory):
    """Builds a label specially for the software_version column in the render
    node table, trimming out non-essential information in the process."""

    def dataWidget(self, record):
        sw_version_text = getSoftwareVersionText(self.data(record))
        return QLabel(sw_version_text)

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
        logger.debug('clobber %s', record.host)

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

niceColors = {PAUSED: QColor(240,230,200),      #Light Orange
             READY: QColor(255,255,255),         #White
             FINISHED: QColor(200,240,200),      #Light Green
             KILLED: QColor(240,200,200),        #Light Red
             CRASHED: QColor(220,90,90),         #Dark Red
             STARTED: QColor(200,220,240),       #Light Blue
             ERROR: QColor(220,90,90),           #Red
             HOLD: QColor(255,255,255),          #White, placeholder
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
