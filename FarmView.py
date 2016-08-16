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
        jobHeader = QTreeWidgetItem(["Name", "ID", "Status", "Progress", "Owner",
                                    "Priority", "Start", "End", "Render Layers"])
        self.jobTree.setHeaderItem(jobHeader)
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

        #taskTree header and column widths
        taskHeader = QTreeWidgetItem(["RenderLayer", "ID", "Status", "Host",
                                        "sFrame", "eFrame", "cFrame", "StartTime",
                                        "EndTime", "Duration", "ExitCode"])
        self.taskTree.setHeaderItem(taskHeader)
        self.taskTree.setColumnWidth(0, 130)        #RenderLayer
        self.taskTree.setColumnWidth(1, 50)         #ID
        self.taskTree.setColumnWidth(2, 60)         #Status
        self.taskTree.setColumnWidth(3, 125)        #Host
        self.taskTree.setColumnWidth(4, 50)         #StartFrame
        self.taskTree.setColumnWidth(5, 50)         #EndFrame
        self.taskTree.setColumnWidth(6, 50)         #CurrentFrame
        self.taskTree.setColumnWidth(7, 110)        #Start Time
        self.taskTree.setColumnWidth(8, 110)        #End Time
        self.taskTree.setColumnWidth(9, 75)         #Duration


        #renderNodeTable column widths
        self.renderNodeTable.setColumnWidth(0, 200)     #Host
        self.renderNodeTable.setColumnWidth(1, 70)      #Status
        self.renderNodeTable.setColumnWidth(2, 70)      #Task ID
        self.renderNodeTable.setColumnWidth(3, 110)     #Version
        self.renderNodeTable.setColumnWidth(4, 100)     #Schedule Enabled
        self.renderNodeTable.setColumnWidth(5, 175)     #Heartbeat
        self.renderNodeTable.setColumnWidth(6, 110)     #Capabilities

        #Job List splitter size
        self.splitter_jobList.setSizes([10500, 10000])

        #Get rid of the spaces between gird layouts
        self.gridLayout_taskTree.setContentsMargins(0,0,0,0)
        self.gridLayout_jobListJobs.setContentsMargins(0,0,0,0)

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

        self.taskTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.taskTree.customContextMenuRequested.connect(self.taskContextMenu)
        #self.taskTree.itemChanged.connect(self.taskTreeEditHandler)

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
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Archive Jobs", self.jobActionHandler,
                "Archive Jobs and hide them from the JobTreeView",
                "archive", "Del")
        self.addItem(self.jobMenu, "Unarchive Jobs", self.jobActionHandler,
                "Unarchive Jobs and add them back to the JobTreeView",
                "unarchive", "Shift+Del")
        self.addItem(self.jobMenu, "Reveal Detailed Data...", self.jobActionHandler,
                "Opens a dialog window the detailed data for the selected jobs.", "data")
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Set Job Priority...", self.setJobPriority,
        "Set priority on each job selected in the Job List")
        editJob = self.addItem(self.jobMenu, "Edit Job...", self.doNothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)

        self.jobMenu.popup(QCursor.pos())

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
                                    cols = ["id", "niceName", "status",
                                            "owner", "priority","startFrame",
                                            "endFrame", "maxNodes",
                                            "projectName", "archived",
                                            "renderLayers,"
                                            "renderLayerTracker"])

    def userFilterAction(self):
        self.userFilterCheckbox.setChecked(0) if self.userFilter else 2
        self.userFilter = False if self.userFilter else True
        self.populateJobTree(clear = True)

    def archivedFilterAction(self):
        self.archivedCheckBox.setChecked(0) if self.showArchivedFilter else 2
        self.showArchivedFilter = False if self.showArchivedFilter else True
        self.populateJobTree(clear = True)

    def formatJobData(self, job):
        renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]
        renderLayersTotal = len(renderLayerTracker)
        renderLayersDone = sum([1 for x in renderLayerTracker if x >= job.endFrame])
        totalFrames = sum([(job.endFrame - job.startFrame) for x in renderLayerTracker])
        completeFrames = sum([(x - job.startFrame) for x in renderLayerTracker])
        percent = "{0:.0%}".format(float(completeFrames / totalFrames))
        taskString  = "{0} ({1}/{2})".format(percent, renderLayersDone, renderLayersTotal)

        return [job.niceName, str(job.id), niceNames[job.status],
                taskString, job.owner, str(job.priority), str(job.startFrame),
                str(job.endFrame), str(job.renderLayers)]

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
        shotItem.setBackgroundColor(2, niceColors[job.status])
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
        jobIDs = self.getJobTreeSel()
        if not jobIDs:
            return

        #Start Job
        if mode == "start":
            map(JobUtils.startJob, jobIDs)
            self.populateJobTree()

        #Reveal Detailed Data
        elif mode == "data":
            if len(jobIDs) == 1:
                self.revealDataTable(jobIDs, hydra_jobboard, "WHERE id = %s")
            else:
                self.revealDetailedHandler(jobIDs, hydra_jobboard, "WHERE id = %s")

        #Kill or Pause Job
        elif mode in ["kill", "pause", "reset"]:
            #TODO: Handle failues better
            choice = yesNoBox(self, "Confirm", "Really {0} the selected jobs?".format(mode))
            if choice == QMessageBox.No:
                return

            modeDict = {"kill" : KILLED, "pause" : PAUSED, "reset" : RESET}
            statusAfterDeath = modeDict[mode]

            responses = [JobUtils.killJob(jobID, statusAfterDeath) for jobID in jobIDs]

            self.populateJobTree()

            if not all(responses):
                warningBox(self, "Error",
                            "One or more nodes couldn't kill their tasks.")

        #Toggle Archive on Job
        elif mode in ["archive", "unarchive"]:
            choice = yesNoBox(self, "Confirm",
                            "Really {0} the selected jobs?".format(mode))
            if choice == QMessageBox.No:
                return

            archMode = 1 if mode == "archive" else 0
            responses = [JobUtils.archiveJob(jobID, archMode) for jobID in jobIDs]

            if not all(responses):
                logger.error("Wow somehow Archive Job had an error")

            self.populateJobTree(clear = True)

        else:
            logger.error("Bad job action handler arg")

        self.doUpdate()

    def setJobPriority(self):
        #TODO: Move to main action handler or get rid of main action handler
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

    #---------------------------------------------------------------------#
    #---------------------------TASK HANDLERS-----------------------------#
    #---------------------------------------------------------------------#
    def taskContextMenu(self):
        self.taskMenu = QMenu(self)
        QObject.connect(self.taskMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.taskMenu, "Kill Tasks", self.taskActionHandler,
                "Kill all tasks selected in the Task Table", "kill", "Ctrl+Shift+K")
        self.addItem(self.taskMenu, "Reset Tasks", self.taskActionHandler,
                "Reset all tasks selected in the Task Tree", "reset", "Ctrl+Shift+R")
        self.addItem(self.taskMenu, "Reveal Detailed Data...", self.taskActionHandler,
                "Opens a dialog window the detailed data for the selected tasks.", "data")
        self.addItem(self.taskMenu, "Load LogFile", self.taskActionHandler,
                "Load the log file for all tasks selected in the Task Tree",
                "log", "Ctrl+Shift+L")
        self.taskMenu.popup(QCursor.pos())

    def jobTreeClickedHandler(self):
        """Handles when the user clicks a job in the JobTree by loading the
        task data into the TaskTree"""
        shotItem = self.jobTree.currentItem()
        if shotItem.parent():
            job_id = int(shotItem.text(1))
            self.loadTaskTree(job_id, True)
            self.currentJobSel = job_id
            self.taskTreeLabel.setText("Task Tree (Job ID: {0})".format(job_id))

    def taskTreeEditHandler(self, item):
        pass

    def loadTaskTree(self, job_id, clear = False):
        if clear:
            self.taskTree.clear()
        #SetupTrunks
        job = hydra_jobboard.fetch("WHERE id = %s", (job_id,),
                                    cols = ["id", "renderLayers",
                                            "renderLayerTracker", "startFrame",
                                            "endFrame", "status"])
        for rl in job.renderLayers.split(","):
            root = QTreeWidgetItem(self.taskTree, [rl])
            root.setFont(0, QFont('Segoe UI', 10, QFont.DemiBold))

        #Load tasks
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                        multiReturn = True,
                                        cols = ["id", "renderLayer", "status",
                                                "startTime", "endTime", "host",
                                                "startFrame", "endFrame",
                                                "currentFrame", "exitCode"])
        #Add tasks to taskTree
        for task in tasks:
            roots = self.taskTree.findItems(str(task.renderLayer), Qt.MatchContains)
            if len(roots) > 0:
                root = roots[0]
                taskData = self.formatTaskData(task)
                taskItem = QTreeWidgetItem(root, taskData)
                #Formatting
                taskItem.setBackgroundColor(2, niceColors[task.status])
                if task.host == self.thisNodeName:
                    taskItem.setFont(3, QFont('Segoe UI', 8, QFont.DemiBold))
            else:
                logger.error("Could not find root for renderLayer {0} on task {1}!".format(task.renderLayer, task.id))

        #Add default data if active tasks don't exist and do formatting
        #Note that since the RLs were added in order we can use the same index
        rlTracker = [int(x) for x in job.renderLayerTracker.split(",")]
        for i in range(0,self.taskTree.topLevelItemCount()):
            topLevelItem = self.taskTree.topLevelItem(i)
            if topLevelItem.childCount() < 1:
                defaultTaskData = [topLevelItem.text(0), "None", niceNames[READY],
                                    "None", str(job.startFrame),
                                    str(job.endFrame), str(job.startFrame),
                                    "None", "None", "None", "None"]
                taksItem = QTreeWidgetItem(topLevelItem, defaultTaskData)

            #Add top level formatting to taskTree data
            if rlTracker[i] == job.endFrame:
                topLevelItem.setBackgroundColor(0, niceColors[FINISHED])
            else:
                statusToUse = topLevelItem.child(topLevelItem.childCount() - 1).text(2)
                statusToUse = "Ready" if statusToUse == "Finished" else statusToUse
                topLevelItem.setBackgroundColor(0, niceColors[niceNamesRev[str(statusToUse)]])
                topLevelItem.setExpanded(True)

    def formatTaskData(self, task):
        if task.endTime:
            duration = task.endTime - task.startTime
        elif task.startTime:
            duration = datetime.datetime.now().replace(microsecond=0) - task.startTime
        else:
            duration = None

        return [str(task.renderLayer), str(task.id), niceNames[task.status],
                    str(task.host), str(task.startFrame), str(task.endFrame),
                    str(task.currentFrame), str(task.startTime),
                    str(task.endTime), str(duration), str(task.exitCode)]

    def getTaskTreeSel(self, mode = "IDs"):
        pass

    def taskActionHandler(self, mode):
        pass

    def loadLog(self, record):
        #webbrowser.open(logFile)
        pass

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
            #self.updateTaskTree()
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
             RESET: QColor(240,230,200),      #Light Orange
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
