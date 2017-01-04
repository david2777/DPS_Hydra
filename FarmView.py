from __future__ import division
#Standard
import os
import sys
import fnmatch
import datetime
import webbrowser
from operator import attrgetter
from collections import defaultdict

#Third Party
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra Qt
from compiled_qt.UI_FarmView import Ui_FarmView
from dialogs_qt.NodeEditorDialog import NodeEditorDialog
from dialogs_qt.DetailedDialog import DetailedDialog
from dialogs_qt.DataTable import DataTableDialog
from dialogs_qt.TaskResetDialog import ResetDialog
from dialogs_qt.MessageBoxes import *

#Hydra
import constants
from dialogs_qt.WidgetFactories import *
from hydra.logging_setup import logger
from hydra.mysql_setup import *
from hydra.threads import *
import utils.hydra_utils as hydra_utils
import utils.node_utils as node_utils

#Doesn't like Qt classes
#pylint: disable=E0602,E1101,C0302

#------------------------------------------------------------------------------#
#--------------------------------Farm View-------------------------------------#
#------------------------------------------------------------------------------#

class FarmView(QMainWindow, Ui_FarmView):
    """FarmView is the queue manager. Used for managing jobs, tasks, and nodes."""
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)

        #Class Variables
        self.thisNodeName = hydra_utils.myHostName()
        logger.info("This host is %s", self.thisNodeName)
        self.username = hydra_utils.getInfoFromCFG("database", "username")
        self.userFilter = False
        self.showArchivedFilter = False
        self.statusMsg = "ERROR"
        self.currentJobSel = None

        with open(hydra_utils.findResource("assets/styleSheet.css"), "r") as myStyles:
            self.setStyleSheet(myStyles.read())

        #My UI Setup Functions
        self.setupTreeViews()
        self.connectButtons()
        self.setupHotkeys()
        self.setWindowIcon(QIcon(hydra_utils.findResource("assets/FarmView.png")))

        #Make sure this node exists
        self.thisNodeButtonsEnabled = True
        self.thisNodeExists = self.findThisNode()

        #Setup Signals
        SIGNAL("doUpdate")
        QObject.connect(self, SIGNAL("doUpdate"), self.doUpdate)

        #Start autoUpdater and then fetch data from DB
        self.autoUpdateThread = stoppableThread(self.doUpdateSignaler, 1, "AutoUpdate_Thread")
        self.doFetch()

    def addItem(self, menu, name, handler, statusTip, hotkey=None):
        #pylint: disable=R0913
        action = QAction(name, self)
        action.setStatusTip(statusTip)
        action.triggered.connect(handler)
        if hotkey:
            action.setShortcut(QKeySequence(hotkey))
        menu.addAction(action)
        return action

    #---------------------------------------------------------------------#
    #--------------------------UI SETUP FUNCTIONS-------------------------#
    #---------------------------------------------------------------------#
    def setupTreeViews(self):
        """Setup the QTreeViewWidgets headers, column spans, and margins"""
        #jobTree header and column widths
        jobHeader = QTreeWidgetItem(["Name", "ID", "Status", "Progress", "Owner",
                                    "Priority", "MPF", "Errors"])
        self.jobTree.setHeaderItem(jobHeader)
        #Must set widths AFTER setting header, same order as header
        widthList = [400, 50, 60, 80, 100, 50, 100]
        for i, x in enumerate(widthList):
            self.jobTree.setColumnWidth(i, x)

        #taskTree header and column widths
        taskHeader = QTreeWidgetItem(["RenderLayer", "ID", "Status", "Host",
                                        "sFrame", "eFrame", "cFrame", "StartTime",
                                        "EndTime", "Duration", "ExitCode"])
        self.taskTree.setHeaderItem(taskHeader)
        #Same order as taskHeader
        widthList = [130, 50, 60, 125, 50, 50, 50, 110, 110, 75]
        for i, x in enumerate(widthList):
            self.taskTree.setColumnWidth(i, x)

        #renderNodeTree column widths
        nodeHeader = QTreeWidgetItem(["Host", "Status", "TaskID", "Version",
                                        "Schedule", "Pulse", "Capabilities"])
        self.renderNodeTree.setHeaderItem(nodeHeader)
        widthList = [200, 70, 70, 85, 75, 175, 110]
        for i, x in enumerate(widthList):
            self.renderNodeTree.setColumnWidth(i, x)

        #Job List splitter size
        self.splitter_jobList.setSizes([10500, 10000])

        #Get rid of the spaces between gird layouts
        self.gridLayout_taskTree.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_jobListJobs.setContentsMargins(0, 0, 0, 0)

    def connectButtons(self):
        """Connect all of the QPushButtons and QCheckBoxes to their actions.
        Connect QMenus to their parents as Context Menus."""
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

        self.renderNodeTree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.renderNodeTree.customContextMenuRequested.connect(self.nodeContextHandler)

    def setupHotkeys(self):
        """Connect QShortcuts to their actions"""
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
        QShortcut(QKeySequence("Ctrl+S"), self, self.startJob)
        QShortcut(QKeySequence("Ctrl+P"), self, self.pauseJob)
        QShortcut(QKeySequence("Ctrl+K"), self, self.killJob)
        QShortcut(QKeySequence("Ctrl+R"), self, self.resetJob)
        QShortcut(QKeySequence("Del"), self, self.archiveJob)
        QShortcut(QKeySequence("Shift+Del"), self, self.unarchiveJob)

    #---------------------------------------------------------------------#
    #---------------------------MISC FUNCTIONS----------------------------#
    #---------------------------------------------------------------------#

    def centralContextHandler(self):
        """Create main Context Menu and add actions to it."""
        self.centralMenu = QMenu(self)
        QObject.connect(self.centralMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.centralMenu, "Update", self.doFetch,
                "Update with the latest information from the Database", "Ctrl+U")

        if self.thisNodeButtonsEnabled:
            self.addItem(self.centralMenu, "Online This Node", self.onlineThisNodeHandler,
                                    "Online This Node", "Ctrl+O")
            self.addItem(self.centralMenu, "Offline This Node", self.offlineThisNodeHandler,
                                    "Wait for the current job to finish then offline this node",
                                    "Ctrl+Shift+O")
            self.addItem(self.centralMenu, "Get Off This Node!", self.getOffThisNodeHandler,
                                    "Kill the current task and offline this node immediately",
                                    "Ctrl+G")

        self.centralMenu.popup(QCursor.pos())

    @staticmethod
    def revealDetailedHandler(data_ids, sqlTable, sqlWhere):
        """Create a dialog box with all the data from mutliple SQL records"""
        dataList = [sqlTable.fetch(sqlWhere, (d_id,)) for d_id in data_ids]
        DetailedDialog.create(dataList)

    @staticmethod
    def revealDataTable(data_ids, sqlTable, sqlWhere):
        """Create a dialog box with all the data from one SQL record"""
        dataList = sqlTable.fetch(sqlWhere, (data_ids,))
        DataTableDialog.create(dataList)

    #---------------------------------------------------------------------#
    #----------------------------JOB HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def jobContextMenu(self):
        """Create a Context Menu for the jobTree"""
        self.jobMenu = QMenu(self)
        QObject.connect(self.jobMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.jobMenu, "Start Jobs", self.startJob,
                "Mark job(s) as Ready so new subtasks can be created",
                "Ctrl+S")
        self.addItem(self.jobMenu, "Pause Jobs", self.pauseJob,
                "Don't make any new subtasks but don't kill existing ones",
                "Ctrl+P")
        self.addItem(self.jobMenu, "Kill Jobs", self.killJob,
                "Kill all subtasks and don't create anymore until job is Started again",
                "Ctrl+K")
        self.addItem(self.jobMenu, "Reset Jobs", self.resetJob,
                "Kill all subtasks and reset each Render Layer to be rendered again",
                "Ctrl+R")
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Archive Jobs", self.archiveJob,
                "Archive Job(s) and hide them from the jobTree",
                "Del")
        self.addItem(self.jobMenu, "Unarchive Jobs", self.unarchiveJob,
                "Unarchive Job(s) and add them back to the jobTree",
                "Shift+Del")
        self.addItem(self.jobMenu, "Reveal Detailed Data...", self.jobDetailedData,
                "Opens a dialog window the detailed data for the selected job(s)")
        self.jobMenu.addSeparator()

        self.addItem(self.jobMenu, "Set Job Priority...", self.prioritizeJob,
        "Set priority on each job selected in the Job List")
        editJob = self.addItem(self.jobMenu, "Edit Job...", self.doNothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)

        self.jobMenu.popup(QCursor.pos())

    def fetchJobs(self, mode="all", job_id=None):
        """Fetch all of the hydra_jobboard jobs corrisponding with the current
        options selected in the UI."""
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
        return hydra_jobboard.fetch(command, commandTuple, multiReturn=True,
                                    cols=["id", "niceName", "status",
                                            "owner", "priority", "startFrame",
                                            "endFrame", "maxNodes",
                                            "projectName", "archived",
                                            "renderLayers", "attempts", "mpf",
                                            "renderLayerTracker"])

    def userFilterAction(self):
        """Toggle fetching only jobs owned by this user"""
        self.userFilter = False if self.userFilter else True
        self.populateJobTree(clear=True)

    def archivedFilterAction(self):
        """Toggle fetching jobs only which are not archived"""
        self.showArchivedFilter = False if self.showArchivedFilter else True
        self.populateJobTree(clear=True)

    @staticmethod
    def formatJobData(job):
        """Takes a hydra_jobboard record and returns an ordered list of the data
        to be inserted into the jobTree"""
        renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]
        renderLayersTotal = len(renderLayerTracker)
        renderLayersDone = sum([1 for x in renderLayerTracker if x >= job.endFrame])
        if job.startFrame != job.endFrame:
            totalFrames = sum([(job.endFrame - job.startFrame) for x in renderLayerTracker])
            startFrames = [x if x > job.startFrame else job.startFrame for x in renderLayerTracker]
            completeFrames = sum([(x - job.startFrame) for x in startFrames])
        else:
            totalFrames = renderLayersTotal
            completeFrames = sum([1 for x in renderLayerTracker if x > 0])
        percent = "{0:.0%}".format(float(completeFrames / totalFrames))
        taskString = "{0} ({1}/{2})".format(percent, renderLayersDone, renderLayersTotal)

        return [job.niceName, str(job.id), niceNames[job.status],
                taskString, job.owner, str(job.priority), str(job.mpf),
                str(job.attempts)]

    def addJobTreeShot(self, job):
        """Adds a hydra_jobboard record to the jobTree, putting it in the
        correct branch and making that branch if needed."""
        jobData = self.formatJobData(job)
        #Search the JobTree for the Job's projectName to see if it already exists
        projSearch = self.jobTree.findItems(str(job.projectName), Qt.MatchExactly)
        if projSearch:
            #If project was found search for job
            shotSearch = self.jobTree.findItems(str(job.id), Qt.MatchRecursive, 1)
            if shotSearch:
                #If job was found update it
                shotItem = shotSearch[0]
                for i in range(0, self.jobTree.columnCount()):
                    shotItem.setData(i, 0, jobData[i])
            else:
                #If job was not found add it as a new item under the project
                projItem = projSearch[0]
                shotItem = QTreeWidgetItem(projItem, jobData)
        else:
            #If project was not found add it and add the job below it
            root = QTreeWidgetItem(self.jobTree, [str(job.projectName)])
            root.setFont(0, QFont('Segoe UI', 10, QFont.DemiBold))
            shotItem = QTreeWidgetItem(root, jobData)

        #Update colors and stuff
        if job.archived == 1:
            for i in range(0, self.jobTree.columnCount()):
                shotItem.setBackgroundColor(i, QColor(200, 200, 200))
        shotItem.setBackgroundColor(2, niceColors[job.status])
        if job.owner == self.username:
            shotItem.setFont(4, QFont('Segoe UI', 8, QFont.DemiBold))

    def populateJobTree(self, clear=False):
        """Loads all fetchable jobs into the jobTree. Clear will clear the
        jobTree before loading the jobs."""
        jobs = self.fetchJobs()
        if not jobs:
            if clear:
                self.jobTree.clear()
            return None

        topLevelOpenList = []
        for i in range(0, self.jobTree.topLevelItemCount()):
            if self.jobTree.topLevelItem(i).isExpanded():
                topLevelOpenList.append(str(self.jobTree.topLevelItem(i).text(0)))

        if clear:
            self.jobTree.clear()

        for job in jobs:
            self.addJobTreeShot(job)

        for i in range(0, self.jobTree.topLevelItemCount()):
            if str(self.jobTree.topLevelItem(i).text(0)) in topLevelOpenList:
                self.jobTree.topLevelItem(i).setExpanded(True)

        labelText = "Job List"
        labelText += " (This User Only)" if self.userFilter else ""
        labelText += " (No Archived Jobs)" if not self.showArchivedFilter else ""
        self.jobTableLabel.setText(labelText + ":")

    def getJobTreeSel(self, mode="IDs"):
        """Returns data from the items selected in the jobTree or None if
        nothing is selected"""
        self.resetStatusBar()
        mySel = self.jobTree.selectedItems()
        if not mySel:
            warningBox(self, "Selection Error",
                        "Please select something from the Job Tree and try again.")
            return None

        if mode == "IDs":
            data = [int(sel.text(1)) for sel in mySel if sel.parent()]

        elif mode == "Rows":
            data = [sel for sel in mySel if sel.parent()]

        return data if data != [] else None

    def jobActionHandler(self, mode):
        """A catch-all function for performing actions on the items selected
        in the jobTree"""
        #pylint: disable=R0912
        jobIDs = self.getJobTreeSel()
        if not jobIDs:
            return None

        cols = ["id", "status", "renderLayers", "renderLayerTracker", "archived",
                "priority", "startFrame", "endFrame", "failures", "attempts"]
        jobOBJs = [hydra_jobboard.fetch("WHERE id = %s", (jID,), cols=cols) for jID in jobIDs]

        #Start Job
        if mode == "start":
            [job.start() for job in jobOBJs]
            self.populateJobTree()

        #Pause Job
        elif mode == "pause":
            [job.pause() for job in jobOBJs]
            self.populateJobTree()

        #Reveal Detailed Data
        elif mode == "data":
            if len(jobIDs) == 1:
                self.revealDataTable(jobIDs, hydra_jobboard, "WHERE id = %s")
            else:
                self.revealDetailedHandler(jobIDs, hydra_jobboard, "WHERE id = %s")

        #Kill
        elif mode == "kill":
            choice = yesNoBox(self, "Confirm", "Really kill the selected jobs?")
            if choice == QMessageBox.No:
                return None

            rawResponses = [job.kill() for job in jobOBJs]
            responses = [all(res) for res in rawResponses]

            self.populateJobTree()

            respString = "Job Kill returned the following errors:\n"
            if not all(responses):
                failureIDXes = [i for i, x in enumerate(responses) if not x]
                for idx in failureIDXes:
                    taskString = "\t"
                    taskFailures = [i for i, x in enumerate(rawResponses[idx]) if not x]
                    statusSuccess = taskFailures[-1]
                    taskSuccess = taskFailures[:-1]
                    taskString += "Job '{}' had ".format(jobIDs[i])
                    if not statusSuccess:
                        taskString += "an error changing its status and "
                    taskString += "{} errors killing subtasks.\n".format(len(taskSuccess))
                    respString += taskString

                logger.error(respString)
                warningBox(self, "Job Kill Errors!", respString)

        #Reset
        elif mode == "reset":
            if len(jobOBJs) > 1:
                choice = yesNoBox(self, "Confirm", "Really reset the selected jobs?\nNote that this will open a dialog for EACH selected job to be reset.")
                if choice == QMessageBox.No:
                    return None

            errList = []
            for job in jobOBJs:
                if job.status in [KILLED, PAUSED, READY, FINISHED]:
                    data = ResetDialog.create([job.renderLayers.split(","),
                                                    job.startFrame])
                    response = job.reset(data)
                else:
                    aboutBox(self, "Warning", "Job {} could not be reset because it is running. Please kill/pause it and try again.".format(job.id))
                    response = 1
                if response < 0:
                    errList.append([response, job.id])

            if errList:
                badStartFrame = [int(x[1]) for x in errList if x[0] == -1]
                badUpdateAttr = [int(x[1]) for x in errList if x[0] == -2]
                errStr = "The following errors occurred during the job reset:\n"

                if badStartFrame:
                    errStr += "\tIDs of jobs given start frame was higher than the job's end frame:\n\t\t{}\n".format(badStartFrame)

                if badUpdateAttr:
                    errStr += "\tIDs of jobs where an unknown error occured while trying to udpdate the attributes in the databse:\n\t\t{}".format(badUpdateAttr)

                aboutBox(self, "Job Reset Errors", errStr)

        #Toggle Archive on Job
        elif mode in ["archive", "unarchive"]:
            choice = yesNoBox(self, "Confirm",
                            "Really {0} the selected jobs?".format(mode))
            if choice == QMessageBox.No:
                return None

            archMode = 1 if mode == "archive" else 0
            responses = [job.archive(archMode) for job in jobOBJs]

            if not all(responses):
                failureIDXes = [i for i, x in enumerate(responses) if not x]
                failureIDs = [jobIDs[i] for i in failureIDXes]
                logger.error("Job Archiver failed on %s", failureIDs)

            self.populateJobTree(clear=True)

        elif mode == "priority":
            for job in jobOBJs:
                msgString = "Priority for job {0}:".format(job.id)
                reply = intBox(self, "Set Job Priority", msgString, job.priority)
                if reply[1]:
                    job.prioritize(reply[0])
                    self.populateJobTree()
                else:
                    logger.debug("PrioritizeJob skipped on %s", job.id)

        self.doUpdate()

    #Convience Functions to get rid of all the functools.partial calls
    def startJob(self):
        self.jobActionHandler("start")

    def pauseJob(self):
        self.jobActionHandler("pause")

    def jobDetailedData(self):
        self.jobActionHandler("data")

    def killJob(self):
        self.jobActionHandler("kill")

    def resetJob(self):
        self.jobActionHandler("reset")

    def archiveJob(self):
        self.jobActionHandler("archive")

    def unarchiveJob(self):
        self.jobActionHandler("unarchive")

    def prioritizeJob(self):
        self.jobActionHandler("priority")


    #---------------------------------------------------------------------#
    #---------------------------TASK HANDLERS-----------------------------#
    #---------------------------------------------------------------------#
    def taskContextMenu(self):
        """Create a Context Menu for the taskTree"""
        self.taskMenu = QMenu(self)
        QObject.connect(self.taskMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.taskMenu, "Kill Tasks", self.killTask,
                "Kill all tasks selected in the Task Table", "Ctrl+Shift+K")
        self.addItem(self.taskMenu, "Reveal Detailed Data...", self.taskDetailedData,
                "Opens a dialog window the detailed data for the selected tasks.")
        self.addItem(self.taskMenu, "Load LogFile...", self.getTaskLog,
                "Load the log file for all tasks selected in the Task Tree",
                "Ctrl+Shift+L")
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

    def loadTaskTree(self, job_id, clear=False):
        """Loads all subtasks into the taskTree given a job id. Clear will
        clear the widget before loading the data."""
        if clear:
            self.taskTree.clear()

        #SetupTrunks
        job = hydra_jobboard.fetch("WHERE id = %s", (job_id,),
                                    cols=["id", "renderLayers",
                                            "renderLayerTracker", "startFrame",
                                            "endFrame", "status", "jobType"])
        for rl in job.renderLayers.split(","):
            rootSearch = self.taskTree.findItems(str(rl), Qt.MatchExactly, 0)
            if rootSearch:
                root = rootSearch[0]
            else:
                root = QTreeWidgetItem(self.taskTree, [rl])
            root.setFont(0, QFont('Segoe UI', 10, QFont.DemiBold))

        #Add tasks to taskTree
        tasks = hydra_taskboard.fetch("WHERE job_id = %s AND archived = '0'", (job_id,),
                                        multiReturn=True,
                                        cols=["id", "renderLayer", "status",
                                                "startTime", "endTime", "host",
                                                "startFrame", "endFrame",
                                                "currentFrame", "exitCode"])

        self.setNodeTaskColors(tasks)

        for task in tasks:
            rootSearch = self.taskTree.findItems(str(task.renderLayer), Qt.MatchExactly, 0)
            if rootSearch:
                root = rootSearch[0]
                taskData = self.formatTaskData(task)
                taskSearch = self.taskTree.findItems(str(task.id), Qt.MatchRecursive, 1)
                if taskSearch:
                    taskItem = taskSearch[0]
                    for i in range(0, self.taskTree.columnCount()):
                        taskItem.setData(i, 0, taskData[i])
                else:
                    taskItem = QTreeWidgetItem(root, taskData)
                #Formatting
                taskItem.setBackgroundColor(2, niceColors[task.status])
                if task.host == self.thisNodeName:
                    taskItem.setFont(3, QFont('Segoe UI', 8, QFont.DemiBold))
            else:
                logger.error("Could not find root for renderLayer %s on task %s!", task.renderLayer, task.id)

        #Add default data if active tasks don't exist
        #Do formatting on all tasks
        #Note that since the RLs were added in order we can use the same index
        rlTracker = [int(x) for x in job.renderLayerTracker.split(",")]
        for i in range(0, self.taskTree.topLevelItemCount()):
            topLevelItem = self.taskTree.topLevelItem(i)
            if topLevelItem.childCount() < 1:
                defaultTaskData = [topLevelItem.text(0), "None", niceNames[READY],
                                    "None", str(job.startFrame),
                                    str(job.endFrame), str(rlTracker[i]),
                                    "None", "None", "None", "None"]
                QTreeWidgetItem(topLevelItem, defaultTaskData)

            #Add top level formatting to taskTree data
            if rlTracker[i] >= job.endFrame:
                topLevelItem.setBackgroundColor(0, niceColors[FINISHED])
            else:
                statusToUse = topLevelItem.child(topLevelItem.childCount() - 1).text(2)
                statusToUse = "Ready" if statusToUse == "Finished" else statusToUse
                topLevelItem.setBackgroundColor(0, niceColors[niceNamesRev[str(statusToUse)]])
                topLevelItem.setExpanded(True)

    @staticmethod
    def formatTaskData(task):
        """Takes a hydra_taskboard record and returns an ordered list of the data
        to be inserted into the taskTree"""
        if task.endTime:
            duration = task.endTime - task.startTime
        elif task.startTime:
            duration = datetime.datetime.now().replace(microsecond=0) - task.startTime
        else:
            duration = None

        startTime = str(task.startTime)[5:] if task.startTime else "None"
        endTime = str(task.endTime)[5:] if task.endTime else "None"

        taskData = [task.renderLayer, task.id, niceNames[task.status], task.host,
                    task.startFrame, task.endFrame, task.currentFrame, startTime,
                    endTime, duration, task.exitCode]

        return map(str, taskData)

    def getTaskTreeSel(self, mode="IDs"):
        """Returns data from the items selected in the taskTree or None if
        nothing is selected"""
        self.resetStatusBar()
        mySel = self.taskTree.selectedItems()
        if not mySel:
            warningBox(self, "Selection Error",
                        "Please select something from the Task Tree and try again.")
            return None

        if mode == "IDs":
            data = [sel.text(1) for sel in mySel if sel.parent()]
            data = [int(taskID) for taskID in data if taskID != "None"]

        elif mode == "Rows":
            data = [sel for sel in mySel if sel.parent() and sel.text(1) != "None"]

        if not data:
            warningBox(self, "Selection Error",
                        "Looks like you selected placeholder tasks. Please select actual tasks to perform actions on them.")
            return None

        return data

    def taskActionHandler(self, mode):
        """A catch-all function for performing actions on the items selected
        in the taskTree"""
        taskIDs = self.getTaskTreeSel("IDs")
        if not taskIDs:
            return None

        if mode == "kill":
            response = yesNoBox(self, "Confirm", "Are you sure you want to kill these tasks: {}".format(taskIDs))
            if response == QMessageBox.No:
                return None
            cols = ["id", "status", "exitCode", "endTime", "host"]
            taskOBJs = [hydra_taskboard.fetch("WHERE id = %s", (t,), cols=cols)
                        for t in taskIDs]
            responses = [task.kill() for task in taskOBJs]
            if not all(responses):
                failureIDXes = [i for i, x in enumerate(responses) if not x]
                failureIDs = [taskIDs[i] for i in failureIDXes]
                logger.error("Task Kill failed on %s", failureIDs)
                warningBox(self, "Task Kill Error!",
                            "Task Kill failed on task(s) with IDs {}".format(failureIDs))

        elif mode == "log":
            if len(taskIDs) > 1:
                choice = yesNoBox(self, "Confirm", "You have {0} tasks selected. Are you sure you want to open {0} logs?".format(len(taskIDs)))
                if choice == QMessageBox.No:
                    return None
            map(self.openLogFile, taskIDs)

        elif mode == "data":
            if len(taskIDs) == 1:
                self.revealDataTable(taskIDs, hydra_taskboard, "WHERE id = %s")
            else:
                self.revealDetailedHandler(taskIDs, hydra_taskboard, "WHERE id = %s")

    #Convience Functions to get rid of all the functools.partial calls
    def killTask(self):
        self.taskActionHandler("kill")

    def getTaskLog(self):
        self.taskActionHandler("log")

    def taskDetailedData(self):
        self.taskActionHandler("data")

    @staticmethod
    def openLogFile(task_id):
        """Opens the default texteditor with the log for the given task_id"""
        taskOBJ = hydra_taskboard.fetch("WHERE id =  %s", (task_id,),
                                        cols=["id", "host"])
        logPath = taskOBJ.getLogPath()
        if os.path.isfile(logPath):
            webbrowser.open(logPath)
        else:
            logger.warning("Log file does not exist or is unreachable.")

    #---------------------------------------------------------------------#
    #---------------------------NODE HANDLERS-----------------------------#
    #---------------------------------------------------------------------#

    def nodeContextHandler(self):
        """Create a Context Menu for the nodeTree"""
        self.nodeMenu = QMenu(self)
        QObject.connect(self.nodeMenu, SIGNAL("aboutToHide()"),
                        self.resetStatusBar)

        self.addItem(self.nodeMenu, "Online Nodes", self.onlineRenderNodesHandler,
                "Online all selected nodes", "Ctrl+Alt+O")
        self.addItem(self.nodeMenu, "Offline Nodes", self.offlineRenderNodesHandler,
                "Offline all selected nodes without killing their current task",
                hotkey="Ctrl+Alt+Shift+O")
        self.addItem(self.nodeMenu, "Get Off Nodes", self.getOffRenderNodesHandler,
                "Kill task then offline all selected nodes", "Ctrl+Alt+G")
        self.nodeMenu.addSeparator()
        self.addItem(self.nodeMenu, "Select by Host Name...", self.selectByHostHandler,
                "Open a dialog to check nodes based on their host name")
        self.addItem(self.nodeMenu, "Reveal Detailed Data...", self.revealNodeDetailedHandler,
                "Opens a dialog window the detailed data for the selected nodes.")
        self.addItem(self.nodeMenu, "Edit Node...", self.nodeEditorTableHandler,
                "Open a dialog to edit selected node's attributes.")

        self.nodeMenu.popup(QCursor.pos())

    def setNodeTaskColors(self, tasks):
        #Reset colors
        for i in range(self.renderNodeTree.topLevelItemCount()):
            self.renderNodeTree.topLevelItem(i).setBackgroundColor(0, niceColors[READY])

        #Set new colors
        if not tasks:
            return
        taskGroups = defaultdict(list)
        for task in tasks:
            taskGroups[str(task.host)].append(task)
        taskGroups = {k : sorted(v, key=attrgetter("id"), reverse=True)[0].status for k, v in taskGroups.iteritems()}
        for node, status in taskGroups.iteritems():
            nodeSearch = self.renderNodeTree.findItems(str(node), Qt.MatchExactly)
            if nodeSearch:
                nodeItem = nodeSearch[0]
                nodeItem.setBackgroundColor(0, niceColors[status])


    def populateNodeTree(self, clear=False):
        """Loads all of the Render Nodes from hydra_rendernode into the nodeTree."""
        if clear:
            self.renderNodeTree.clear()

        renderCols = ["host", "status", "task_id", "pulse", "software_version",
                        "capabilities", "scheduleEnabled"]
        renderNodes = hydra_rendernode.fetch(orderTuples=(("host", "ASC"),),
                                            multiReturn=True, cols=renderCols)

        for node in renderNodes:
            self.addNodeTreeHost(node)

    def addNodeTreeHost(self, node):
        nodeData = self.formatNodeData(node)
        #Search the nodeTree to see if the node already exists in the tree
        nodeSearch = self.renderNodeTree.findItems(str(node.host), Qt.MatchExactly)
        if nodeSearch:
            #If the node was found, update it's information
            nodeItem = nodeSearch[0]
            for i in range(0, self.renderNodeTree.columnCount()):
                nodeItem.setData(i, 0, nodeData[i])
        else:
            #If not add it as a new item
            nodeItem = QTreeWidgetItem(self.renderNodeTree, nodeData)

        #Formatting
        nodeItem.setBackgroundColor(1, niceColors[node.status])
        if node.host == self.thisNodeName:
            nodeItem.setFont(0, QFont('Segoe UI', 8, QFont.DemiBold))

    @staticmethod
    def formatNodeData(node):
        """Given a hydra_rendernode record returns a list of data to be inserted
        into the nodeTree."""
        sched = "True" if node.scheduleEnabled == 1 else "False"
        timeString = "None"
        if node.pulse:
            total_seconds = (datetime.datetime.now().replace(microsecond=0) - node.pulse).total_seconds()
            days = int(total_seconds / 60 / 60 / 24)
            hours = int(total_seconds / 60 / 60 % 24)
            minutes = int(total_seconds / 60 % 60)
            timeString = "{0} Days, {1} Hours, {2} Mins ago".format(days, hours, minutes)

        nodeData = [node.host, niceNames[node.status], node.task_id,
                    node.software_version, sched, timeString, node.capabilities]

        return map(str, nodeData)

    def getNodeTreeSel(self):
        """Returns the name of each node selected in the nodeTree, None if
        nothing is selected."""
        self.resetStatusBar()
        rows = self.renderNodeTree.selectedItems()

        if not rows:
            warningBox(self, "Selection Error",
                    "Please select something from the Render Node Table and try again.")
            return None
        else:
            return [str(item.text(0)) for item in rows]

    def onlineRenderNodesHandler(self):
        """Onlines each node selected in the nodeTree"""
        hosts = self.getNodeTreeSel()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes?\n" + str(hosts))

        if choice == QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols=["status", "task_id", "host"])
                thisNode.online()
            self.populateNodeTree()

    def offlineRenderNodesHandler(self):
        """Offlines each node selected in the nodeTree"""
        hosts = self.getNodeTreeSel()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", "Are you sure you want to offline"
                          " these nodes?\n" + str(hosts))

        if choice == QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols=["status", "task_id", "host"])
                thisNode.offline()
            self.populateNodeTree()

    def getOffRenderNodesHandler(self):
        """Kills and Offlines each node selected in the nodeTree"""
        hosts = self.getNodeTreeSel()
        if not hosts:
            return

        choice = yesNoBox(self, "Confirm", constants.GETOFF_STRING + str(hosts))
        if choice == QMessageBox.No:
            return

        #else
        cols = ["host", "status", "task_id"]
        renderHosts = [hydra_rendernode.fetch("WHERE host = %s", (host,), cols=cols)
                        for host in hosts]

        responses = [host.getOff() for host in renderHosts]
        if not all(responses):
            failureIDXes = [i for i, x in enumerate(responses) if not x]
            failureHosts = [renderHosts[i] for i in failureIDXes]
            logger.error("Could not get off %s", failureHosts)
            warningBox(self, "GetOff Error!",
                        "Could not get off the following hosts: {}".format(failureHosts))

        self.populateNodeTree()

    def nodeEditorTableHandler(self):
        """Opens the NodeEditorDialog for the selected nodes. Confirms with
        the user before opening more than one."""
        hosts = self.getNodeTreeSel()
        if not hosts:
            return None
        elif len(hosts) > 1:
            choice = yesNoBox(self, "Confirm", constants.MULTINODEEDIT_STRING)
            if choice == QMessageBox.Yes:
                for host in hosts:
                    self.nodeEditor(host)
        else:
            self.nodeEditor(hosts[0])

        self.doFetch()

    def nodeEditor(self, host_name):
        """Given a host_name, opens the NodeEditorDialog for editing. Pushes
        any changes made to the database."""
        thisNode = hydra_rendernode.fetch("WHERE host = %s", (host_name,),
                                            cols=["host", "minPriority",
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

        if edits:
            if edits["schedEnabled"]:
                schedEnabled = 1
            else:
                schedEnabled = 0
            query = "UPDATE hydra_rendernode SET minPriority = %s"
            query += ", scheduleEnabled = %s, capabilities = %s"
            query += " WHERE host = %s"
            editsTuple = (edits["priority"], schedEnabled, edits["comps"], host_name)
            with transaction() as t:
                t.cur.execute(query, editsTuple)
            self.populateNodeTree()

    def revealNodeDetailedHandler(self):
        """Opens a deatiled data dialog conataining all of the information
        for each selected node."""
        node_list = self.getNodeTreeSel()
        if node_list:
            if len(node_list) == 1:
                self.revealDataTable(node_list, hydra_rendernode, "WHERE host = %s")
            else:
                self.revealDetailedHandler(node_list, hydra_rendernode, "WHERE host = %s")

    def selectByHostHandler(self):
        """Selects hosts in the nodeTree via host name"""
        reply = strBox(self, "Select By Host Name", "Host (using * as wildcard):")
        if reply[1]:
            colCount = self.renderNodeTree.columnCount() - 1
            searchString = str(reply[0])
            rows = self.renderNodeTree.rowCount()
            for rowIndex in range(0, rows):
                item = str(self.renderNodeTree.item(rowIndex, 0).text())
                if fnmatch.fnmatch(item, searchString):
                    mySel = QTableWidgetSelectionRange(rowIndex, 0, rowIndex, colCount)
                    self.renderNodeTree.setRangeSelected(mySel, True)
                    logger.debug("Selecting %s matched with %s", item, searchString)

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
            self.autoUpdateThread.restart()

    def onlineThisNodeHandler(self):
        """Changes the local render node's status to online if it was offline,
        goes back to started if it was pending offline."""
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            thisNode.online()
            self.updateStatusBar(thisNode)
            self.populateNodeTree()

    def offlineThisNodeHandler(self):
        """Changes the local render node's status to offline if it was idle,
        pending if it was working on something."""
        #Get the most current info from the database
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            thisNode.offline()
            self.updateStatusBar(thisNode)
            self.populateNodeTree()

    def getOffThisNodeHandler(self):
        """Offlines the node and sends a message to the render node server
        running on localhost to kill its current task(task will be
        resubmitted)"""
        thisNode = node_utils.getThisNodeOBJ()
        if not thisNode:
            return

        choice = yesNoBox(self, "Confirm", constants.GETOFFLOCAL_STRING)
        if choice == QMessageBox.Yes:
            response = thisNode.getOff()
            if not response:
                logger.error("Could not GetOff this node!")
                warningBox(self, "GetOff Error", "Could not GetOff this node!")
            self.populateNodeTree()
            self.updateStatusBar(thisNode)

    def nodeEditorHandler(self):
        """Opens a NodeEditorDialog for this node"""
        if self.thisNodeExists:
            self.nodeEditor(self.thisNodeName)

    #---------------------------------------------------------------------#
    #--------------------------UPDATE HANDLERS----------------------------#
    #---------------------------------------------------------------------#

    def findThisNode(self):
        """Makes sure this node exists in the hydra_rendernode board. Alerts
        the user if not."""
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            return thisNode
        else:
            warningBox(self, title="Notice", msg=constants.DOESNOTEXISTERR_STRING)
            self.setThisNodeButtonsEnabled(False)
            return None

    def doFetch(self):
        """Aggregate method for initilizaing all of the widgets on the default tab."""
        self.populateNodeTree()
        self.populateJobTree(clear=True)
        if self.thisNodeExists:
            thisNode = self.findThisNode()
            self.updateStatusBar(thisNode)
        if self.currentJobSel:
            self.loadTaskTree(self.currentJobSel, True)

    def doUpdateSignaler(self):
        """Setup a signaler for updating so that we don't modify the GUI in another thread"""
        self.emit(SIGNAL("doUpdate"))

    def doUpdate(self):
        """Smart updater that updates information the current tab on the main
        tabWidget"""
        curTab = self.tabWidget.currentIndex()

        thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                            (self.thisNodeName,))
        self.updateStatusBar(thisNode)
        if curTab == 0:
            #Main View
            self.populateJobTree()
            if self.currentJobSel:
                self.loadTaskTree(self.currentJobSel)
            self.populateNodeTree()
        elif curTab == 1:
            #Recent Jobs
            self.loadTaskGrid()
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
        self.nodeVersionLabel.setText(str(thisNode.software_version))
        self.minPriorityLabel.setText(str(thisNode.minPriority))
        self.capabilitiesLabel.setText(thisNode.capabilities)
        self.scheduleEnabled.setText(str(thisNode.scheduleEnabled))
        self.weekSchedule.setText(str(thisNode.weekSchedule))
        self.pulseLabel.setText(str(thisNode.pulse))

    def loadTaskGrid(self):
        """Loads data into the taskGrid (Second tab in the UI)"""
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT %s"
        records = hydra_jobboard.fetch(command, (self.limitSpinBox.value(),),
                                        multiReturn=True)
        try:
            columns = records[0].__dict__.keys()
        except IndexError:
            return None

        columns = [labelFactory(col) for col in columns if col.find("__") is not 0]

        clearLayout(self.taskGrid)
        setupDataGrid(records, columns, self.taskGrid)

    def updateStatusBar(self, thisNode=None):
        """Updates the statusbar with the latest status on the farm"""
        with transaction() as t:
            t.cur.execute("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        #logger.debug("Counts = " + str(counts))
        countString = ", ".join(["{0} {1}".format(count, niceNames[status]) for (count, status) in counts])
        if thisNode:
            countString += ", {0} {1}".format(thisNode.host, niceNames[thisNode.status])
        nowTime = datetime.datetime.now().strftime("%H:%M")
        self.statusMsg = "{0} as of {1}".format(countString, nowTime)
        self.statusbar.showMessage(self.statusMsg)

    def resetStatusBar(self):
        """Resets the status to the last set status. Useful after displaying
        tips in the status bar."""
        self.statusbar.showMessage(self.statusMsg)

    def setThisNodeButtonsEnabled(self, choice):
        """Enables or disables buttons on This Node tab"""
        self.onlineThisNodeButton.setEnabled(choice)
        self.offlineThisNodeButton.setEnabled(choice)
        self.getOffThisNodeButton.setEnabled(choice)
        self.thisNodeButtonsEnabled = choice

    @staticmethod
    def doNothing():
        """Does nothing"""
        pass

#This is at the bottom for a specific reason I can't remember
#pylint: disable=C0326
niceColors = {PAUSED: QColor(240,230,200),      #Light Orange
             READY: QColor(255,255,255),        #White
             FINISHED: QColor(200,240,200),     #Light Green
             KILLED: QColor(240,200,200),       #Light Red
             CRASHED: QColor(220,90,90),        #Dark Red
             STARTED: QColor(200,220,240),      #Light Blue
             ERROR: QColor(220,90,90),          #Red
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
    window.autoUpdateThread.terminate()
    sys.exit(retcode)
