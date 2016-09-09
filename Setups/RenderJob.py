#Standard
import types

#Third Party
from MySQLdb import Error as sqlerror

#Hydra
import Utilities.TaskUtils as TaskUtils
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger

class RenderJob():
    def __init__(self, hydraJob, loadSubtasksOpt = False):
        #TODO: Rename and move to Constants to make it easy to verify data durring sql_table.update()
        """Pass a hydra_jobboard object or an int of the job id you wish to load"""
        self.Commitable_Attrs = ['archived', 'attempts', 'baseCMD', 'byFrame',
                                'endFrame', 'execName', 'failures', 'maxAttempts',
                                'maxNodes', 'niceName', 'owner', 'phase',
                                'priority', 'projectName', 'renderLayerTracker',
                                'renderLayers', 'requirements', 'startFrame',
                                'status', 'taskFile', 'timeout']
        self.SQL_Attrs = self.Commitable_Attrs + ['creationTime', 'id']
        self.loadSubtasksOpt = loadSubtasksOpt
        self.subtasksLoaded = False
        #If the input hydraJob is not a hydra_jobboard instance try to cast it
        #   to an int and load the hydra_jobboard class instance for that id int
        if not isinstance(hydraJob, hydra_jobboard):
            logger.debug("Could not find hydra_jobboard instance, attempting to load via Job ID...")
            try:
                hydraJob = int(hydraJob)
                hydraJob = hydra_jobboard.fetch("WHERE id = %s", (hydraJob,))
            except ValueError:
                logger.error("Could not load RenderJob with the supplied information '{}'".format(hydraJob))
                return None

        logger.debug("Loading Job with id '{}'".format(hydraJob.id))
        self.loads(hydraJob)

    def __repr__(self):
        return "Hydra Render Job Object with ID: {}".format(self.id)

    def loads(self, hydraJobOBJ):
        #Load all valid attributes as class variables
        self.jobOBJ = hydraJobOBJ
        valueDict = {attr : getattr(hydraJobOBJ, attr) for attr in self.SQL_Attrs if hasattr(hydraJobOBJ, attr)}
        self.__dict__.update(valueDict)

        #Job type is hardcoded for now
        self.jobType = "MayaRender"

        #Load all subtasks if self.loadSubtasksOpt is True
        if self.loadSubtasksOpt:
            self.loadSubtasks()
        return True

    def loadSubtasks(self):
        self.subtasksLoaded = True
        self.subTasks = hydra_taskboard.fetch("WHERE job_id = %s", (self.id,),
                                                multiReturn = True)
        self.activeSubTasks = [t for t in self.subTasks if t.status == "S"]

    def reload(self):
        self.loads(hydra_jobboard.fetch("WHERE id = %s", (self.id,)))
        return True

    def start(self):
        with transaction() as t:
            t.cur.execute("UPDATE hydra_jobboard SET status = 'R' WHERE id = %s", (self.id,))
        self.reload()
        return True

    def pause(self):
        with transaction() as t:
            t.cur.execute("UPDATE hydra_jobboard SET status = 'U' WHERE id = %s", (self.id,))
        self.reload()
        return True

    def kill(self, statusAfterDeath = "K", TCPKill = True):
        #TODO: Better exception handling for killing in general
        self.reload()
        if not self.subtasksLoaded:
            self.loadSubtasks()
        idList = [int(t.id) for t in self.activeSubTasks]
        logger.info(idList)
        responses = [TaskUtils.killTask(taskID, statusAfterDeath) for taskID in idList]
        logger.info(responses)
        logger.info(all(responses))

        jobUpdate = "UPDATE hydra_jobboard SET status = %s WHERE id = %s"
        with transaction() as t:
            t.cur.execute(jobUpdate, (statusAfterDeath, self.id))
        self.reload()
        logger.info(all(responses))
        return all(responses)

    def reset(self):
        self.reload()
        response = self.kill("R")
        if not response:
            logger.error("Job Kill was unsuccessful, skipping reset...")
            return False
        renderLayerTracker = ["0" for x in self.renderLayers]
        renderLayerTracker = ",".join(renderLayerTracker)
        with transaction() as t:
            t.cur.execute("UPDATE hydra_jobboard SET renderLayerTracker = %s, failures = '', attempts = '0' WHERE id = %s",
                            (renderLayerTracker, self.id))
        self.reload()
        return True

    def archive(self, mode):
        if type(mode) != int:
            mode = 1 if str(mode)[0].lower() == "t" else 0
        jobCommand = "UPDATE hydra_jobboard SET archived = %s WHERE id = %s"
        with transaction() as t:
            t.cur.execute(jobCommand, (mode, self.id))
        self.reload()
        return True

    def createJobCMD(self, platform = "win32"):
        #TODO:Get path with correct platform
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        if self.jobType == "MayaRender":
            renderList = [self.execsDict[self.execName], self.baseCMD,
                            "-s", str(self.startFrame), "-e",
                            str(self.endFrame), "-b", str(self.byFrame),
                             "-rl", str(self.renderLayer), self.taskFile]

        elif self.jopType == "FusionComp":
            renderList = [self.execsDict[self.execName], self.taskFile,
                            self.baseCMD, "/render", "/frames",
                            "{0}..{1}".format(self.startFrame, self.endFrame),
                            "/by", str(self.byFrame), "/exit"]

        return " ".join(renderList)

    def commit(self):
        """Update the DB with all of the info from this class."""
        valueDict = {attr : getattr(self, attr) for attr in self.Commitable_Attrs if hasattr(self, attr)}
        for k,v in valueDict.iteritems():
            setattr(self.jobOBJ, k, v)
        try:
            with transaction() as t:
                response = self.jobOBJ.update(t)
        except sqlerror as e:
            logger.error(e)
            response = False

        if response:
            self.reload()
            return True
        else:
            logger.error("Could not commit changes... Reverting to last good state.")
            self.reload()
            return False
