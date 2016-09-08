#Standard
import types

#Third Party

#Hydra
import Utilities.TaskUtils as TaskUtils
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger

class RenderJob():
    def __init__(self, hydraJob):
        """Pass a hydra_jobboard object or an int of the job id you wish to load"""
        #If the input hydraJob is not a class instance try to cast it to an int
        #   and load the hydra_jobboard class instance for that id int
        if type(hydraJob) not types.InstanceType:
            try:
                hydraJob = int(hydraJob)
                hydraJob = hydra_jobboard.fetch("WHERE id = %s", (hydraJob,))
            except ValueError:
                logger.error("Could not load RenderJob with the supplied information '{}'".format(hydraJob))
                return None

        logger.debug("Loading Job with id '{}'".format(hydraJob.id))
        self.loads(hydraJob)

    def loads(self, hydraJobOBJ):
        #Job type is hardcoded for now
        self.jobOBJ = hydraJobOBJ
        self.jobType = "MayaRender"
        self.id = int(hydraJobOBJ.id)
        self.niceName = hydraJobOBJ.niceName
        self.projectName = hydraJobOBJ.projectName
        self.owner = hydraJobOBJ.owner
        self.status = hydraJobOBJ.status
        self.creationTime = hydraJobOBJ.creationTime
        self.requirements = hydraJobOBJ.requirements
        self.execName = hydraJobOBJ.execName
        self.baseCMD = hydraJobOBJ.baseCMD
        self.startFrame = int(hydraJobOBJ.startFrame)
        self.endFrame = int(hydraJobOBJ.endFrame)
        self.byFrame = int(hydraJobOBJ.byFrame)
        self.renderLayers = hydraJobOBJ.renderLayers.split(",")
        self.renderLayerTracker = hydraJobOBJ.renderLayerTracker.split(",")
        self.taskFile = "\"{}\"".format(hydraJobOBJ.taskFile)
        self.priority = int(hydraJobOBJ.priority)
        self.phase = int(hydraJobOBJ.phase)
        self.maxNodes = int(hydraJobOBJ.maxNodes)
        self.timeout = int(hydraJobOBJ.timeout)
        self.failures = hydraJobOBJ.failures.split(",")
        self.attempts = int(hydraJobOBJ.attempts)
        self.maxAttempts = int(hydraJobOBJ.maxAttempts)
        self.archived = True if int(hydraJobOBJ.archived) == 1 else False

        self.subTasks = hydra_taskboard.fetch("WHERE job_id = %s", (self.id,),
                                                multiReturn = True)
        self.activeSubTasks = [t for t in self.subTasks if t.status == "S"]
        return True

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
        self.reload()
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

    def updateCompletedTask(self, taskInfo):
        return False

    def __repr__(self):
        pStr = ("Hydra Render Job: {0}\n"+
                "\tName: {1}\n"+
                "\tProject: {2}\n"+
                "\tOwner: {3}\n"
                "\tStatus: {4}\n")
        return pStr.format(self.id, self.niceName, self.projectName,
                            self.owner, self.status)
