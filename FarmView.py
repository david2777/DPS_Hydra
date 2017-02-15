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
from PyQt4 import QtGui, QtCore

#Hydra Qt
from compiled_qt.UI_FarmView import Ui_FarmView
from dialogs_qt.NodeEditorDialog import NodeEditorDialog
from dialogs_qt.DetailedDialog import DetailedDialog
from dialogs_qt.DataTable import DataTableDialog
import dialogs_qt.MessageBoxes as MessageBoxes
import dialogs_qt.WidgetFactories as WidgetFactories

#Hydra
from hydra.logging_setup import logger
import hydra.hydra_sql as sql
import hydra.long_strings as longstr
import hydra.threads as hydra_threads
import utils.hydra_utils as hydra_utils
import utils.node_utils as node_utils

#Doesn't like Qt classes
#pylint: disable=E1101,C0302

#------------------------------------------------------------------------------#
#--------------------------------Farm View-------------------------------------#
#------------------------------------------------------------------------------#

class FarmView(QtGui.QMainWindow, Ui_FarmView):
    """FarmView is the queue manager. Used for managing jobs, tasks, and nodes."""
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
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
        self.setup_tree_views()
        self.connect_buttons()
        self.setup_hotkeys()
        self.setWindowIcon(QtGui.QIcon(hydra_utils.findResource("assets/FarmView.png")))

        #Make sure this node exists
        self.thisNodeButtonsEnabled = True
        self.thisNodeExists = self.find_this_node()

        #Setup Signals
        QtCore.SIGNAL("do_update")
        QtCore.QObject.connect(self, QtCore.SIGNAL("do_update"), self.do_update)

        #Start autoUpdater and then fetch data from DB
        self.autoUpdateThread = hydra_threads.stoppableThread(self.do_update_signaler, 10, "AutoUpdate_Thread")
        self.doFetch()

    def add_item(self, menu, name, handler, statusTip, hotkey=None):
        #pylint: disable=R0913
        action = QtGui.QAction(name, self)
        action.setStatusTip(statusTip)
        action.triggered.connect(handler)
        if hotkey:
            action.setShortcut(QtGui.QKeySequence(hotkey))
        menu.addAction(action)
        return action

    #--------------------------------------------------------------------------#
    #----------------------------UI SETUP FUNCTIONS----------------------------#
    #--------------------------------------------------------------------------#
    def setup_tree_views(self):
        """Setup the QTreeViewWidgets headers, column spans, and margins"""
        #jobTree header and column widths
        jobHeader = QtGui.QTreeWidgetItem(["Name", "ID", "Status", "Progress", "Owner",
                                    "Priority", "MPF", "Errors"])
        self.jobTree.setHeaderItem(jobHeader)
        #Must set widths AFTER setting header, same order as header
        widthList = [400, 50, 60, 80, 100, 50, 100]
        for i, x in enumerate(widthList):
            self.jobTree.setColumnWidth(i, x)

        #taskTree header and column widths
        taskHeader = QtGui.QTreeWidgetItem(["ID", "Status", "Host", "sFrame",
                                            "eFrame", "StartTime", "EndTime",
                                            "Duration", "ExitCode"])
        self.taskTree.setHeaderItem(taskHeader)
        #Same order as taskHeader
        widthList = [50, 60, 125, 50, 50, 50, 110, 120, 75]
        for i, x in enumerate(widthList):
            self.taskTree.setColumnWidth(i, x)

        #renderNodeTree column widths
        nodeHeader = QtGui.QTreeWidgetItem(["Host", "Status", "TaskID", "Version",
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

    def connect_buttons(self):
        """Connect all of the QPushButtons and QCheckBoxes to their actions.
        Connect QMenus to their parents as Context Menus."""
        #Connect tab switch data update
        self.tabWidget.currentChanged.connect(self.do_update)
        #Connect buttons in This Node tab
        self.fetchButton.clicked.connect(self.doFetch)
        self.onlineThisNodeButton.clicked.connect(self.online_this_node_handler)
        self.offlineThisNodeButton.clicked.connect(self.offline_this_node_handler)
        self.getOffThisNodeButton.clicked.connect(self.get_off_this_node_handler)
        self.autoUpdateCheckbox.stateChanged.connect(self.auto_update_handler)
        self.editThisNodeButton.clicked.connect(self.node_editor_handler)

        #jobTree itemClicked
        self.jobTree.itemClicked.connect(self.job_tree_clicked_handler)

        #Connect basic filter checkboxKeys
        self.archivedCheckBox.stateChanged.connect(self.archived_filter_action)
        self.userFilterCheckbox.stateChanged.connect(self.user_filter_action)

        #Connect Context Menus
        self.centralwidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.centralwidget.customContextMenuRequested.connect(self.central_context_handler)

        self.jobTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.jobTree.customContextMenuRequested.connect(self.job_context_menu)

        self.taskTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.taskTree.customContextMenuRequested.connect(self.task_context_menu)

        self.renderNodeTree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.renderNodeTree.customContextMenuRequested.connect(self.node_context_handler)

    def setup_hotkeys(self):
        """Connect QShortcuts to their actions"""
        #This Node
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+O"), self, self.online_this_node_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+O"), self, self.offline_this_node_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+G"), self, self.get_off_this_node_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+U"), self, self.doFetch)

        #Node Table
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+O"), self, self.online_render_nodes_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+Shift+O"), self, self.offline_render_nodes_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+G"), self, self.get_off_render_nodes_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+D"), self, self.reveal_node_detailed_handler)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Alt+E"), self, self.node_editor_table_handler)

        #Job Tree
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, self.start_job)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+P"), self, self.pause_job)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+K"), self, self.kill_job)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+R"), self, self.reset_job)
        QtGui.QShortcut(QtGui.QKeySequence("Del"), self, self.archive_job)
        QtGui.QShortcut(QtGui.QKeySequence("Shift+Del"), self, self.unarchive_job)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+D"), self, self.job_detailed_data)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self, self.prioritize_job)

        #Task Tree
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+S"), self, self.start_task)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+P"), self, self.pause_task)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+K"), self, self.kill_task)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+R"), self, self.reset_task)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+D"), self, self.task_detailed_data)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+L"), self, self.get_task_log)
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+T"), self, self.tail_task_log)

    #--------------------------------------------------------------------------#
    #-----------------------------MISC FUNCTIONS-------------------------------#
    #--------------------------------------------------------------------------#

    def central_context_handler(self):
        """Create main Context Menu and add actions to it."""
        self.centralMenu = QtGui.QMenu(self)
        QtCore.QObject.connect(self.centralMenu, QtCore.SIGNAL("aboutToHide()"),
                        self.reset_status_bar)

        self.add_item(self.centralMenu, "Update", self.doFetch,
                "Update with the latest information from the Database", "Ctrl+U")

        if self.thisNodeButtonsEnabled:
            self.add_item(self.centralMenu, "Online This Node", self.online_this_node_handler,
                                    "Online This Node", "Ctrl+O")
            self.add_item(self.centralMenu, "Offline This Node", self.offline_this_node_handler,
                                    "Wait for the current job to finish then offline this node",
                                    "Ctrl+Shift+O")
            self.add_item(self.centralMenu, "Get Off This Node!", self.get_off_this_node_handler,
                                    "Kill the current task and offline this node immediately",
                                    "Ctrl+G")

        self.centralMenu.popup(QtGui.QCursor.pos())

    @staticmethod
    def reveal_detailed_handler(data_ids, sqlTable, sqlWhere):
        """Create a dialog box with all the data from mutliple SQL records"""
        dataList = [sqlTable.fetch(sqlWhere, (d_id,)) for d_id in data_ids]
        DetailedDialog.create(dataList)

    @staticmethod
    def reveal_data_table(data_ids, sqlTable, sqlWhere):
        """Create a dialog box with all the data from one SQL record"""
        dataList = sqlTable.fetch(sqlWhere, (data_ids,))
        DataTableDialog.create(dataList)

    #--------------------------------------------------------------------------#
    #------------------------------JOB HANDLERS--------------------------------#
    #--------------------------------------------------------------------------#

    def job_context_menu(self):
        """Create a Context Menu for the jobTree"""
        self.jobMenu = QtGui.QMenu(self)
        QtCore.QObject.connect(self.jobMenu, QtCore.SIGNAL("aboutToHide()"),
                        self.reset_status_bar)

        self.add_item(self.jobMenu, "Start Jobs", self.start_job,
                "Mark job(s) as Ready so new subtasks can be created",
                "Ctrl+S")
        self.add_item(self.jobMenu, "Pause Jobs", self.pause_job,
                "Don't make any new subtasks but don't kill existing ones",
                "Ctrl+P")
        self.add_item(self.jobMenu, "Kill Jobs", self.kill_job,
                "Kill all subtasks and don't create anymore until job is Started again",
                "Ctrl+K")
        self.add_item(self.jobMenu, "Reset Jobs", self.reset_job,
                "Kill all subtasks and reset each Render Layer to be rendered again",
                "Ctrl+R")
        self.jobMenu.addSeparator()

        self.add_item(self.jobMenu, "Archive Jobs", self.archive_job,
                "Archive Job(s) and hide them from the jobTree",
                "Del")
        self.add_item(self.jobMenu, "Unarchive Jobs", self.unarchive_job,
                "Unarchive Job(s) and add them back to the jobTree",
                "Shift+Del")
        self.add_item(self.jobMenu, "Reveal Detailed Data...", self.job_detailed_data,
                "Opens a dialog window the detailed data for the selected job(s)",
                "Ctrl+D")
        self.jobMenu.addSeparator()

        self.add_item(self.jobMenu, "Set Job Priority...", self.prioritize_job,
        "Set priority on each job selected in the Job List", "Ctrl+Q")
        editJob = self.add_item(self.jobMenu, "Edit Job...", self.do_nothing,
                            "Edit Job, WIP")
        editJob.setEnabled(False)

        self.jobMenu.popup(QtGui.QCursor.pos())

    def fetch_jobs(self, mode="all", job_id=None):
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
        return sql.hydra_jobboard.fetch(command, commandTuple, multiReturn=True,
                                    cols=["id", "niceName", "status",
                                            "owner", "priority", "startFrame",
                                            "endFrame", "maxNodes",
                                            "projectName", "archived",
                                            "renderLayers", "attempts", "mpf",
                                            "byFrame", "frame_count"])

    def user_filter_action(self):
        """Toggle fetching only jobs owned by this user"""
        self.userFilter = False if self.userFilter else True
        self.populate_job_tree(clear=True)

    def archived_filter_action(self):
        """Toggle fetching jobs only which are not archived"""
        self.showArchivedFilter = False if self.showArchivedFilter else True
        self.populate_job_tree(clear=True)

    @staticmethod
    def format_job_data(job):
        """Takes a hydra_jobboard record and returns an ordered list of the data
        to be inserted into the jobTree"""
        taskString = "{0} ({1}/{2})".format(0, 0, 0)

        return [job.niceName, str(job.id), sql.niceNames[job.status],
                taskString, job.owner, str(job.priority), str(job.mpf),
                str(job.attempts)]

    def add_job_tree_shot(self, job):
        """Adds a hydra_jobboard record to the jobTree, putting it in the
        correct branch and making that branch if needed."""
        jobData = self.format_job_data(job)
        #Search the JobTree for the Job's projectName to see if it already exists
        projSearch = self.jobTree.findItems(str(job.projectName), QtCore.Qt.MatchExactly)
        if projSearch:
            #If project was found search for job
            shotSearch = self.jobTree.findItems(str(job.id), QtCore.Qt.MatchRecursive, 1)
            if shotSearch:
                #If job was found update it
                shotItem = shotSearch[0]
                for i in range(0, self.jobTree.columnCount()):
                    shotItem.setData(i, 0, jobData[i])
            else:
                #If job was not found add it as a new item under the project
                projItem = projSearch[0]
                shotItem = QtGui.QTreeWidgetItem(projItem, jobData)
        else:
            #If project was not found add it and add the job below it
            root = QtGui.QTreeWidgetItem(self.jobTree, [str(job.projectName)])
            root.setFont(0, QtGui.QFont('Segoe UI', 10, QtGui.QFont.DemiBold))
            shotItem = QtGui.QTreeWidgetItem(root, jobData)

        #Update colors and stuff
        if job.archived == 1:
            for i in range(0, self.jobTree.columnCount()):
                shotItem.setBackgroundColor(i, QtGui.QColor(200, 200, 200))
        shotItem.setBackgroundColor(2, niceColors[job.status])
        if job.owner == self.username:
            shotItem.setFont(4, QtGui.QFont('Segoe UI', 8, QtGui.QFont.DemiBold))

    def populate_job_tree(self, clear=False):
        """Loads all fetchable jobs into the jobTree. Clear will clear the
        jobTree before loading the jobs."""
        jobs = self.fetch_jobs()
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
            self.add_job_tree_shot(job)

        for i in range(0, self.jobTree.topLevelItemCount()):
            if str(self.jobTree.topLevelItem(i).text(0)) in topLevelOpenList:
                self.jobTree.topLevelItem(i).setExpanded(True)

        labelText = "Job List"
        labelText += " (This User Only)" if self.userFilter else ""
        labelText += " (No Archived Jobs)" if not self.showArchivedFilter else ""
        self.jobTableLabel.setText(labelText + ":")

    def get_job_tree_sel(self, mode="IDs"):
        """Returns data from the items selected in the jobTree or None if
        nothing is selected"""
        self.reset_status_bar()
        mySel = self.jobTree.selectedItems()
        if not mySel:
            MessageBoxes.warningBox(self, "Selection Error",
                        "Please select something from the Job Tree and try again.")
            return None

        if mode == "IDs":
            data = [int(sel.text(1)) for sel in mySel if sel.parent()]

        elif mode == "Rows":
            data = [sel for sel in mySel if sel.parent()]

        return data if data != [] else None

    def job_action_handler(self, mode):
        """A catch-all function for performing actions on the items selected
        in the jobTree"""
        #pylint: disable=R0912
        jobIDs = self.get_job_tree_sel()
        if not jobIDs:
            return None

        jobOBJs = [sql.hydra_jobboard.fetch("WHERE id = %s", (jID,)) for jID in jobIDs]

        #Start Job
        if mode == "start":
            _ = [job.start() for job in jobOBJs]

        #Pause Job
        elif mode == "pause":
            _ = [job.pause() for job in jobOBJs]

        #Kill
        elif mode == "kill":
            choice = MessageBoxes.yesNoBox(self, "Confirm", "Really kill the selected jobs?")
            if choice == QtGui.QMessageBox.No:
                return None

            rawResponses = [job.kill() for job in jobOBJs]
            responses = [all(res) for res in rawResponses]

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
                MessageBoxes.warningBox(self, "Job Kill Errors!", respString)

        #Reset
        elif mode == "reset":
            jobIDs = [int(job.id) for job in jobOBJs]
            choice = MessageBoxes.yesNoBox(self, "Confirm", "Really reset the following jobs?\n{}".format(jobIDs))
            if choice == QtGui.QMessageBox.No:
                return None

            _ = [job.reset() for job in jobOBJs]

        #Reveal Detailed Data
        elif mode == "data":
            if len(jobIDs) == 1:
                self.reveal_data_table(jobIDs, sql.hydra_jobboard, "WHERE id = %s")
            else:
                self.reveal_detailed_handler(jobIDs, sql.hydra_jobboard, "WHERE id = %s")

        #Toggle Archive on Job
        elif mode in ["archive", "unarchive"]:
            choice = MessageBoxes.yesNoBox(self, "Confirm",
                            "Really {0} the selected jobs?".format(mode))
            if choice == QtGui.QMessageBox.No:
                return None

            archMode = 1 if mode == "archive" else 0
            responses = [job.archive(archMode) for job in jobOBJs]

            if not all(responses):
                failureIDXes = [i for i, x in enumerate(responses) if not x]
                failureIDs = [jobIDs[i] for i in failureIDXes]
                logger.error("Job Archiver failed on %s", failureIDs)

            self.populate_job_tree(clear=True)

        elif mode == "priority":
            for job in jobOBJs:
                msgString = "Priority for job {0}:".format(job.id)
                reply = MessageBoxes.intBox(self, "Set Job Priority", msgString, job.priority)
                if reply[1]:
                    job.prioritize(reply[0])
                    self.populate_job_tree()
                else:
                    logger.debug("PrioritizeJob skipped on %s", job.id)

        self.do_update()

    #Convience Functions to get rid of all the functools.partial calls
    def start_job(self):
        self.job_action_handler("start")

    def pause_job(self):
        self.job_action_handler("pause")

    def job_detailed_data(self):
        self.job_action_handler("data")

    def kill_job(self):
        self.job_action_handler("kill")

    def reset_job(self):
        self.job_action_handler("reset")

    def archive_job(self):
        self.job_action_handler("archive")

    def unarchive_job(self):
        self.job_action_handler("unarchive")

    def prioritize_job(self):
        self.job_action_handler("priority")


    #--------------------------------------------------------------------------#
    #-----------------------------TASK HANDLERS--------------------------------#
    #--------------------------------------------------------------------------#
    def task_context_menu(self):
        """Create a Context Menu for the taskTree"""
        self.taskMenu = QtGui.QMenu(self)
        QtCore.QObject.connect(self.taskMenu, QtCore.SIGNAL("aboutToHide()"),
                        self.reset_status_bar)

        self.add_item(self.taskMenu, "Start Tasks", self.start_task,
                "Start all tasks selected in the Task Table", "Ctrl+Shift+S")
        self.add_item(self.taskMenu, "Pause Tasks", self.pause_task,
                "Pause all tasks selected in the Task Table", "Ctrl+Shift+P")
        self.add_item(self.taskMenu, "Kill Tasks", self.kill_task,
                "Kill all tasks selected in the Task Table", "Ctrl+Shift+K")
        self.add_item(self.taskMenu, "Reset Tasks", self.reset_task,
                "Reset all tasks selected in the Task Table", "Ctrl+Shift+R")
        self.taskMenu.addSeparator()

        self.add_item(self.taskMenu, "Reveal Detailed Data...", self.task_detailed_data,
                "Opens a dialog window the detailed data for the selected tasks.",
                "Ctrl+Shift+D")
        self.add_item(self.taskMenu, "Load LogFile...", self.get_task_log,
                "Load the log file for all tasks selected in the Task Tree",
                "Ctrl+Shift+L")
        self.add_item(self.taskMenu, "Tail LogFile...", self.tail_task_log,
                "Tail the log file for all tasks selected in the Task Tree",
                "Ctrl+Shift+T")
        self.taskMenu.popup(QtGui.QCursor.pos())

    def job_tree_clicked_handler(self):
        """Handles when the user clicks a job in the JobTree by loading the
        task data into the TaskTree"""
        shotItem = self.jobTree.currentItem()
        if shotItem.parent():
            job_id = int(shotItem.text(1))
            self.load_task_tree(job_id, True)
            self.currentJobSel = job_id
            self.taskTreeLabel.setText("Task Tree (Job ID: {0})".format(job_id))

    def load_task_tree(self, job_id, clear=False):
        """Loads all subtasks into the taskTree given a job id. Clear will
        clear the widget before loading the data."""
        if clear:
            self.taskTree.clear()

        taskList = sql.hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                                multiReturn=True)

        for task in taskList:
            taskData = self.format_task_data(task)
            taskSearch = self.taskTree.findItems(str(task.id), QtCore.Qt.MatchRecursive, 0)
            if taskSearch:
                taskItem = taskSearch[0]
                for i in range(0, self.taskTree.columnCount()):
                    taskItem.setData(i, 0, taskData[i])
            else:
                taskItem = QtGui.QTreeWidgetItem(self.taskTree, taskData)

            taskItem.setBackgroundColor(2, niceColors[task.status])
            if task.host == self.thisNodeName:
                taskItem.setFont(2, QtGui.QFont('Segoe UI', 8, QtGui.QFont.DemiBold))

        self.set_node_task_colors(taskList)

    @staticmethod
    def format_task_data(task):
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

        taskData = [task.id, sql.niceNames[task.status], task.host, task.startFrame,
                    task.endFrame, startTime, endTime, duration, task.exitCode]

        return map(str, taskData)

    def get_task_tree_sel(self, mode="IDs"):
        """Returns data from the items selected in the taskTree or None if
        nothing is selected"""
        self.reset_status_bar()
        mySel = self.taskTree.selectedItems()
        if not mySel:
            MessageBoxes.warningBox(self, "Selection Error",
                        "Please select something from the Task Tree and try again.")
            return None

        if mode == "IDs":
            idList = [sel.text(0) for sel in mySel]
            data = [int(taskID) for taskID in idList if taskID != "None"]

        elif mode == "Rows":
            data = [sel for sel in mySel if sel.text(0) != "None"]

        if not data:
            MessageBoxes.warningBox(self, "Selection Error",
                        "Please select one or more tasks from the TaskTree and try again.")
            return None

        return data

    def task_action_handler(self, mode):
        """A catch-all function for performing actions on the items selected
        in the taskTree"""
        taskIDs = self.get_task_tree_sel("IDs")
        if not taskIDs:
            return None

        taskOBJs = [sql.hydra_taskboard.fetch("WHERE id = %s", (t,),) for t in taskIDs]

        if mode == "start":
            _ = [task.start() for task in taskOBJs]

        elif mode == "pause":
            _ = [task.pause() for task in taskOBJs]

        elif mode == "reset":
            response = MessageBoxes.yesNoBox(self, "Confirm", "Are you sure you want to reset the following tasks?\n{}".format(taskIDs))
            if response == QtGui.QMessageBox.No:
                return None
            _ = [task.reset() for task in taskOBJs]

        elif mode == "kill":
            response = MessageBoxes.yesNoBox(self, "Confirm", "Are you sure you want to kill these tasks?\n{}".format(taskIDs))
            if response == QtGui.QMessageBox.No:
                return None
            responses = [task.kill() for task in taskOBJs]
            if not all(responses):
                failureIDXes = [i for i, x in enumerate(responses) if not x]
                failureIDs = [taskIDs[i] for i in failureIDXes]
                logger.error("Task Kill failed on %s", failureIDs)
                MessageBoxes.warningBox(self, "Task Kill Error!",
                            "Task Kill failed on task(s) with IDs {}".format(failureIDs))

        elif mode in ["log", "tail"]:
            if len(taskOBJs) > 1:
                choice = MessageBoxes.yesNoBox(self, "Confirm", "You have {0} tasks selected. Are you sure you want to open {0} logs?".format(len(taskIDs)))
                if choice == QtGui.QMessageBox.No:
                    return None
            _ = [self.open_log_file(task, mode) for task in taskOBJs]

        elif mode == "data":
            if len(taskIDs) == 1:
                self.reveal_data_table(taskIDs, sql.hydra_taskboard, "WHERE id = %s")
            else:
                self.reveal_detailed_handler(taskIDs, sql.hydra_taskboard, "WHERE id = %s")

        self.do_update()

    #Convience Functions to get rid of all the functools.partial calls
    def start_task(self):
        self.task_action_handler("start")

    def pause_task(self):
        self.task_action_handler("pause")

    def reset_task(self):
        self.task_action_handler("reset")

    def kill_task(self):
        self.task_action_handler("kill")

    def get_task_log(self):
        self.task_action_handler("log")

    def tail_task_log(self):
        self.task_action_handler("tail")

    def task_detailed_data(self):
        self.task_action_handler("data")

    def open_log_file(self, task, mode="log"):
        """Opens the default texteditor with the log for the given task_id"""
        logPath = task.get_log_path()
        logger.debug(logPath)
        if logPath and os.path.isfile(logPath):
            if mode == "log":
                webbrowser.open(logPath)
            elif mode == "tail":
                if sys.platform == "win32":
                    cmd = " ".join(["start powershell Get-Content", logPath, "-Wait"])
                    os.system(cmd)
                else:
                    MessageBoxes.aboutBox(self, "Sorry", "This platform doesn't support tail yet...")
            else:
                MessageBoxes.aboutBox(self, "Error", "Bad arg given to open_log_file")
                logger.critical("Bad arg given to open_log_file")
        else:
            MessageBoxes.warningBox(self, "Log Not Found",
                                    "Log could not be found for Task {}".format(int(task.id)))
            logger.warning("Log file does not exist or is unreachable.")

    #--------------------------------------------------------------------------#
    #-----------------------------NODE HANDLERS--------------------------------#
    #--------------------------------------------------------------------------#

    def node_context_handler(self):
        """Create a Context Menu for the nodeTree"""
        self.nodeMenu = QtGui.QMenu(self)
        QtCore.QObject.connect(self.nodeMenu, QtCore.SIGNAL("aboutToHide()"),
                        self.reset_status_bar)

        self.add_item(self.nodeMenu, "Online Nodes", self.online_render_nodes_handler,
                "Online all selected nodes", "Ctrl+Alt+O")
        self.add_item(self.nodeMenu, "Offline Nodes", self.offline_render_nodes_handler,
                "Offline all selected nodes without killing their current task",
                hotkey="Ctrl+Alt+Shift+O")
        self.add_item(self.nodeMenu, "Get Off Nodes", self.get_off_render_nodes_handler,
                "Kill task then offline all selected nodes", "Ctrl+Alt+G")
        self.nodeMenu.addSeparator()
        self.add_item(self.nodeMenu, "Select by Host Name...", self.select_by_host_handler,
                "Open a dialog to check nodes based on their host name")
        self.add_item(self.nodeMenu, "Reveal Detailed Data...", self.reveal_node_detailed_handler,
                "Opens a dialog window the detailed data for the selected nodes.", "Ctrl+Alt+D")
        self.add_item(self.nodeMenu, "Edit Node...", self.node_editor_table_handler,
                "Open a dialog to edit selected node's attributes.", "Ctrl+Alt+E")

        self.nodeMenu.popup(QtGui.QCursor.pos())

    def set_node_task_colors(self, tasks):
        #Reset colors
        for i in range(self.renderNodeTree.topLevelItemCount()):
            self.renderNodeTree.topLevelItem(i).setBackgroundColor(0, niceColors[sql.READY])

        #Set new colors
        if not tasks:
            return
        taskGroups = defaultdict(list)
        for task in tasks:
            taskGroups[str(task.host)].append(task)
        taskGroups = {k : sorted(v, key=attrgetter("id"), reverse=True)[0].status for k, v in taskGroups.iteritems()}
        for node, status in taskGroups.iteritems():
            nodeSearch = self.renderNodeTree.findItems(str(node), QtCore.Qt.MatchExactly)
            if nodeSearch:
                nodeItem = nodeSearch[0]
                nodeItem.setBackgroundColor(0, niceColors[status])


    def populate_node_tree(self, clear=False):
        """Loads all of the Render Nodes from hydra_rendernode into the nodeTree."""
        if clear:
            self.renderNodeTree.clear()

        renderCols = ["host", "status", "task_id", "pulse", "software_version",
                        "capabilities", "schedule_enabled"]
        renderNodes = sql.hydra_rendernode.fetch("ORDER BY host ASC",
                                                    multiReturn=True,
                                                    cols=renderCols)

        for node in renderNodes:
            self.add_node_tree_host(node)

    def add_node_tree_host(self, node):
        nodeData = self.format_node_data(node)
        #Search the nodeTree to see if the node already exists in the tree
        nodeSearch = self.renderNodeTree.findItems(str(node.host), QtCore.Qt.MatchExactly)
        if nodeSearch:
            #If the node was found, update it's information
            nodeItem = nodeSearch[0]
            for i in range(0, self.renderNodeTree.columnCount()):
                nodeItem.setData(i, 0, nodeData[i])
        else:
            #If not add it as a new item
            nodeItem = QtGui.QTreeWidgetItem(self.renderNodeTree, nodeData)

        #Formatting
        nodeItem.setBackgroundColor(1, niceColors[node.status])
        if node.host == self.thisNodeName:
            nodeItem.setFont(0, QtGui.QFont('Segoe UI', 8, QtGui.QFont.DemiBold))

    @staticmethod
    def format_node_data(node):
        """Given a hydra_rendernode record returns a list of data to be inserted
        into the nodeTree."""
        sched = "True" if node.schedule_enabled == 1 else "False"
        timeString = "None"
        if node.pulse:
            total_seconds = (datetime.datetime.now().replace(microsecond=0) - node.pulse).total_seconds()
            days = int(total_seconds / 60 / 60 / 24)
            hours = int(total_seconds / 60 / 60 % 24)
            minutes = int(total_seconds / 60 % 60)
            timeString = "{0} Days, {1} Hours, {2} Mins ago".format(days, hours, minutes)

        nodeData = [node.host, sql.niceNames[node.status], node.task_id,
                    node.software_version, sched, timeString, node.capabilities]

        return map(str, nodeData)

    def get_node_tree_sel(self):
        """Returns the name of each node selected in the nodeTree, None if
        nothing is selected."""
        self.reset_status_bar()
        rows = self.renderNodeTree.selectedItems()

        if not rows:
            MessageBoxes.warningBox(self, "Selection Error",
                    "Please select something from the Render Node Table and try again.")
            return None
        else:
            return [str(item.text(0)) for item in rows]

    def online_render_nodes_handler(self):
        """Onlines each node selected in the nodeTree"""
        hosts = self.get_node_tree_sel()
        if not hosts:
            return

        choice = MessageBoxes.yesNoBox(self, "Confirm", "Are you sure you want to online"
                          " these nodes?\n" + str(hosts))

        if choice == QtGui.QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols=["status", "task_id", "host"])
                thisNode.online()
            self.populate_node_tree()

    def offline_render_nodes_handler(self):
        """Offlines each node selected in the nodeTree"""
        hosts = self.get_node_tree_sel()
        if not hosts:
            return

        choice = MessageBoxes.yesNoBox(self, "Confirm", "Are you sure you want to offline"
                          " these nodes?\n" + str(hosts))

        if choice == QtGui.QMessageBox.Yes:
            for renderHost in hosts:
                thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (renderHost,),
                                                    cols=["status", "task_id", "host"])
                thisNode.offline()
            self.populate_node_tree()

    def get_off_render_nodes_handler(self):
        """Kills and Offlines each node selected in the nodeTree"""
        hosts = self.get_node_tree_sel()
        if not hosts:
            return

        choice = MessageBoxes.yesNoBox(self, "Confirm", longstr.GetOff_String + str(hosts))
        if choice == QtGui.QMessageBox.No:
            return

        #else
        cols = ["host", "status", "task_id"]
        renderHosts = [sql.hydra_rendernode.fetch("WHERE host = %s", (host,), cols=cols)
                        for host in hosts]

        responses = [host.getOff() for host in renderHosts]
        if not all(responses):
            failureIDXes = [i for i, x in enumerate(responses) if not x]
            failureHosts = [renderHosts[i] for i in failureIDXes]
            logger.error("Could not get off %s", failureHosts)
            MessageBoxes.warningBox(self, "GetOff Error!",
                        "Could not get off the following hosts: {}".format(failureHosts))

        self.populate_node_tree()

    def node_editor_table_handler(self):
        """Opens the NodeEditorDialog for the selected nodes. Confirms with
        the user before opening more than one."""
        hosts = self.get_node_tree_sel()
        if not hosts:
            return None
        elif len(hosts) > 1:
            choice = MessageBoxes.yesNoBox(self, "Confirm", longstr.MultiNodeEdit_String)
            if choice == QtGui.QMessageBox.Yes:
                for host in hosts:
                    self.node_editor(host)
        else:
            self.node_editor(hosts[0])

        self.doFetch()

    def node_editor(self, host_name):
        """Given a host_name, opens the NodeEditorDialog for editing. Pushes
        any changes made to the database."""
        thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (host_name,),
                                            cols=["host", "minPriority",
                                                    "capabilities",
                                                    "schedule_enabled",
                                                    "week_schedule"])
        comps = thisNode.capabilities.split(" ")
        defaults = {"host" : thisNode.host,
                    "priority" : thisNode.minPriority,
                    "comps" : comps,
                    "schedule_enabled" : int(thisNode.schedule_enabled),
                    "week_schedule" : thisNode.week_schedule}
        edits = NodeEditorDialog.create(defaults)

        if edits:
            if edits["schedEnabled"]:
                schedEnabled = 1
            else:
                schedEnabled = 0
            query = "UPDATE hydra_rendernode SET minPriority = %s"
            query += ", schedule_enabled = %s, capabilities = %s"
            query += " WHERE host = %s"
            editsTuple = (edits["priority"], schedEnabled, edits["comps"], host_name)
            with sql.transaction() as t:
                t.cur.execute(query, editsTuple)
            self.populate_node_tree()

    def reveal_node_detailed_handler(self):
        """Opens a deatiled data dialog conataining all of the information
        for each selected node."""
        node_list = self.get_node_tree_sel()
        if node_list:
            if len(node_list) == 1:
                self.reveal_data_table(node_list, sql.hydra_rendernode, "WHERE host = %s")
            else:
                self.reveal_detailed_handler(node_list, sql.hydra_rendernode, "WHERE host = %s")

    def select_by_host_handler(self):
        """Selects hosts in the nodeTree via host name"""
        reply = MessageBoxes.strBox(self, "Select By Host Name", "Host (using * as wildcard):")
        if reply[1]:
            colCount = self.renderNodeTree.columnCount() - 1
            searchString = str(reply[0])
            rows = self.renderNodeTree.rowCount()
            for rowIndex in range(0, rows):
                item = str(self.renderNodeTree.item(rowIndex, 0).text())
                if fnmatch.fnmatch(item, searchString):
                    mySel = QtGui.QTableWidgetSelectionRange(rowIndex, 0, rowIndex, colCount)
                    self.renderNodeTree.setRangeSelected(mySel, True)
                    logger.debug("Selecting %s matched with %s", item, searchString)

    #--------------------------------------------------------------------------#
    #------------------------THIS NODE BUTTON HANDLERS-------------------------#
    #--------------------------------------------------------------------------#

    def auto_update_handler(self):
        """Toggles Auto Updater
        Note that this is run AFTER the CheckState is changed so when we do
        .isChecked() it's looking for the state after it has been checked."""
        if not self.autoUpdateCheckbox.isChecked():
            self.autoUpdateThread.terminate()
        else:
            self.autoUpdateThread.restart()

    def online_this_node_handler(self):
        """Changes the local render node's status to online if it was offline,
        goes back to started if it was pending offline."""
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            thisNode.online()
            self.update_status_bar(thisNode)
            self.populate_node_tree()

    def offline_this_node_handler(self):
        """Changes the local render node's status to offline if it was idle,
        pending if it was working on something."""
        #Get the most current info from the database
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            thisNode.offline()
            self.update_status_bar(thisNode)
            self.populate_node_tree()

    def get_off_this_node_handler(self):
        """Offlines the node and sends a message to the render node server
        running on localhost to kill its current task(task will be
        resubmitted)"""
        thisNode = node_utils.getThisNodeOBJ()
        if not thisNode:
            return

        choice = MessageBoxes.yesNoBox(self, "Confirm", longstr.GetOffLocal_String)
        if choice == QtGui.QMessageBox.Yes:
            response = thisNode.getOff()
            if not response:
                logger.error("Could not GetOff this node!")
                MessageBoxes.warningBox(self, "GetOff Error", "Could not GetOff this node!")
            self.populate_node_tree()
            self.update_status_bar(thisNode)

    def node_editor_handler(self):
        """Opens a NodeEditorDialog for this node"""
        if self.thisNodeExists:
            self.node_editor(self.thisNodeName)

    #--------------------------------------------------------------------------#
    #----------------------------UPDATE HANDLERS-------------------------------#
    #--------------------------------------------------------------------------#

    def find_this_node(self):
        """Makes sure this node exists in the hydra_rendernode board. Alerts
        the user if not."""
        thisNode = node_utils.getThisNodeOBJ()
        if thisNode:
            return thisNode
        else:
            MessageBoxes.warningBox(self, title="Notice", msg=longstr.DoesNotExist_Str)
            self.set_this_node_buttons_enabled(False)
            return None

    def doFetch(self):
        """Aggregate method for initilizaing all of the widgets on the default tab."""
        self.populate_node_tree()
        self.populate_job_tree(clear=True)
        if self.thisNodeExists:
            thisNode = self.find_this_node()
            self.update_status_bar(thisNode)
        if self.currentJobSel:
            self.load_task_tree(self.currentJobSel, True)

    def do_update_signaler(self):
        """Setup a signaler for updating so that we don't modify the GUI in another thread"""
        self.emit(QtCore.SIGNAL("do_update"))

    def do_update(self):
        """Smart updater that updates information the current tab on the main
        tabWidget"""
        curTab = self.tabWidget.currentIndex()

        thisNode = sql.hydra_rendernode.fetch("WHERE host = %s",
                                                (self.thisNodeName,))
        self.update_status_bar(thisNode)
        if curTab == 0:
            #Main View
            self.populate_job_tree()
            if self.currentJobSel:
                self.load_task_tree(self.currentJobSel)
            self.populate_node_tree()
        elif curTab == 1:
            #Recent Jobs
            self.load_task_grid()
        elif curTab == 2:
            #This Node
            if self.thisNodeExists:
                self.update_this_node_info(thisNode)

    def update_this_node_info(self, thisNode):
        """Updates widgets on the "This Node" tab with the most recent
        information available."""
        self.nodeNameLabel.setText(thisNode.host)
        self.nodeStatusLabel.setText(sql.niceNames[thisNode.status])
        if thisNode.task_id:
            self.taskIDLabel.setText(str(thisNode.task_id))
        else:
            self.taskIDLabel.setText("None")
        self.nodeVersionLabel.setText(str(thisNode.software_version))
        self.minPriorityLabel.setText(str(thisNode.minPriority))
        self.capabilitiesLabel.setText(thisNode.capabilities)
        self.scheduleEnabled.setText(str(thisNode.schedule_enabled))
        self.weekSchedule.setText(str(thisNode.week_schedule))
        self.pulseLabel.setText(str(thisNode.pulse))

    def load_task_grid(self):
        """Loads data into the taskGrid (Second tab in the UI)"""
        command = "WHERE archived = '0' ORDER BY id DESC LIMIT %s"
        records = sql.hydra_jobboard.fetch(command, (self.limitSpinBox.value(),),
                                            multiReturn=True)
        try:
            columns = records[0].__dict__.keys()
        except IndexError:
            return None

        columns = [WidgetFactories.labelFactory(col) for col in columns if col.find("__") is not 0]

        WidgetFactories.clearLayout(self.taskGrid)
        WidgetFactories.setupDataGrid(records, columns, self.taskGrid)

    def update_status_bar(self, thisNode=None):
        """Updates the statusbar with the latest status on the farm"""
        with sql.transaction() as t:
            t.cur.execute("SELECT count(status), status FROM hydra_rendernode GROUP BY status")
            counts = t.cur.fetchall()
        #logger.debug("Counts = " + str(counts))
        countString = ", ".join(["{0} {1}".format(count, sql.niceNames[status]) for (count, status) in counts])
        if thisNode:
            countString += ", {0} {1}".format(thisNode.host, sql.niceNames[thisNode.status])
        nowTime = datetime.datetime.now().strftime("%H:%M")
        self.statusMsg = "{0} as of {1}".format(countString, nowTime)
        self.statusbar.showMessage(self.statusMsg)

    def reset_status_bar(self):
        """Resets the status to the last set status. Useful after displaying
        tips in the status bar."""
        self.statusbar.showMessage(self.statusMsg)

    def set_this_node_buttons_enabled(self, choice):
        """Enables or disables buttons on This Node tab"""
        self.onlineThisNodeButton.setEnabled(choice)
        self.offlineThisNodeButton.setEnabled(choice)
        self.getOffThisNodeButton.setEnabled(choice)
        self.thisNodeButtonsEnabled = choice

    @staticmethod
    def do_nothing():
        """Does nothing"""
        pass

#This is at the bottom for a specific reason I can't remember
#pylint: disable=C0326
niceColors = {sql.PAUSED: QtGui.QColor(240,230,200),      #Light Orange
             sql.READY: QtGui.QColor(255,255,255),        #White
             sql.FINISHED: QtGui.QColor(200,240,200),     #Light Green
             sql.KILLED: QtGui.QColor(240,200,200),       #Light Red
             sql.CRASHED: QtGui.QColor(220,90,90),        #Dark Red
             sql.STARTED: QtGui.QColor(200,220,240),      #Light Blue
             sql.ERROR: QtGui.QColor(220,90,90),          #Red
             sql.IDLE: QtGui.QColor(255,255,255),         #White
             sql.OFFLINE: QtGui.QColor(240,240,240),      #Gray
             sql.PENDING: QtGui.QColor(240,230,200),      #Orange
             sql.TIMEOUT: QtGui.QColor(220,90,90),        #Dark Red
             }

#------------------------------------------------------------------------------#
#-------------------------------------MAIN-------------------------------------#
#------------------------------------------------------------------------------#

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = FarmView()
    window.show()
    retcode = app.exec_()
    window.autoUpdateThread.terminate()
    sys.exit(retcode)
