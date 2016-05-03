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
        self.userFilter = False
        self.showArchivedFilter = False

        self.statusMsg = "ERROR"

        self.currentJobSel = None

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

        #Connect Context Menus
        self.centralwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.centralwidget.customContextMenuRequested.connect(self.centralContextHandler)

        self.jobTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.jobTree.customContextMenuRequested.connect(self.jobContextHandler)

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

        addItem("Soft Update", self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update", self.doFetch,
                "Update all of the latest information from the Database")
        self.centralMenu.addSeparator()
        onAct = addItem("Online This Node", self.onlineThisNodeHandler,
                        "Online This Node")
        offAct = addItem("Offline This Node", self.offlineThisNodeHandler,
                        "Wait for the current job to finish then offline this node")
        getAct = addItem("Get Off This Node!", self.getOffThisNodeHandler,
                        "Kill the current task and offline this node immediately")

        if not self.thisNodeButtonsEnabled:
            onAct.setEnabled(False)
            offAct.setEnabled(False)
            getAct.setEnabled(False)

        self.centralMenu.popup(QCursor.pos())

    def revealDetailedHandler(self, data_ids, sqlTable, sqlWhere):
        dataList = [sqlTable.secureFetch(sqlWhere, (d_id))[0] for d_id in data_ids]
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

        addItem("Soft Update", self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update", self.doFetch,
                "Update all of the latest information from the Database")
        self.jobMenu.addSeparator()
        addItem("Start Jobs", self.startJobHandler,
                "Start all jobs selected in Job List")
        addItem("Pause Jobs", self.pauseJobHandler,
                "Pause all jobs selected in Job List")
        addItem("Kill Jobs", self.killJobHandler,
                "Kill all jobs selected in Job List")
        addItem("Reset Jobs", self.resetJobHandler,
                "Reset all jobs selected in Job List")
        addItem("Start Test Frames...", self.callTestFrameBox,
                "Open a dialog to start the first X frames in each job "
                "selected in the Job List")
        self.jobMenu.addSeparator()
        addItem("Archive/Unarchive Jobs", self.toggleArchiveHandler,
                "Toggle the Archived status on each job selected in he Job List")
        addItem("Reset Node Limit on Jobs", self.resetNodeManagementHandler,
                "Reset the number of tasks which are ready to match the limit "
                "of the number of concurant tasks.")
        addItem("Reveal Detailed Data...", self.revealJobDetailedHandler,
                "Opens a dialog window the detailed data for the selected jobs.")
        self.jobMenu.addSeparator()
        #setJobPriorityHandler
        addItem("Set Job Priority...", self.setJobPriorityHandler,
        "Set priority on each job selected in the Job List")
        editJob = addItem("Edit Job...", self.doNothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)
        self.jobMenu.addSeparator()

        uFA = addItem("Only Show My Jobs", self.userFilterContextHandler,
                        "Only show the jobs belonging to the current user")
        uFA.setCheckable(True)
        if self.userFilter:
            uFA.setChecked(True)

        aFA = addItem("Show Archived Jobs", self.archivedFilterContextHandler,
                        "Show jobs which have been archived")
        aFA.setCheckable(True)
        if self.showArchivedFilter:
            aFA.setChecked(True)
        self.jobMenu.popup(QCursor.pos())

    def fetchJobs(self):
        cmd = self.jobCommandBuilder()
        try:
            return hydra_jobboard.fetch(cmd)
        except sqlerror as err:
            logger.debug(str(err))
            aboutBox(self, "SQL error", str(err))
            return

    def getJobData(self, job):
        if job.tasksTotal > 0:
            percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
            taskString  = "{0} ({1}/{2})".format(percent, job.tasksComplete,
                                                job.tasksTotal)
        else:
            taskString = "0% (0/0)"

        return [job.niceName, str(job.id), job.owner, niceNames[job.job_status],
                taskString, str(job.priority)]

    def jobTreeHandler(self, mode = "IDs"):
        self.resetStatusBar()
        mySel = self.jobTree.selectedItems()
        if len(mySel) < 1:
            aboutBox(self, "Selection Error",
                    "Please select something from the Job Table and try again.")
            return

        if mode == "IDs":
            data = [int(sel.text(1)) for sel in mySel if sel.parent()]

        elif mode == "Rows":
            data = mySel

        return data if data != [] else None

    def jobTreeClickedHandler(self):
        shotItem = self.jobTree.currentItem()
        if shotItem.parent():
            self.initTaskTable(int(shotItem.text(1)), shotItem)

    def addJobTreeShot(self, jobData, job):
        proj = self.jobTree.findItems(str(job.projectName), Qt.MatchContains)
        if proj != []:
            #If project was found search for job
            shotItem = self.jobTree.findItems(str(job.id), Qt.MatchRecursive, 1)
            if shotItem != []:
                #If job was found update it
                shotItem = shotItem[0]
                shotItem.setData(0,0,jobData[0])
                shotItem.setData(1,0,jobData[1])
                shotItem.setData(2,0,jobData[2])
                shotItem.setData(3,0,jobData[3])
                shotItem.setData(4,0,jobData[4])
                shotItem.setData(5,0,jobData[5])
            else:
                #If job was not found add it as a new item
                shotItem = QTreeWidgetItem(proj[0], jobData)
        else:
            #If project was not found add it and the item
            root = QTreeWidgetItem(self.jobTree, [str(job.projectName)])
            root.setFont(0, QFont('Segoe UI', 10, QFont.DemiBold))
            shotItem = QTreeWidgetItem(root, jobData)

        #Update colors and stuff
        shotItem.setBackgroundColor(3, niceColors[job.job_status])
        if job.archived == 1:
            shotItem.setBackgroundColor(0, QColor(220,220,220))
            shotItem.setBackgroundColor(1, QColor(220,220,220))
            shotItem.setBackgroundColor(2, QColor(220,220,220))
            shotItem.setBackgroundColor(4, QColor(220,220,220))
            shotItem.setBackgroundColor(5, QColor(220,220,220))
        if job.owner == self.username:
            shotItem.setFont(2, QFont('Segoe UI', 8, QFont.DemiBold))

    def populateJobTree(self):
        jobs = self.fetchJobs()
        if not jobs:
            return

        for job in jobs:
            jobData = self.getJobData(job)
            self.addJobTreeShot(jobData, job)

        labelText = "Job List"
        labelText += " (This User Only)" if self.userFilter else ""
        labelText += " (No Archived Jobs)" if not self.showArchivedFilter else ""
        self.jobTableLabel.setText(labelText + ":")

    def initJobTree(self):
        self.jobTree.itemClicked.connect(self.jobTreeClickedHandler)
        header = QTreeWidgetItem(["Name", "ID", "Owner", "Status", "Tasks",
                                    "Priority"])
        self.jobTree.setHeaderItem(header)
        #Must set widths AFTER setting header
        self.jobTree.setColumnWidth(0, 250)        #Project/Name
        self.jobTree.setColumnWidth(1, 50)         #ID
        self.jobTree.setColumnWidth(2, 100)        #Owner
        self.jobTree.setColumnWidth(3, 60)         #Status
        self.jobTree.setColumnWidth(4, 60)         #Tasks
        self.jobTree.setColumnWidth(5, 50)         #Priority
        self.populateJobTree()

    def updateJobTreeRow(self, job_id, shotItem):
        [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id))
        data = self.getJobData(job)

        for i in range(0, 6):
            shotItem.setData(i,0,data[i])
            if job.archived == 1:
                shotItem.setBackgroundColor(i, QColor(200,200,200))

        shotItem.setBackgroundColor(3, niceColors[job.job_status])

        if job.owner == self.username:
            shotItem.setFont(2, QFont('Segoe UI', 8, QFont.DemiBold))

    def userFilterContextHandler(self):
        self.userFilterCheckbox.setChecked(0) if self.userFilter else 2
        self.populateJobTree()
        self.resetStatusBar()

    def archivedFilterContextHandler(self):
        self.archivedCheckBox.setChecked(0) if self.showArchivedFilter else 2
        self.populateJobTree()
        self.resetStatusBar()

    def userFilterActionHandler(self):
        self.userFilterCheckbox.setChecked(0) if self.userFilter else 2
        self.userFilter = False if self.userFilter else True
        self.jobTree.clear()
        self.populateJobTree()

    def archivedFilterActionHandler(self):
        self.archivedCheckBox.setChecked(0) if self.showArchivedFilter else 2
        self.showArchivedFilter = False if self.showArchivedFilter else True
        self.jobTree.clear()
        self.populateJobTree()

    def jobCommandBuilder(self):
        #TODO:Secure this
        command = "WHERE"
        command += " owner = '{0}'" if self.userFilter else ""
        command += " AND" if command != "WHERE" and not self.showArchivedFilter else ""
        command += " archived = 0" if not self.showArchivedFilter else ""

        return command.format(self.username) if command != "WHERE" else ""

    def startJobHandler(self):
        job_ids = self.jobTreeHandler()
        if job_ids:
            map(JobUtils.startJob, job_ids)
            self.populateJobTree()

    def killJobHandler(self):
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really kill the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                responses = map(JobUtils.killJob, job_ids)
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if True in responses:
                    aboutBox(self, "Error",
                            "One or more nodes couldn't kill their tasks.")
                map(JobUtils.manageNodeLimit, job_ids)
                self.populateJobTree()

    def pauseJobHandler(self):
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really pause the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                responses = [JobUtils.killJob(job_id, PAUSED) for job_id in job_ids]
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if True in responses:
                    aboutBox(self, "Error",
                            "One or more nodes couldn't kill their tasks.")
                self.populateJobTree()

    def resetJobHandler(self):
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                responses = [JobUtils.resetJob(job_id, READY) for job_id in job_ids]
            except sqlerror as err:
                logger.error(str(err))
                aboutBox(self, "SQL Error", str(err))
            finally:
                if True in responses:
                    aboutBox(self, "Error",
                            "One or more nodes couldn't kill their tasks.")
                self.populateJobTree()

    def resetNodeManagementHandler(self):
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        cStr = "Are you sure you want to reset node managment on the selected Job?\n"
        cStr += "This will hold all Tasks above the max node count set on the Job."
        choice = yesNoBox(self, "Confirm", cStr)
        if choice == QMessageBox.Yes:
            map(JobUtils.setupNodeLimit, job_ids)
        self.populateJobTree()

    def setJobPriorityHandler(self):
        selection = self.jobTreeHandler("Rows")
        if not selection:
            return
        for sel in selection:
            job_id = int(sel.text(1))
            job_priority = int(sel.text(5))
            msgString = "Priority for job {0}:".format(job_id)
            reply = intBox(self, "Set Job Priority", msgString , job_priority)
            if reply[1]:
                JobUtils.prioritizeJob(job_id, reply[0])
                self.populateJobTree()
            else:
                logger.info("prioritizeJob skipped on {0}".format(job_id))

    def toggleArchiveHandler(self):
        #TODO:Secure this
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        choice = yesNoBox(self, "Confirm",
                        "Really archive or unarchive the selected jobs?")
        if choice == QMessageBox.Yes:
            try:
                commandList = []
                for job_id in job_ids:
                    [job] = hydra_jobboard.secureFetch("WHERE id = %s",(job_id))
                    new = 0
                    if job.archived == 0:
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
                self.populateJobTree()

    def revealJobDetailedHandler(self):
        job_ids = self.jobTreeHandler()
        if job_ids:
            self.revealDetailedHandler(job_ids, hydra_jobboard, "WHERE id = %s")

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

    def initTaskTable(self, job_id, shotItem):
        try:
            [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id))
        except sqlerror as err:
            aboutBox(self, "SQL Error", str(err))
            logger.error(str(err))
            return
        self.currentJobSel = job.id
        sString = "Task List (Job ID: {0}) (Node Limit: {1})".format(str(job_id),
                                                                    int(job.maxNodes))
        self.taskTableLabel.setText(sString)

        try:
            tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id))
        except sqlerror as err:
            aboutBox(self, "SQL Error", str(err))
            logger.error(str(err))
            return

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

        JobUtils.updateJobTaskCount(job_id, tasks = tasks, commit = True)
        self.updateJobTreeRow(job_id, shotItem)

    def updateTaskTable(self):
        #TODO:Make this work
        if self.currentJobSel:
            #Update here
            pass

    def taskTableHandler(self, mode = "IDs"):
        self.resetStatusBar()
        rows = self.taskTable.selectionModel().selectedRows()
        if len(rows) < 1:
            msg = "Please select something from the Job Table and try again."
            aboutBox(self, "Selection Error", msg)
            return

        if mode == "IDs":
            return [self.taskTable.item(ro.row(), 0).text() for ro in rows]
        elif mode == "Rows":
            return [item.row() for item in rows]
        else:
            logger.error("Bad taskTableHandler mode!")
            return

    def startTaskHandler(self):
        task_ids = self.taskTableHandler()
        if task_ids:
            map(TaskUtils.startTask, task_ids)
            self.updateTaskTable()

    def resetTaskHandler(self):
        task_ids = self.taskTableHandler()
        if not task_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
        if choice == QMessageBox.Yes:
            responses = [TaskUtils.resetTask(t_id, READY) for t_id in task_ids]
            self.updateTaskTable()
            if True in responses:
                msg = "Unable to reset task {0} because there was an error communicating with it's host.".format(task_id)
                aboutBox(self, "Reset Task Error", msg)

    def callTestFrameBox(self):
        job_ids = self.jobTreeHandler()
        if not job_ids:
            return
        job_id = job_ids[0]
        reply = intBox(self, "StartTestFrames", "Start X Test Frames?", 10)
        if reply[1]:
            logger.info("Starting {0} test frames on job_id {1}".format(reply[0], job_id))
            tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id))

            map(TaskUtils.startTask, tasks[0:reply[0]])
            logger.info("Test Tasks Started!")
            JobUtils.updateJobTaskCount(job_id, tasks = tasks, commit = True)
            JobUtils.manageNodeLimit(job_id)
            self.populateJobTree()
        else:
            logger.info("No test tasks started.")

    def killTaskHandler(self):
        task_ids = self.taskTableHandler()
        if not task_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really kill selected tasks?")
        if choice == QMessageBox.Yes:
            for task_id in task_ids:
                try:
                    response = TaskUtils.killTask(task_id)
                    if response:
                        aboutBox(self, "Error",
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
        self.updateTaskTable()
        self.populateJobTree()

    def pauseTaskHandler(self):
        task_ids = self.taskTableHandler()
        if not task_ids:
            return
        choice = yesNoBox(self, "Confirm", "Really kill selected tasks?")
        if choice == QMessageBox.Yes:
            for task_id in task_ids:
                try:
                    response = TaskUtils.killTask(task_id, PAUSED)
                    if response:
                        aboutBox(self, "Error",
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
        self.updateTaskTable()
        self.populateJobTree()

    def loadLogHandler(self):
        task_ids = self.taskTableHandler()
        if not task_ids:
            return
        if len(task_ids) > 1:
            choice = yesNoBox(self, "Open logs?", "Note, this will open a text"
                            " editor for EACH task selected. Continue?")
            if choice == QMessageBox.Yes:
                for task_id in task_ids:
                    [taskOBJ] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id))
                    loadLog(taskOBJ)
        else:
            [taskOBJ] = hydra_taskboard.secureFetch("WHERE id = %s", (task_ids[0]))
            loadLog(taskOBJ)

    def advancedSearchHandler(self):
        #results = TaskSearchDialog.create()
        logger.error("Not Implemeted!")

    def revealTaskDetailedHandler(self):
        rows = self.taskTableHandler()
        if not rows:
            return
        task_id_list = []
        for row in rows:
            task_id_list.append(int(self.taskTable.item(row, 0).text()))
        self.revealDetailedHandler(task_id_list, hydra_taskboard, "WHERE id = %s")

    def searchByTaskID(self):
        """~~UNTESTED~~
        Given a task id, finds the job, selects it in the job table, and
        displays the tasks for that job, including the one searched for. Does
        nothing if task id doesn't exist."""
        reply = intBox(self, "Search for job via TaskID", 0)
        if reply[1]:
            taskID = int(reply[0])
            cmd = "SELECT job_id FROM hydra_taskboard WHERE id = %s"
            with transaction() as t:
                [task] = t.cur.execute(cmd, (taskID))
            shotItem = self.jobTree.findItems(str(task.job_id), Qt.MatchRecursive, 1)
            if shotItem != []:
                self.jobTree.itemClicked(shotItem[0], 0)
            else:
                self.aboutBox("Error!", "Could not find job for given task!")

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

        addItem("Soft Update", self.doUpdate,
                "Update with the most important information from the Database")
        addItem("Full Update", self.doFetch,
                "Update all of the latest information from the Database")
        self.nodeMenu.addSeparator()
        addItem("Online Nodes", self.onlineRenderNodesHandler,
                "Online all checked nodes")
        addItem("Offline Nodes", self.offlineRenderNodesHandler,
                "Offline all checked nodes without killing their current task")
        addItem("Get Off Nodes", self.getOffRenderNodesHandler,
                "Kill task then offline all checked nodes")
        self.nodeMenu.addSeparator()
        addItem("Select All Nodes", self.selectAllNodesHandler,
                "Check all nodes in the Node Table")
        addItem("Deselect All Node", self.selectNoneNodesHandler,
                "Uncheck all ndoes in the Node Table")
        addItem("Select by Host Name...", self.selectByHostHandler,
                "Open a dialog to check nodes based on their host name")
        self.nodeMenu.addSeparator()
        addItem("Reveal Detailed Data...", self.revealNodeDetailedHandler,
                "Opens a dialog window the detailed data for the selected nodes.")
        addItem("Edit Node...", self.nodeEditorTableHandler,
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

        #h = host, s = status, t = task_id, p = pulse
        nodeDict = {h:[s,t,p] for h, s, t, p in nodeData}
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
            aboutBox(self, "Selection Error",
                    "Please select something from the Render Node Table and try again.")
            return
        rows = [item.row() for item in rows]
        nodes = [str(self.renderNodeTable.item(row, 0).text()) for row in rows]
        return nodes

    def onlineRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes? <br>" + str(hosts))
        if choice == QMessageBox.Yes:
            try:
                with transaction() as t:
                    rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
                for node_row in rendernode_rows:
                    NodeUtils.onlineNode(node_row)
                self.updateRenderNodeTable()
            except sqlerror as err:
                logger.error(str(err))
                self.sqlErrorBox()
        else:
            aboutBox(self, "Aborted", "No action taken.")

    def offlineRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to offline"
                          " these nodes? <br>" + str(hosts))
        if choice == QMessageBox.Yes:
            with transaction() as t:
                rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
                for node_row in rendernode_rows:
                    if node_row.host in hosts:
                        NodeUtils.offlineNode(node_row)
            self.updateRenderNodeTable()
        else:
            aboutBox(self, "Aborted", "No action taken.")

    def getOffRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "<B>WARNING</B>: All progress on"
                          " current tasks will be lost for the selected"
                          " render nodes. Are you sure you want to stop these"
                          " nodes? <br>" + str(hosts))
        if choice == QMessageBox.Yes:
            try:
                with transaction() as t:
                    rendernode_rows = hydra_rendernode.fetch(explicitTransaction=t)
            except sqlerror as err:
                logger.error(str(err))
                self.sqlErrorBox()
                return

            for thisNode in rendernode_rows:
                NodeUtils.offlineNode(thisNode)
                if thisNode.task_id:
                    try:
                        response = TaskUtils.killTask(thisNode.task_id, READY)
                        if not response:
                            logger.warning("Problem killing task durring GetOff")
                            aboutBox(self, "Error",
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

                self.updateRenderNodeTable()
        else:
            aboutBox(self, "Aborted", "No action taken.")

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
        #TODO:Cleanup and secure
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
        node_list = self.renderNodeTableHandler()
        if node_list:
            self.revealDetailedHandler(node_list, hydra_rendernode, "WHERE host = %s")

    def selectAllNodesHandler(self):
        rows = self.renderNodeTable.rowCount()
        colCount = self.renderNodeTable.columnCount() - 1
        rows = [x for x in range(rows)]
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

        self.updateRenderNodeTable()
        self.updateStatusBar()

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

        self.updateRenderNodeTable()
        self.updateStatusBar()

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
        if choice == QMessageBox.Yes:
            NodeUtils.offlineNode(thisNode)
            if thisNode.task_id:
                task_id = thisNode.task_id
                try:
                    response = TaskUtils.killTask(task_id, READY)
                    if not response:
                        logger.warning("Problem killing task durring GetOff")
                        aboutBox(self, "Error",
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
            self.updateRenderNodeTable()
            self.updateStatusBar()
        else:
            aboutBox(self, "Abort", "No action taken.")

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
            allNodes = hydra_rendernode.fetch(order = "ORDER BY host")
            logger.info(allNodes)
            thisNode = None
            for node in allNodes:
                if node.host == self.thisNodeName:
                    thisNode = node

            if thisNode:
                self.thisNodeExists = True

            if not self.thisNodeExists:
                self.nodeDoesNotExistBox()
                self.setThisNodeButtonsEnabled(False)

            self.initRenderNodeTable(allNodes)
            self.updateStatusBar(thisNode)

            self.initJobTree()
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
                self.populateJobTree()
                self.updateTaskTable()
                self.updateRenderNodeTable()
            elif curTab == 1:
                #Recent Jobs
                self.updateRenderJobGrid()
            elif curTab == 2:
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
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT %s"
        records = hydra_jobboard.secureFetch(command, (self.limitSpinBox.value()))
        columns = records[0].__dict__.keys()
        columns = [labelFactory(col) for col in columns if col.find("__") is not 0]

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
