"""The software for managing jobs, tasks, and nodes."""
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




#------------------------------------------------------------------------------#
#--------------------------------Farm View-------------------------------------#
#------------------------------------------------------------------------------#

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
        self.userFilter = False
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
        
    def closeEvent(self, event):
        event.accept()
        sys.exit(0)


    #---------------------------------------------------------------------#
    #--------------------------UI SETUP FUNCTIONS-------------------------#
    #---------------------------------------------------------------------#
    def setupTables(self):
        # Column widths on the render node table
        self.renderNodeTable.setColumnWidth(0, 30)  # check boxes
        self.renderNodeTable.setColumnWidth(1, 200) # host
        self.renderNodeTable.setColumnWidth(2, 70)  # status
        self.renderNodeTable.setColumnWidth(3, 70)  # task id
        self.renderNodeTable.setColumnWidth(4, 80) # minPriority
        self.renderNodeTable.setColumnWidth(5, 500) # capabilities
        self.renderNodeTable.setColumnWidth(6, 60)  # version
        self.renderNodeTable.setColumnWidth(7, 110) # heartbeat

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

        #Get the global column count for later
        self.taskTableCols = self.taskTable.columnCount()

    def connectButtons(self):
        #Connect buttons in This Node tab
        QObject.connect(self.fetchButton, SIGNAL("clicked()"), self.doFetch)
        QObject.connect(self.onlineThisNodeButton, SIGNAL("clicked()"),
                        self.onlineThisNodeHandler)
        QObject.connect(self.offlineThisNodeButton, SIGNAL("clicked()"),
                        self.offlineThisNodeHandler)
        QObject.connect(self.getOffThisNodeButton, SIGNAL("clicked()"),
                        self.getOffThisNodeHandler)
                        
        #Connect basic filter checkboxKeys
        QObject.connect(self.archivedCheckBox, SIGNAL("stateChanged(int)"),
                        self.archivedFilterActionHandler)
        QObject.connect(self.userFilterCheckbox, SIGNAL("stateChanged(int)"),
                        self.userFilterActionHandler)
                        
        #Connect actions in Job View
        QObject.connect(self.jobTable, SIGNAL ("cellClicked(int,int)"),
                self.jobCellClickedHandler)
        
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
        
        addItem("Fetch", self.doFetch, "Fetch the latest information from the Database")
        self.centralMenu.addSeparator()
        onAct = addItem("Online This Node", self.onlineThisNodeHandler, "Online This Node")
        offAct = addItem("Offline This Node", self.offlineThisNodeHandler, "Wait for the current job to finish then offline this node")
        getAct = addItem("Get Off This Node!", self.getOffThisNodeHandler, "Kill the current task and offline this node immediately")
        
        if not self.thisNodeButtonsEnabled:
            onAct.setEnabled(False)
            offAct.setEnabled(False)
            getAct.setEnabled(False)
        
        self.centralMenu.popup(QCursor.pos())

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
        
        addItem("Fetch", self.doFetch, "Fetch the latest information from the Database")
        self.jobMenu.addSeparator()
        addItem("Start Jobs", self.startJobHandler, "Start all jobs selected in Job List")
        addItem("Pause Jobs", self.pauseJobHandler, "Pause all jobs selected in Job List")
        addItem("Kill Jobs", self.killJobHandler, "Kill all jobs selected in Job List")
        addItem("Reset Jobs", self.resetJobHandler, "Reset all jobs selected in Job List")
        addItem("Start Test Frames...", self.callTestFrameBox, "Open a dialog to start the first X frames in each job selected in the Job List")
        self.jobMenu.addSeparator()
        addItem("Toggle Archive", self.toggleArchiveHandler, "Toggle the Archived status on each job selected in he Job List")
        addItem("Reset Node Limit", self.resetNodeManagementHandler, "Reset the number of tasks which are ready to match the limit of the number of concurant tasks.")
        self.jobMenu.addSeparator()
        #setJobPriorityHandler
        addItem("Set Job Priority...", self.setJobPriorityHandler, "Set priority on each job selected in the Job List")
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
            
        addItem("Filters...", self.filterJobHandler, "Open filters dialog to select which types of jobs are shown in the Job List")
        self.jobMenu.popup(QCursor.pos())
    
    def userFilterActionHandler(self):
        if self.userFilter == True:
            self.userFilter = False
            self.userFilterCheckbox.setChecked(0)
        else:
            self.userFilter = True
            self.userFilterCheckbox.setChecked(2)
        self.updateJobTable()
        self.resetStatusBar()

    def archivedFilterActionHandler(self):
        if self.showArchivedFilter == True:
            self.showArchivedFilter = False
            self.archivedCheckBox.setChecked(0)
        else:
            self.showArchivedFilter = True
            self.archivedCheckBox.setChecked(2)
        self.updateJobTable()
        self.resetStatusBar()
        
    def jobCommandBuilder(self):
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
                    if statuses[i] == False:
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

        if self.filters != None:
            command += " LIMIT 0,{0}".format(limit)
            
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
                if job.tasksTotal > 0:
                    percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
                    taskString  = "{0} ({1}/{2})".format(percent, job.tasksComplete, job.tasksTotal)
                else:
                    taskString = "0% (0/0)"
                self.jobTable.setItem(pos, 0, TableWidgetItem_int(str(job.id)))
                self.jobTable.setItem(pos, 1, TableWidgetItem_int(str(job.priority)))
                self.jobTable.setItem(pos, 2, TableWidgetItem_int(str(niceNames[job.job_status])))
                self.jobTable.item(pos, 2).setBackgroundColor(niceColors[job.job_status])
                self.jobTable.setItem(pos, 3, TableWidgetItem(str(job.owner)))
                self.jobTable.setItem(pos, 4, TableWidgetItem(taskString))
                self.jobTable.setItem(pos, 5, TableWidgetItem(str(job.niceName)))
                if job.owner == self.username:
                    self.jobTable.item(pos, 3).setFont(QFont('Segoe UI', 8, QFont.DemiBold))
                if job.archived == 1:
                    self.jobTable.item(pos, 0).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 1).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 3).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 4).setBackgroundColor(QColor(220,220,220))
                    self.jobTable.item(pos, 5).setBackgroundColor(QColor(220,220,220))
                    
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
        self.jobTable.setSortingEnabled(True)

    def updateJobRow(self, row):
        job_id = int(self.jobTable.item(row, 0).text())
        JobUtils.updateJobTaskCount(job_id)
        try:
            [job] = hydra_jobboard.fetch("WHERE id = '{0}'".format(job_id))
            pos = row
            if job.tasksTotal > 0:
                percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
                taskString  = "{0} ({1}/{2})".format(percent, job.tasksComplete, job.tasksTotal)
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
            aboutBox(title="Selection Error", msg = "Please select something from the Job Table and try again.")
            return None
        return [item.row() for item in rows]

    def startJobHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            JobUtils.startJob(job_id)
        self.updateJobTable()
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
                    response = False
                    if JobUtils.killJob(job_id):
                        response = True
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if response:
                    aboutBox(self, "Error", "One or more nodes couldn't kill their tasks.")
                self.updateJobTable()
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
                    aboutBox(self, "Error", "One or more nodes couldn't kill their tasks.")
                self.updateJobTable()
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
                        aboutBox(title = "Reset Job Error",
                        msg = "Could not reset task(s) under job {0} becase of error(s) communicating with their host(s)".format(job_id))
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.updateJobTable()
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
        
        self.updateJobTable()
        self.jobCellClickedHandler(rows[-1])
        self.jobTable.setCurrentCell(rows[-1], 0)

    def setJobPriorityHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        for row in rows:
            job_id = int(self.jobTable.item(row, 0).text())
            msgString = "Priority for job {0}:".format(job_id)
            #TODO:Get current priority
            reply = intBox(self, "Set Job Priority", msgString , 50)
            if reply[1]:
                JobUtils.prioritizeJob(job_id, reply[0])
            else:
                logger.info("prioritizeJob skipped on {0}".format(job_id))
        self.updateJobTable()
        self.jobTable.setCurrentCell(rows[-1], 0)

    def toggleArchiveHandler(self):
        rows = self.jobTableHandler()
        if not rows:
            return
        choice = yesNoBox(self, "Confirm", "Really archive or unarchive the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                commandList = []
                for row in rows:
                    job_id = int(self.jobTable.item(row, 0).text())
                    [job] = hydra_jobboard.fetch("WHERE id = '{0}'".format(job_id))
                    if job.archived == 1:
                        new = 0
                    else:
                        new = 1
                    job_command = "UPDATE hydra_jobboard SET archived = '{0}' WHERE id = '{1}'".format(new, job_id)
                    task_command = "UPDATE hydra_taskboard SET archived = '{0}' WHERE job_id = '{1}'".format(new, job_id)
                    commandList.append(job_command)
                    commandList.append(task_command)

                with transaction() as t:
                    for cmd in commandList:
                        t.cur.execute(cmd)

            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                self.updateJobTable()
                
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
        
        addItem("Fetch", self.doFetch, "Fetch the latest information from the Database")
        self.taskMenu.addSeparator()
        addItem("Start Tasks", self.startTaskHandler, "Start all tasks selected in the Task List")
        addItem("Pause Tasks", self.pauseTaskHandler, "Pause all tasks selected in the Task List")
        addItem("Kill Tasks", self.killTaskHandler, "Kill all tasks selected in the Task List")
        addItem("Reset Tasks", self.resetTaskHandler, "Reset all tasks selected in the Task List")
        self.taskMenu.addSeparator()
        addItem("Load LogFile", self.loadLogHandler, "Load the log file for all tasks selected in the Task List")
        self.taskMenu.popup(QCursor.pos())

    def updateTaskTable(self, job_id):
        with transaction() as t:
            t.cur.execute("SELECT maxNodes FROM hydra_jobboard WHERE id = '{0}'".format(str(job_id)))
            limit = t.cur.fetchall()[0][0]
        sString = "Task List (Job ID: {0}) (Node Limit: {1})".format(str(job_id), int(limit)) 
        self.taskTableLabel.setText(sString)
        try:
            tasks = hydra_taskboard.fetch("WHERE job_id = '{0}'".format(job_id))
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
                    aboutBox(title = "Reset Task Error",
                    msg = "Unable to reset task {0} because there was an error communicating with it's host.".format(task_id))
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
                tasks = hydra_taskboard.fetch ("WHERE job_id = '{0}'".format(job_id))
                for task in tasks[0:reply[0]]:
                    TaskUtils.startTask(task.id)
                logger.info("Test Tasks Started!")
                with transaction() as t:
                    [job] = hydra_jobboard.fetch("WHERE id = '{0}'".format(job_id))
                    job.job_status = "S"
                    job.update(t)
                self.updateJobTable()
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
                        aboutBox(self, "Error", "Task couldn't be killed for ""some reason.")
                except socketerror as err:
                    logger.error(str(err))
                    aboutBox(self, "Error", "Task couldn't be killed because "
                    "there was a problem communicating with the host running "
                    "it.")
                except sqlerror as err:
                    logger.error(str(err))
                    aboutBox(self, "SQL Error", str(err))
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
                        aboutBox(self, "Error", "Task couldn't be killed for ""some reason.")
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
            choice = yesNoBox(self, "Open logs?", "Note, this will open a text editor for EACH task selected. Continue?")
            if choice == QMessageBox.Yes:
                for row in rows:
                    task_id = int(self.taskTable.item(row, 0).text())
                    [taskOBJ] = hydra_taskboard.fetch("WHERE id = '{0}'".format(task_id))
                    loadLog(taskOBJ)
        else:
            task_id = int(self.taskTable.item(rows[0], 0).text())
            [taskOBJ] = hydra_taskboard.fetch("WHERE id = '{0}'".format(task_id))
            loadLog(taskOBJ)

    def advancedSearchHandler(self):
        results = TaskSearchDialog.create()
        logger.error("Not Implemeted!")
        print results

    def filterJobHandler(self):
        self.filters = JobFilterDialog.create(self.filters)
        #logger.debug(self.filters)
        logger.info(self.jobCommandBuilder())
        self.updateJobTable()

    def searchByTaskID(self):
        """Given a task id, finds the job, selects it in the job table, and
        displays the tasks for that job, including the one searched for. Does
        nothing if task id doesn't exist."""

        #Retrieve job id by task id in the database
        task_id = str(self.taskIDLineEdit.text())
        if task_id:
            with transaction() as t:
                query = "SELECT job_id FROM hydra_taskboard WHERE id = '{0}'".format(task_id)
                t.cur.execute(query)
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
        
        addItem("Online Nodes", self.onlineRenderNodesHandler, "Online all checked nodes")
        addItem("Offline Nodes", self.offlineRenderNodesHandler, "Offline all checked nodes without killing their current task")
        addItem("Get Off Nodes", self.getOffRenderNodesHandler, "Kill task then offline all checked nodes")
        self.nodeMenu.addSeparator()
        addItem("Select All Nodes", self.selectAllNodesHandler, "Check all nodes in the Node Table")
        addItem("Deselect All Node", self.selectNoneNodesHandler, "Uncheck all ndoes in the Node Table")
        addItem("Select by Host Name...", self.selectByHostHandler, "Open a dialog to check nodes based on their host name")
        self.nodeMenu.addSeparator()
        editNodeItem = addItem("Edit Node...", self.doNothing, "Open a dialog to edit selected node's attributes. WIP.")
        editNodeItem.setEnabled(False)
        
        self.nodeMenu.popup(QCursor.pos())
        
    def updateRenderNodeTable(self):
        #Clear the table(note: this is done to avoid duplication of items)
        self.renderNodeTable.clearContents()
        self.renderNodeTable.setRowCount(0)

        #Prevent rows from being sorted while table is populating
        self.renderNodeTable.setSortingEnabled(False)

        nodes = hydra_rendernode.fetch(order="order by host")
        self.renderNodeTable.setRowCount(len(nodes))
        
        
        for pos, node in enumerate(nodes):
            self.renderNodeTable.setItem(pos, 0, TableWidgetItem_check())
            self.renderNodeTable.setItem(pos, 1, TableWidgetItem_int(str(node.host)))
            self.renderNodeTable.setItem(pos, 2, TableWidgetItem(str(niceNames[node.status])))
            self.renderNodeTable.item(pos, 2).setBackgroundColor(niceColors[node.status])
            self.renderNodeTable.setItem(pos, 3, TableWidgetItem(str(node.task_id)))
            self.renderNodeTable.setItem(pos, 4, TableWidgetItem(str(node.minPriority)))
            self.renderNodeTable.setItem(pos, 5, TableWidgetItem(str(node.capabilities)))
            nodeVersion  = getSoftwareVersionText(node.software_version)
            self.renderNodeTable.setItem(pos, 6, TableWidgetItem(str(nodeVersion)))
            self.renderNodeTable.setItem(pos, 7, TableWidgetItem_dt(node.pulse))
            if node.host == Utils.myHostName():
                self.renderNodeTable.item(pos, 1).setFont(QFont('Segoe UI', 8, QFont.DemiBold))

        self.renderNodeTable.setSortingEnabled(True)

    def onlineRenderNodesHandler(self):
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

    def offlineRenderNodesHandler(self):
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

    def getOffRenderNodesHandler(self):
        """For all nodes with boxes checked in the render nodes table, changes
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
                                logger.warning("Problem killing task durring GetOff")
                                aboutBox(self, "Error", "There was a problem killing the task during GetOff!")
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

    def selectAllNodesHandler(self):
        rows = self.renderNodeTable.rowCount()
        for rowIndex in range(0, rows):
            item = self.renderNodeTable.item(rowIndex, 0)
            item.setCheckState(Qt.Checked)

    def selectNoneNodesHandler(self):
        rows = self.renderNodeTable.rowCount()
        for rowIndex in range(0, rows):
            item = self.renderNodeTable.item(rowIndex, 0)
            item.setCheckState(Qt.Unchecked)

    def selectByHostHandler(self):
        reply = strBox(self, "Select By Host Name", "Host (using * as wildcard):")
        if reply[1]:
            searchString = str(reply[0])
            rows = self.renderNodeTable.rowCount()
            for rowIndex in range(0, rows):
                item = str(self.renderNodeTable.item(rowIndex, 1).text())
                if fnmatch.fnmatch(item, searchString):
                    self.renderNodeTable.item(rowIndex, 0).setCheckState(Qt.Checked)
                    logger.info("Selecting {0} matched with {1}".format(item, searchString))
                    
    #---------------------------------------------------------------------#
    #----------------------THIS NODE BUTTON HANDLERS----------------------#
    #---------------------------------------------------------------------#
                    
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
                            aboutBox(self, "Error", "There was a problem killing the task during GetOff!")
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

    #---------------------------------------------------------------------#
    #--------------------------UPDATE HANDLERS----------------------------#
    #---------------------------------------------------------------------#

    def doFetch(self):
        """Aggregate method for updating all of the widgets."""
        try:
            self.updateThisNodeInfo()
            self.updateRenderNodeTable()
            self.updateRenderJobGrid()
            self.updateJobTable()
            self.updateStatusBar()
        except sqlerror as err:
            logger.error(str(err))
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
            logger.error(str(err))
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
                "Information about this node cannot be displayed because it is "
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
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT {0}".format(self.limitSpinBox.value())
        records = (hydra_jobboard.fetch(command))
        
        clearLayout(self.taskGrid)
        setupDataGrid(records, columns, self.taskGrid)

    def updateStatusBar(self):
        with transaction() as t:
            t.cur.execute ("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        thisNode = NodeUtils.getThisNodeData()
        logger.debug("Counts = " + str(counts))
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
        v = re.search("rendernodemain-dist-([0-9]+)", sw_ver,
                        re.IGNORECASE)
        if v:
            return v.group(1)

        #Case 2: source code file
        elif re.search("rendernodemain.py$", sw_ver, re.IGNORECASE):
            return "Dev"

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
        if os.path.exists(logFile):
            logger.info("Opening Log File @ {0}".format(str(logFile)))
            webbrowser.open(logFile)
        else:
            aboutBox(title = "Invalid Log File Path", msg = "Invalid log file path for task: {0}".format(record.id))
            logger.error("Invalid log file path for task: {0}".format(record.id))
    else:
        aboutBox(title = "No Log on File", msg = "No log on file for task: {0}\nJob was probably never started or was recently reset.".format(record.id))
        logger.warning("No log file on record for task: {0}".format(record.id))


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
