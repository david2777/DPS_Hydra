from __future__ import division
"""The software for managing jobs, tasks, and nodes."""
#Standard
import os
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
from Dialogs.DataTable import DataTableDialog
from Dialogs.MessageBoxes import *

#Hydra
import Constants
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *
from Setups.Threads import workerSignalThread
import Utilities.Utils as Utils
import Utilities.TaskUtils as TaskUtils
import Utilities.JobUtils as JobUtils
import Utilities.NodeUtils as NodeUtils

#------------------------------------------------------------------------------#
#--------------------------------Farm View-------------------------------------#
#------------------------------------------------------------------------------#

class FarmView(QMainWindow, Ui_FarmView):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        with open(Utils.findResource("styleSheet.css"),"r") as myStyles:
            self.setStyleSheet(myStyles.read())

        #My UI Setup Functions
        self.setupTables()
        self.connectButtons()
        self.setupHotkeys()
        self.setWindowIcon(QIcon(Utils.findResource("Images/FarmView.png")))

        #Class Variables
        self.thisNodeName = Utils.myHostName()
        logger.info("This host is {0}".format(self.thisNodeName))
        self.username = Utils.getInfoFromCFG("database", "username")
        self.userFilter = False
        self.showArchivedFilter = False
        self.statusMsg = "ERROR"
        self.currentJobSel = None

        #Make sure this node exists
        self.thisNodeButtonsEnabled = True
        self.thisNodeExists = self.findThisNode()

        #Start autoUpdater and then fetch data from DB
        self.autoUpdateThread = workerSignalThread("run", 10)
        QObject.connect(self.autoUpdateThread, SIGNAL("run"), self.doUpdate)
        self.autoUpdateThread.start()
        self.doFetch()

    def addItem(self, menu, name, handler, statusTip, arg = None, hotkey = None):
        action = QAction(name, self)
        action.setStatusTip(statusTip)
        if arg:
            action.triggered.connect(functools.partial(handler, arg))
        else:
            action.triggered.connect(handler)
        if hotkey:
            action.setShortcut(QKeySequence(hotkey))
        menu.addAction(action)
        return action

    #---------------------------------------------------------------------#
    #--------------------------UI SETUP FUNCTIONS-------------------------#
    #---------------------------------------------------------------------#
    def setupTables(self):
        #jobTree header and column widths
        header = QTreeWidgetItem(["Name", "Job ID", "Status", "Tasks", "Owner",
                                    "Priority", "Start", "End", "Max Nodes"])
        self.jobTree.setHeaderItem(header)
        #Must set widths AFTER setting header
        self.jobTree.setColumnWidth(0, 300)         #Project/Name
        self.jobTree.setColumnWidth(1, 50)          #ID
        self.jobTree.setColumnWidth(2, 60)          #Status
        self.jobTree.setColumnWidth(3, 80)          #Percentage
        self.jobTree.setColumnWidth(4, 100)         #Owner
        self.jobTree.setColumnWidth(5, 50)          #Priority
        self.jobTree.setColumnWidth(6, 70)          #Start Frame
        self.jobTree.setColumnWidth(6, 70)          #End Frame
        self.jobTree.setColumnWidth(6, 60)          #Max Nodes

        #renderNodeTable column widths
        self.renderNodeTable.setColumnWidth(0, 200)     #Host
        self.renderNodeTable.setColumnWidth(1, 70)      #Status
        self.renderNodeTable.setColumnWidth(2, 70)      #Task ID
        self.renderNodeTable.setColumnWidth(3, 110)     #Version
        self.renderNodeTable.setColumnWidth(4, 100)     #Schedule Enabled
        self.renderNodeTable.setColumnWidth(5, 175)     #Heartbeat
        self.renderNodeTable.setColumnWidth(6, 110)     #Capabilities

        #taskTable column widths
        self.taskTable.setColumnWidth(0, 60)        #ID
        self.taskTable.setColumnWidth(1, 60)        #Start Frame
        self.taskTable.setColumnWidth(2, 60)        #End Frame
        self.taskTable.setColumnWidth(3, 100)       #Host
        self.taskTable.setColumnWidth(4, 60)        #Status
        self.taskTable.setColumnWidth(5, 60)        #Priority
        self.taskTable.setColumnWidth(6, 120)       #Start Time
        self.taskTable.setColumnWidth(7, 120)       #End Time
        self.taskTable.setColumnWidth(8, 120)       #Duration
        self.taskTable.setColumnWidth(9, 120)       #Code

        #Job List splitter size
        self.splitter_jobList.setSizes([11000, 10000])

        #Get rid of the spaces between gird layouts
        self.gridLayout_taskList.setContentsMargins(0,0,0,0)
        self.gridLayout_jobListJobs.setContentsMargins(0,0,0,0)

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
        self.autoUpdateCheckbox.stateChanged.connect(self.autoUpdateHandler)
        self.editThisNodeButton.clicked.connect(self.nodeEditorHandler)

        #jobTree itemClicked
        self.jobTree.itemClicked.connect(self.jobTreeClickedHandler)

        #Connect basic filter checkboxKeys
        self.archivedCheckBox.stateChanged.connect(self.archivedFilterAction)
        self.userFilterCheckbox.stateChanged.connect(self.userFilterAction)

        #Connect Context Menus
        self.centralwidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.centralwidget.customContextMenuRequested.connect(self.centralContextHandler)

        self.jobTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.jobTree.customContextMenuRequested.connect(self.jobContextMenu)

        self.taskTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.taskTable.customContextMenuRequested.connect(self.taskContextMenu)
        self.taskTable.itemChanged.connect(self.taskTableEditHandler)

        self.renderNodeTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.renderNodeTable.customContextMenuRequested.connect(self.nodeContextHandler)

    def setupHotkeys(self):
        #This Node
        QShortcut(QKeySequence("Ctrl+O"), self, self.onlineThisNodeHandler)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, self.offlineThisNodeHandler)
        QShortcut(QKeySequence("Ctrl+G"), self, self.getOffThisNodeHandler)
        QShortcut(QKeySequence("Ctrl+U"), self, self.doFetch)

        #Node Table
        QShortcut(QKeySequence("Ctrl+Alt+O"), self, self.onlineRenderNodesHandler)
        QShortcut(QKeySequence("Ctrl+Alt+Shift+O"), self, self.offlineRenderNodesHandler)
        QShortcut(QKeySequence("Ctrl+Alt+G"), self, self.getOffRenderNodesHandler)

        #Job Tree
        jobStartFunc = functools.partial(self.jobActionHandler, "start")
        jobPauseFunc = functools.partial(self.jobActionHandler, "pause")
        jobKillFunc = functools.partial(self.jobActionHandler, "kill")
        jobResetFunc = functools.partial(self.jobActionHandler, "reset")
        jobArchiveFunc = functools.partial(self.jobActionHandler, "archive")
        jobUnarchiveFunc = functools.partial(self.jobActionHandler, "unarchive")
        QShortcut(QKeySequence("Ctrl+S"), self, jobStartFunc)
        QShortcut(QKeySequence("Ctrl+P"), self, jobPauseFunc)
        QShortcut(QKeySequence("Ctrl+K"), self, jobKillFunc)
        QShortcut(QKeySequence("Ctrl+R"), self, jobResetFunc)
        QShortcut(QKeySequence("Del"), self, jobArchiveFunc)
        QShortcut(QKeySequence("Shift+Del"), self, jobUnarchiveFunc)

        #Task Table
        taskStartFunc = functools.partial(self.taskActionHandler, "start")
        taskPauseFunc = functools.partial(self.taskActionHandler, "pause")
        taskKillFunc = functools.partial(self.taskActionHandler, "kill")
        taskResetFunc = functools.partial(self.taskActionHandler, "reset")
        taskLogFunc = functools.partial(self.taskActionHandler, "log")
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, taskStartFunc)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self, taskPauseFunc)
        QShortcut(QKeySequence("Ctrl+Shift+K"), self, taskKillFunc)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, taskResetFunc)
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, taskLogFunc)

    #---------------------------------------------------------------------#
    #---------------------------MISC FUNCTIONS----------------------------#
    #---------------------------------------------------------------------#

    def centralContextHandler(self):
        self.centralMenu = QMenu(self)
        QObject.connect(self.centralMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.centralMenu, "Update", self.doFetch,
                "Update with the latest information from the Database",
                hotkey = "Ctrl+U")

        if self.thisNodeButtonsEnabled:
            self.addItem(self.centralMenu, "Online This Node", self.onlineThisNodeHandler,
                                    "Online This Node", hotkey = "Ctrl+O")
            self.addItem(self.centralMenu, "Offline This Node", self.offlineThisNodeHandler,
                                    "Wait for the current job to finish then offline this node",
                                    hotkey = "Ctrl+Shift+O")
            self.addItem(self.centralMenu, "Get Off This Node!", self.getOffThisNodeHandler,
                                    "Kill the current task and offline this node immediately",
                                    hotkey = "Ctrl+G")

        self.centralMenu.popup(QCursor.pos())

    def revealDetailedHandler(self, data_ids, sqlTable, sqlWhere):
        dataList = [sqlTable.fetch(sqlWhere, (d_id,)) for d_id in data_ids]
        DetailedDialog.create(dataList)

    def revealDataTable(self, data_ids, sqlTable, sqlWhere):
        dataList = sqlTable.fetch(sqlWhere, (data_ids,))
        DataTableDialog.create(dataList)

    #---------------------------------------------------------------------#
    #----------------------------JOB HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def jobContextMenu(self):
        self.jobMenu = QMenu(self)
        QObject.connect(self.jobMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.jobMenu, "Start Jobs", self.jobActionHandler,
                "Start jobs selected in Job Tree", "start", "Ctrl+S")
        self.addItem(self.jobMenu, "Pause Jobs", self.jobActionHandler,
                "Pause jobs selected in Job Tree", "pause", "Ctrl+P")
        self.addItem(self.jobMenu, "Kill Jobs", self.jobActionHandler,
                "Kill jobs selected in Job Tree", "kill", "Ctrl+K")
        self.addItem(self.jobMenu, "Reset Jobs", self.jobActionHandler,
                "Reset jobs selected in Job Tree", "reset", "Ctrl+R")
        self.addItem(self.jobMenu, "Start Test Frames...", self.callTestFrameBox,
                "Open a dialog to start the first X frames in each job selected in Job Tree "
                "selected in the Job List")
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Archive Jobs", self.jobActionHandler,
                "Archive Jobs and hide them from the JobTreeView",
                "archive", "Del")
        self.addItem(self.jobMenu, "Unarchive Jobs", self.jobActionHandler,
                "Unarchive Jobs and add them back to the JobTreeView",
                "unarchive", "Shift+Del")
        self.addItem(self.jobMenu, "Reset Node Limit on Jobs", self.jobActionHandler,
                "Reset the number of tasks which are ready to match the limit "
                "of the number of concurant tasks.", "manage")
        self.addItem(self.jobMenu, "Reveal Detailed Data...", self.jobActionHandler,
                "Opens a dialog window the detailed data for the selected jobs.", "data")
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Set Job Priority...", self.setJobPriority,
        "Set priority on each job selected in the Job List")
        editJob = self.addItem(self.jobMenu, "Edit Job...", self.doNothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)

        self.jobMenu.popup(QCursor.pos())

    def jobTreeClickedHandler(self):
        """Handles when the user clicks a job in the JobTree by loading the
        task data into the TaskTable"""
        shotItem = self.jobTree.currentItem()
        if shotItem.parent():
            job_id = int(shotItem.text(1))
            self.initTaskTable(job_id, shotItem)
            self.currentJobSel = job_id

    def fetchJobs(self, mode = "all", job_id = None):
        #Build the fetch command
        if mode == "single":
            command = "WHERE id = %s"
            commandTuple = (job_id,)
        else:
            commandTuple = tuple()
            command = "WHERE"
            command += " owner = %s" if self.userFilter else ""
            command += " AND" if command != "WHERE" and not self.showArchivedFilter else ""
            command += " archived = 0" if not self.showArchivedFilter else ""
            if command == "WHERE":
                command = ""
            else:
                if self.userFilter:
                    commandTuple = (self.username,)

        #Fetch the Jobs
        return hydra_jobboard.fetch(command, commandTuple, multiReturn = True,
                                    cols = ["id", "niceName", "job_status",
                                            "owner", "priority","startFrame",
                                            "endFrame", "maxNodes",
                                            "tasksComplete", "tasksTotal",
                                            "projectName", "archived"])

    def userFilterAction(self):
        self.userFilterCheckbox.setChecked(0) if self.userFilter else 2
        self.userFilter = False if self.userFilter else True
        self.populateJobTree(clear = True)

    def archivedFilterAction(self):
        self.archivedCheckBox.setChecked(0) if self.showArchivedFilter else 2
        self.showArchivedFilter = False if self.showArchivedFilter else True
        self.populateJobTree(clear = True)

    def formatJobData(self, job):
        if job.tasksTotal > 0:
            percent = "{0:.0%}".format(float(job.tasksComplete / job.tasksTotal))
            taskString  = "{0} ({1}/{2})".format(percent, job.tasksComplete,
                                                job.tasksTotal)
        else:
            taskString = "0% (0/0)"

        return [job.niceName, str(job.id), niceNames[job.job_status],
                taskString, job.owner, str(job.priority), str(job.startFrame),
                str(job.endFrame), str(job.maxNodes)]

    def addJobTreeShot(self, job):
        jobData = self.formatJobData(job)
        #Search the JobTree for the Job's projectName to see if it already exists
        proj = self.jobTree.findItems(str(job.projectName), Qt.MatchContains)
        if proj != []:
            #If project was found search for job
            shotItem = self.jobTree.findItems(str(job.id), Qt.MatchRecursive, 1)
            if shotItem != []:
                #If job was found update it
                shotItem = shotItem[0]
                for i in range(0,9):
                    shotItem.setData(i,0,jobData[i])
            else:
                #If job was not found add it as a new item under the project
                shotItem = QTreeWidgetItem(proj[0], jobData)
        else:
            #If project was not found add it and add the job below it
            root = QTreeWidgetItem(self.jobTree, [str(job.projectName)])
            root.setFont(0, QFont('Segoe UI', 10, QFont.DemiBold))
            shotItem = QTreeWidgetItem(root, jobData)

        #Update colors and stuff
        if job.archived == 1:
            for i in range(0,9):
                shotItem.setBackgroundColor(i, QColor(200,200,200))
        shotItem.setBackgroundColor(2, niceColors[job.job_status])
        if job.owner == self.username:
            shotItem.setFont(4, QFont('Segoe UI', 8, QFont.DemiBold))

    def populateJobTree(self, clear = False):
        jobs = self.fetchJobs()
        if not jobs:
            return

        topLevelOpenList = []
        for i in range(0,self.jobTree.topLevelItemCount()):
            if self.jobTree.topLevelItem(i).isExpanded():
                topLevelOpenList.append(str(self.jobTree.topLevelItem(i).text(0)))

        if clear:
            self.jobTree.clear()

        for job in jobs:
            self.addJobTreeShot(job)

        for i in range(0,self.jobTree.topLevelItemCount()):
            if str(self.jobTree.topLevelItem(i).text(0)) in topLevelOpenList:
                self.jobTree.topLevelItem(i).setExpanded(True)

        labelText = "Job List"
        labelText += " (This User Only)" if self.userFilter else ""
        labelText += " (No Archived Jobs)" if not self.showArchivedFilter else ""
        self.jobTableLabel.setText(labelText + ":")

    def getJobTreeSel(self, mode = "IDs"):
        self.resetStatusBar()
        mySel = self.jobTree.selectedItems()
        if len(mySel) < 1:
            warningBox(self, "Selection Error",
                        "Please select something from the Job Tree and try again.")
            return

        if mode == "IDs":
            data = [int(sel.text(1)) for sel in mySel if sel.parent()]

        elif mode == "Rows":
            data = mySel

        return data if data != [] else None

    def jobActionHandler(self, mode):
        job_ids = self.getJobTreeSel()
        if not job_ids:
            return

        #Start Job
        if mode == "start":
            map(JobUtils.startJob, job_ids)
            self.populateJobTree()

        #Reveal Detailed Data
        elif mode == "data":
            if len(job_ids) == 1:
                self.revealDataTable(job_ids, hydra_jobboard, "WHERE id = %s")
            else:
                self.revealDetailedHandler(job_ids, hydra_jobboard, "WHERE id = %s")

        #Kill or Pause Job
        elif mode in ["kill", "pause"]:
            choice = yesNoBox(self, "Confirm", "Really {0} the selected jobs?".format(mode))
            if choice == QMessageBox.No:
                return

            statusAfterDeath = KILLED if mode == "kill" else PAUSED
            responses = [JobUtils.killJob(job_id, statusAfterDeath) for job_id in job_ids]

            self.populateJobTree()

            if not all(responses):
                warningBox(self, "Error",
                            "One or more nodes couldn't kill their tasks.")

        #Reset Job
        elif mode == "reset":
            choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
            if choice == QMessageBox.No:
                return

            responses = [JobUtils.resetJob(job_id, READY) for job_id in job_ids]

            map(JobUtils.setupNodeLimit, job_ids)
            self.populateJobTree()

            if not all(responses):
                warningBox(self, "Error",
                            "One or more nodes couldn't reset their tasks.")

        #Reset Node Management on Job
        elif mode == "manage":
            choice = yesNoBox(self, "Confirm", Constants.RESETNODEMGMT_STRING)
            if choice == QMessageBox.Yes:
                map(JobUtils.setupNodeLimit, job_ids)
            self.populateJobTree()

        #Toggle Archive on Job
        elif mode in ["archive", "unarchive"]:
            choice = yesNoBox(self, "Confirm",
                            "Really {0} the selected jobs?".format(mode))
            if choice == QMessageBox.No:
                return

            commandList = []
            new = 0 if mode == "unarchive" else 1
            jobCommand = "UPDATE hydra_jobboard SET archived = %s WHERE id = %s"
            commandList = [(new, job_id) for job_id in job_ids]

            try:
                with transaction() as t:
                    for commandTuple in commandList:
                        t.cur.execute(jobCommand, commandTuple)

            except sqlerror as err:
                logger.error(str(err))
                warningBox(self, "SQL Error", str(err))

            finally:
                self.populateJobTree(clear = True)

        else:
            logger.error("Bad job action handler arg")
        #TODO: Remove this?
        JobUtils.updateJobTaskCount(self.currentJobSel)
        self.doUpdate()

    def setJobPriority(self):
        selection = self.getJobTreeSel("Rows")
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
                logger.debug("PrioritizeJob skipped on {0}".format(job_id))

    def callTestFrameBox(self):
        job_ids = self.getJobTreeSel()
        if not job_ids:
            return

        job_id = job_ids[0]
        reply = intBox(self, "StartTestFrames", "Start X Test Frames?", 10)
        if not reply[1]:
            return

        logger.debug("Starting {0} test frames on job_id {1}".format(reply[0], job_id))
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                        cols = ["id", "status"],
                                        multiReturn = True)
        taskIDs = [int(task.id) for task in tasks]
        map(TaskUtils.startTask, taskIDs[0:reply[0]])
        JobUtils.updateJobTaskCount(job_id, tasks = tasks, commit = True)
        JobUtils.manageNodeLimit(job_id)
        self.populateJobTree()

    #---------------------------------------------------------------------#
    #---------------------------TASK HANDLERS-----------------------------#
    #---------------------------------------------------------------------#
    def taskContextMenu(self):
        self.taskMenu = QMenu(self)
        QObject.connect(self.taskMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.taskMenu, "Start Tasks", self.taskActionHandler,
                "Start all tasks selected in the Task Table",
                "start", "Ctrl+Shift+S")
        self.addItem(self.taskMenu, "Pause Tasks", self.taskActionHandler,
                "Pause all tasks selected in the Task Table",
                "pause", "Ctrl+Shift+P")
        self.addItem(self.taskMenu, "Kill Tasks", self.taskActionHandler,
                "Kill all tasks selected in the Task Table", "kill", "Ctrl+Shift+K")
        self.addItem(self.taskMenu, "Reset Tasks", self.taskActionHandler,
                "Reset all tasks selected in the Task Tree", "reset", "Ctrl+Shift+R")
        self.taskMenu.addSeparator()
        self.addItem(self.taskMenu, "Reveal Detailed Data...", self.taskActionHandler,
                "Opens a dialog window the detailed data for the selected tasks.", "data")
        self.addItem(self.taskMenu, "Load LogFile", self.taskActionHandler,
                "Load the log file for all tasks selected in the Task Tree",
                "log", "Ctrl+Shift+L")
        self.taskMenu.popup(QCursor.pos())

    def taskTableEditHandler(self, item):
        #TODO:Verify data, verify changes with user?
        #TODO:Cleanup
        row = int(item.row())
        col = int(item.column())
        newValue = str(item.text())
        task_id = int(self.taskTable.item(row, 0).text())
        valueMap = {1 : "startFrame", 2 : "endFrame", 3 : "host", 5 : "priority",
                    9 : "exitCode"}
        if col in [0,4,6,7,8]:#ID, Status, Start Time, End Time, Duration
            logger.warning("You probably shouldn't edit those...")
            return
        elif col in [1,2,5,9]:#Start Frame, End Frame, Priority, Exit Code
            newValue = int(newValue)
        try:
            query = "UPDATE hydra_taskboard SET {0} = %s WHERE id = %s".format(valueMap[col])
            with transaction() as t:
                t.cur.execute(query, (newValue, task_id))
        except sqlerror as err:
            warningBox(self, "SQL Error", str(err))
            logger.error(str(err))

        self.updateTaskTable()

    def initTaskTable(self, job_id, shotItem):
        job = hydra_jobboard.fetch("WHERE id = %s", (job_id,),
                                    cols = ["id", "maxNodes"])
        sStr = "Task List (Job ID: {0}) (Node Limit: {1})"
        self.taskTableLabel.setText(sStr.format(str(job_id), str(job.maxNodes)))

        taskCols = ["id", "startTime", "endTime", "startFrame", "endFrame",
                "host", "status", "priority", "exitCode"]
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                        cols = taskCols, multiReturn = True)

        self.taskTable.setRowCount(len(tasks))
        self.taskTable.itemChanged.disconnect(self.taskTableEditHandler)
        for pos, task in enumerate(tasks):
            tdiff = None
            if task.endTime:
                tdiff = task.endTime - task.startTime
            elif task.startTime:
                tdiff = datetime.datetime.now().replace(microsecond=0) - task.startTime
            #Populate the taskTable
            self.taskTable.setItem(pos, 0, TableWidgetItem_int(str(task.id)))
            self.taskTable.setItem(pos, 1, TableWidgetItem_int(str(task.startFrame)))
            self.taskTable.setItem(pos, 2, TableWidgetItem_int(str(task.endFrame)))
            self.taskTable.setItem(pos, 3, TableWidgetItem(str(task.host)))
            self.taskTable.setItem(pos, 4, TableWidgetItem(str(niceNames[task.status])))
            self.taskTable.setItem(pos, 5, TableWidgetItem_int(str(task.priority)))
            self.taskTable.setItem(pos, 6, TableWidgetItem_dt(str(task.startTime)))
            self.taskTable.setItem(pos, 7, TableWidgetItem_dt(str(task.endTime)))
            self.taskTable.setItem(pos, 8, TableWidgetItem_dt(str(tdiff)))
            self.taskTable.setItem(pos, 9, TableWidgetItem_int(str(task.exitCode)))
            self.taskTable.item(pos, 4).setBackgroundColor(niceColors[task.status])

        self.taskTable.itemChanged.connect(self.taskTableEditHandler)
        JobUtils.updateJobTaskCount(job_id)
        job = self.fetchJobs("single", job_id)[0]
        self.addJobTreeShot(job)

    def updateTaskTable(self):
        #NOTE:This method is broken because sorting will change the order...
        #Probably doesn't matter since I think I'll change this to a TreeView soon
        if not self.currentJobSel:
            return
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (self.currentJobSel,),
                                        multiReturn = True,
                                        cols = ["host", "status", "startTime",
                                                "endTime", "exitCode"])

        self.taskTable.itemChanged.disconnect(self.taskTableEditHandler)
        for pos, task in enumerate(tasks):
            tdiff = None
            if task.endTime:
                tdiff = task.endTime - task.startTime
            elif task.startTime:
                tdiff = datetime.datetime.now().replace(microsecond=0) - task.startTime
            #Populate the taskTable
            self.taskTable.setItem(pos, 3, TableWidgetItem(str(task.host)))
            self.taskTable.setItem(pos, 4, TableWidgetItem(str(niceNames[task.status])))
            self.taskTable.setItem(pos, 6, TableWidgetItem_dt(str(task.startTime)))
            self.taskTable.setItem(pos, 7, TableWidgetItem_dt(str(task.endTime)))
            self.taskTable.setItem(pos, 8, TableWidgetItem_dt(str(tdiff)))
            self.taskTable.setItem(pos, 9, TableWidgetItem_int(str(task.exitCode)))
            self.taskTable.item(pos, 4).setBackgroundColor(niceColors[task.status])

        self.taskTable.itemChanged.connect(self.taskTableEditHandler)

    def getTaskTableSel(self, mode = "IDs"):
        self.resetStatusBar()
        rows = self.taskTable.selectionModel().selectedRows()
        if len(rows) < 1:
            msg = "Please select something from the Task Table and try again."
            warningBox(self, "Selection Error", msg)
            return

        if mode == "IDs":
            return [self.taskTable.item(ro.row(), 0).text() for ro in rows]
        elif mode == "Rows":
            return [item.row() for item in rows]
        else:
            logger.error("Bad getTaskTableSel mode!")
            return

    def taskActionHandler(self, mode):
        task_ids = self.getTaskTableSel()
        if not task_ids:
            return

        #load Detailed Data
        if mode == "data":
            if len(task_ids) == 1:
                self.revealDataTable(task_ids, hydra_taskboard, "WHERE id = %s")
            else:
                self.revealDetailedHandler(task_ids, hydra_taskboard, "WHERE id = %s")

        #Start Task
        elif mode == "start":
            map(TaskUtils.startTask, task_ids)
            self.updateTaskTable()

        #Reset Task
        elif mode == "reset":
            choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?")
            if choice == QMessageBox.No:
                return
            responses = [TaskUtils.resetTask(t_id, READY) for t_id in task_ids]
            self.updateTaskTable()
            if not all(responses):
                msg = "Unable to reset task {0} because there was an error communicating with it's host.".format(task_id)
                warningBox(self, "Reset Task Error", msg)

        #Pause or Kill Task
        elif mode in ["pause", "kill"]:
            choice = yesNoBox(self, "Confirm", "Really {0} selected tasks?".format(mode))
            if choice == QMessageBox.No:
                return
            statusAfterDeath = KILLED if mode == "kill" else PAUSED
            notKilled = []
            for task_id in task_ids:
                response = TaskUtils.killTask(task_id, statusAfterDeath)
                if not response:
                    notKilled.append(task_id)
            if len(notKilled) > 0:
                warningBox(self, "Error",
                        "Task(s) with id(s) {0} couldn't be killed for some reason.".format(str(notKilled)))
            self.updateTaskTable()
            self.populateJobTree()

        #Load LogFile
        elif mode == "log":
            if len(task_ids) == 1:
                task = hydra_taskboard.fetch("WHERE id = %s", (task_ids[0],),
                                            cols = ["logFile", "host", "id"])
                self.loadLog(task)
            else:
                choice = yesNoBox(self, "Open logs?", "Note, this will open a text"
                                " editor for EACH task selected. Continue?")
                if choice == QMessageBox.No:
                    return
                for task_id in task_ids:
                    task = hydra_taskboard.fetch("WHERE id = %s", (task_id,),
                                                cols = ["logFile", "host", "id"])
                    self.loadLog(task)


        else:
            logger.error("Bad task handler arg")
        #TODO: Get rid of these?
        JobUtils.manageNodeLimit(self.currentJobSel)
        JobUtils.updateJobTaskCount(self.currentJobSel)
        self.doUpdate()

    def loadLog(self, record):
        logFile = record.logFile
        if logFile:
            logFile = os.path.abspath(logFile)
            lSplit = logFile.split("\\")
            lSplit[0] = "\\\\{0}".format(record.host)
            logFile = "\\".join(lSplit)
            logFile = os.path.abspath(logFile)
            if os.path.exists(logFile):
                logger.debug("Opening Log File @ {0}".format(str(logFile)))
                webbrowser.open(logFile)
            else:
                warningBox(self, "Invalid Log File Path",
                        "Invalid log file path for task: {0}".format(record.id))
                logger.error("Invalid log file path for task: {0}".format(record.id))
                logger.error(logFile)
        else:
            warningBox(self, "No Log on File", Constants.NOLOG_STRING.format(record.id))
            logger.warning("No log file on record for task: {0}".format(record.id))

    def advancedSearchHandler(self):
        #results = TaskSearchDialog.create()
        logger.warning("Not Implemeted!")

    def searchByTaskID(self):
        """~~UNTESTED~~"""
        reply = intBox(self, "Search for job via TaskID", 0)
        if reply[1]:
            taskID = int(reply[0])
            cmd = "SELECT job_id FROM hydra_taskboard WHERE id = %s"
            with transaction() as t:
                [task] = t.cur.execute(cmd, (taskID,))
            shotItem = self.jobTree.findItems(str(task.job_id), Qt.MatchRecursive, 1)
            if shotItem != []:
                self.jobTree.itemClicked(shotItem[0], 0)
            else:
                self.warningBox("Error!", "Could not find job for given task!")

    #---------------------------------------------------------------------#
    #---------------------------NODE HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def nodeContextHandler(self):
        self.nodeMenu = QMenu(self)
        QObject.connect(self.nodeMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.nodeMenu, "Online Nodes", self.onlineRenderNodesHandler,
                "Online all selected nodes", hotkey = "Ctrl+Alt+O")
        self.addItem(self.nodeMenu, "Offline Nodes", self.offlineRenderNodesHandler,
                "Offline all selected nodes without killing their current task",
                hotkey = "Ctrl+Alt+Shift+O")
        self.addItem(self.nodeMenu, "Get Off Nodes", self.getOffRenderNodesHandler,
                "Kill task then offline all selected nodes", hotkey = "Ctrl+Alt+G")
        self.nodeMenu.addSeparator()
        self.addItem(self.nodeMenu, "Select by Host Name...", self.selectByHostHandler,
                "Open a dialog to check nodes based on their host name")
        self.addItem(self.nodeMenu, "Reveal Detailed Data...", self.revealNodeDetailedHandler,
                "Opens a dialog window the detailed data for the selected nodes.")
        self.addItem(self.nodeMenu, "Edit Node...", self.nodeEditorTableHandler,
                "Open a dialog to edit selected node's attributes. WIP.")

        self.nodeMenu.popup(QCursor.pos())

    def initRenderNodeTable(self):
        renderCols = ["host", "status", "task_id", "pulse", "software_version",
                        "capabilities", "scheduleEnabled"]
        nodes = hydra_rendernode.fetch(orderTuples = (("host", "ASC"),),
                                            multiReturn = True,
                                            cols = renderCols)
        self.renderNodeTable.setSortingEnabled(False)
        self.renderNodeTable.setRowCount(len(nodes))
        for row, node in enumerate(nodes):
            #Make a nice string for time since last Heartbeat
            timeString = "None"
            if node.pulse:
                total_seconds = (datetime.datetime.now().replace(microsecond=0) - node.pulse).total_seconds()
                hours = int(total_seconds / 60 / 60 )
                minutes = int(total_seconds / 60 % 60)
                seconds = int(total_seconds % 60)
                timeString = "{0} Hours, {1} Mins, {2} Secs ago".format(hours, minutes, seconds)

            nodeVersion = NodeUtils.getSoftwareVersionText(node.software_version)
            self.renderNodeTable.setItem(row, 0, TableWidgetItem(str(node.host)))
            self.renderNodeTable.setItem(row, 1, TableWidgetItem(str(niceNames[node.status])))
            self.renderNodeTable.setItem(row, 2, TableWidgetItem(str(node.task_id)))
            self.renderNodeTable.setItem(row, 3, TableWidgetItem(str(nodeVersion)))
            self.renderNodeTable.setItem(row, 4, TableWidgetItem(str(node.scheduleEnabled)))
            self.renderNodeTable.setItem(row, 5, TableWidgetItem(timeString))
            self.renderNodeTable.setItem(row, 6, TableWidgetItem(str(node.capabilities)))
            self.renderNodeTable.item(row, 1).setBackgroundColor(niceColors[node.status])
            if node.host == self.thisNodeName:
                self.renderNodeTable.item(row, 0).setFont(QFont('Segoe UI', 8, QFont.DemiBold))
        self.renderNodeTable.setSortingEnabled(True)

    def renderNodeTableHandler(self):
        self.resetStatusBar()
        rows = self.renderNodeTable.selectionModel().selectedRows()
        if len(rows) < 1:
            warningBox(self, "Selection Error",
                    "Please select something from the Render Node Table and try again.")
            return
        rows = [item.row() for item in rows]
        nodes = [str(self.renderNodeTable.item(row, 0).text()) for row in rows]
        logger.debug(nodes)
        return nodes

    def onlineRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes?\n" + str(hosts))
        if choice == QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols = ["status", "task_id", "host"])
                NodeUtils.onlineNode(thisNode)
            self.initRenderNodeTable()

    def offlineRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to offline"
                          " these nodes?\n" + str(hosts))
        if choice == QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols = ["status", "task_id", "host"])
                NodeUtils.offlineNode(thisNode)
            self.initRenderNodeTable()

    def getOffRenderNodesHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", Constants.GETOFF_STRING + str(hosts))
        if choice == QMessageBox.No:
            return

        for renderHost in hosts:
            thisNode = hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                cols = ["host", "status", "task_id"])
            NodeUtils.offlineNode(thisNode)
            if thisNode.task_id:
                try:
                    response = TaskUtils.killTask(thisNode.task_id, READY)
                    if not response:
                        logger.warning("Problem killing task durring GetOff on {0}".format(thisNode.host))
                        warningBox(self, "Error",
                                "There was a problem killing the task during GetOff on {0}".format(thisNode.host))
                    else:
                        aboutBox(self, "Success", "Job was reset, {0} offlined.".format(thisNode.host))
                except socketerror:
                    logger.error(socketerror.message)
                    warningBox(self, "Error", Constants.SOCKETERR_STRING)
            else:
                aboutBox(self, "Success", "No job was found on {0}, node offlined".format(thisNode.host))

            self.initRenderNodeTable()

    def nodeEditorTableHandler(self):
        hosts = self.renderNodeTableHandler()
        if not hosts:
            return
        elif len(hosts) > 1:
            choice = yesNoBox(self, "Confirm", Constants.MULTINODEEDIT_STRING)
            if choice == QMessageBox.No:
                aboutBox(self, "Abort", "No action taken.")
            else:
                for host in hosts:
                    self.nodeEditor(host)
        else:
            self.nodeEditor(hosts[0])

        self.doFetch()

    def nodeEditor(self, nodeName):
        thisNode = hydra_rendernode.fetch("WHERE host = %s", (nodeName,),
                                            cols = ["host", "minPriority",
                                                    "capabilities",
                                                    "scheduleEnabled",
                                                    "weekSchedule"])
        comps = thisNode.capabilities.split(" ")
        defaults = {"host" : thisNode.host,
                    "priority" : thisNode.minPriority,
                    "comps" : comps,
                    "scheduleEnabled" : int(thisNode.scheduleEnabled),
                    "weekSchedule" : thisNode.weekSchedule}
        edits = NodeEditorDialog.create(defaults)
        #logger.debug(edits)
        if edits:
            if edits["schedEnabled"]:
                schedEnabled = 1
            else:
                schedEnabled = 0
            query = "UPDATE hydra_rendernode SET minPriority = %s"
            query += ", scheduleEnabled = %s, capabilities = %s"
            query += " WHERE host = %s"
            editsTuple = (edits["priority"], schedEnabled, edits["comps"], nodeName)
            with transaction() as t:
                t.cur.execute(query, editsTuple)
            self.initRenderNodeTable()

    def revealNodeDetailedHandler(self):
        node_list = self.renderNodeTableHandler()
        if node_list:
            if len(node_list) == 1:
                self.revealDataTable(node_list, hydra_rendernode, "WHERE host = %s")
            else:
                self.revealDetailedHandler(node_list, hydra_rendernode, "WHERE host = %s")

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
                    logger.debug("Selecting {0} matched with {1}".format(item, searchString))

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
        thisNode = NodeUtils.getThisNodeData()
        if thisNode:
            NodeUtils.onlineNode(thisNode)
            self.updateStatusBar(thisNode)
            self.initRenderNodeTable()

    def offlineThisNodeHandler(self):
        """Changes the local render node's status to offline if it was idle,
        pending if it was working on something."""
        #Get the most current info from the database
        thisNode = NodeUtils.getThisNodeData()
        if thisNode:
            NodeUtils.offlineNode(thisNode)
            self.updateStatusBar(thisNode)
            self.initRenderNodeTable()

    def getOffThisNodeHandler(self):
        """Offlines the node and sends a message to the render node server
        running on localhost to kill its current task(task will be
        resubmitted)"""
        thisNode = NodeUtils.getThisNodeData()
        if not thisNode:
            logger.error("This Node could not be found while trying to getOff!")
            warningBox(self, "Error", "This Node could not be found while trying to getOff!")
            return

        choice = yesNoBox(self, "Confirm", Constants.GETOFFLOCAL_STRING)
        if choice == QMessageBox.Yes:
            NodeUtils.offlineNode(thisNode)
            if thisNode.task_id:
                task_id = thisNode.task_id
                try:
                    response = TaskUtils.killTask(task_id, READY)
                    if not response:
                        logger.warning("Problem killing task durring GetOff")
                        warningBox(self, "Error",
                                "There was a problem killing the task during GetOff!")
                    else:
                        aboutBox(self, "Success", "Job was reset, node offlined.")
                except socketerror:
                    logger.error(socketerror.message)
                    warningBox(self, "Error", Constants.SOCKETERR_STRING)
            else:
                aboutBox(self, "Success", "No job was found on node, node offlined")
            self.initRenderNodeTable()
            self.updateStatusBar(thisNode)

    def nodeEditorHandler(self):
        if self.thisNodeExists:
            self.nodeEditor(self.thisNodeName)

    #---------------------------------------------------------------------#
    #--------------------------UPDATE HANDLERS----------------------------#
    #---------------------------------------------------------------------#
    def findThisNode(self):
        allNodes = hydra_rendernode.fetch(multiReturn = True, cols = ["host", "status"])
        for node in allNodes:
            if node.host == self.thisNodeName:
                return node
        #If node cannot be found
        warningBox(self, title = "Notice",
                        msg = Constants.DOESNOTEXISTERR_STRING)
        self.setThisNodeButtonsEnabled(False)
        return False

    def doFetch(self):
        """Aggregate method for initilizaing all of the widgets on the default tab."""
        self.initRenderNodeTable()
        self.populateJobTree()
        if self.thisNodeExists:
            thisNode = self.findThisNode()
            self.updateStatusBar(thisNode)

    def doUpdate(self):
        """Smart updater that updates information the current tab on the main
        tabWidget"""
        curTab = self.tabWidget.currentIndex()

        thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                            (self.thisNodeName,))
        self.updateStatusBar(thisNode)
        if curTab == 0:
            #Job List
            self.populateJobTree()
            self.updateTaskTable()
            self.initRenderNodeTable()
        elif curTab == 1:
            #Recent Jobs
            self.updateRenderJobGrid()
        elif curTab == 2:
            #This Node
            if self.thisNodeExists:
                self.updateThisNodeInfo(thisNode)

    def updateThisNodeInfo(self, thisNode):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        self.nodeNameLabel.setText(thisNode.host)
        self.nodeStatusLabel.setText(niceNames[thisNode.status])
        if thisNode.task_id:
            self.taskIDLabel.setText(str(thisNode.task_id))
        else:
            self.taskIDLabel.setText("None")
        self.nodeVersionLabel.setText(NodeUtils.getSoftwareVersionText(thisNode.software_version))
        self.minPriorityLabel.setText(str(thisNode.minPriority))
        self.capabilitiesLabel.setText(thisNode.capabilities)
        self.scheduleEnabled.setText(str(thisNode.scheduleEnabled))
        self.weekSchedule.setText(str(thisNode.weekSchedule))
        self.pulseLabel.setText(str(thisNode.pulse))

    def updateRenderJobGrid(self):
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT %s"
        records = hydra_jobboard.fetch(command, (self.limitSpinBox.value(),),
                                        multiReturn = True)
        try:
            columns = records[0].__dict__.keys()
        except IndexError:
            return None

        columns = [labelFactory(col) for col in columns if col.find("__") is not 0]

        clearLayout(self.taskGrid)
        setupDataGrid(records, columns, self.taskGrid)

    def updateStatusBar(self, thisNode = None):
        with transaction() as t:
            t.cur.execute ("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        #logger.debug("Counts = " + str(counts))
        countString = ", ".join (["{0} {1}".format(count, niceNames[status]) for (count, status) in counts])
        if self.thisNodeExists:
            countString += ", {0} {1}".format(thisNode.host, niceNames[thisNode.status])
        time = datetime.datetime.now().strftime("%H:%M")
        self.statusMsg = "{0} as of {1}".format(countString, time)
        self.statusbar.showMessage(self.statusMsg)

    def resetStatusBar(self):
        self.statusbar.showMessage(self.statusMsg)

    def setThisNodeButtonsEnabled(self, choice):
        """Enables or disables buttons on This Node tab"""
        self.onlineThisNodeButton.setEnabled(choice)
        self.offlineThisNodeButton.setEnabled(choice)
        self.getOffThisNodeButton.setEnabled(choice)
        self.thisNodeButtonsEnabled = choice

    def doNothing(self):
        pass

#This is at the bottom for a specific reason I can't remember
niceColors = {PAUSED: QColor(240,230,200),      #Light Orange
             READY: QColor(255,255,255),        #White
             FINISHED: QColor(200,240,200),     #Light Green
             KILLED: QColor(240,200,200),       #Light Red
             CRASHED: QColor(220,90,90),        #Dark Red
             STARTED: QColor(200,220,240),      #Light Blue
             ERROR: QColor(220,90,90),          #Red
             MANAGED: QColor(240,230,200),      #Light Orange
             IDLE: QColor(255,255,255),         #White
             OFFLINE: QColor(240,240,240),      #Gray
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
