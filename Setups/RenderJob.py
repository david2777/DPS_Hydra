#Standard

#Third Party

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger

class RenderJob():
    def __init__(self, Hydra_Job_Obj):
        logger.debug("Loading Job with id '{}'".format(Hydra_Job_Obj.id))
        self.loads(Hydra_Job_Obj)

    def loads(self, Hydra_Job_Obj):
        #Job type is hardcoded for now
        self.jobType = "MayaRender"
        self.id = int(Hydra_Job_Obj.id)
        self.niceName = Hydra_Job_Obj.niceName
        self.projectName = Hydra_Job_Obj.projectName
        self.owner = Hydra_Job_Obj.owner
        self.status = Hydra_Job_Obj.status
        self.creationTime = Hydra_Job_Obj.creationTime
        self.requirements = Hydra_Job_Obj.requirements
        self.execName = Hydra_Job_Obj.execName
        self.baseCMD = Hydra_Job_Obj.baseCMD
        self.startFrame = int(Hydra_Job_Obj.startFrame)
        self.endFrame = int(Hydra_Job_Obj.endFrame)
        self.byFrame = int(Hydra_Job_Obj.byFrame)
        self.renderLayer = Hydra_Job_Obj.renderLayers
        self.renderLayerTracker = Hydra_Job_Obj.renderLayerTracker
        self.taskFile = "\"{}\"".format(Hydra_Job_Obj.taskFile)
        self.priority = int(Hydra_Job_Obj.priority)
        self.phase = int(Hydra_Job_Obj.phase)
        self.maxNodes = int(Hydra_Job_Obj.maxNodes)
        self.timeout = int(Hydra_Job_Obj.timeout)
        self.failures = Hydra_Job_Obj.failures
        self.attempts = int(Hydra_Job_Obj.attempts)
        self.maxAttempts = int(Hydra_Job_Obj.maxAttempts)
        self.archived = True if int(Hydra_Job_Obj.archived) == 1 else False

        self.subTasks = hydra_taskboard.fetch("WHERE job_id = %s", (self.id,),
                                                multiReturn = True)
        self.activeSubTasks = [t for t in subTasks if t.status == "S"]
        return True

    def reload(self):
        self.loads(hydra_jobboard.fetch("WHERE id = %s", (self.id,)))
        return True

    def start(self):
        return True

    def pause(self):
        return True

    def kill(self, statusAfterDeath = "K", TCPKill = True):
        return True

    def archive(self, mode):
        return True

    def createJobCMD(self, platform = "win32"):
        #TODO:Get path with correct platform
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        if self.jobType = "MayaRender":
            renderList = [self.execsDict[self.execName], self.baseCMD,
                            "-s", str(self.startFrame), "-e",
                            str(self.endFrame), "-b", str(self.byFrame),
                             "-rl", str(self.renderLayer), self.taskFile]
            return " ".join(renderList)
        else:
            return None

    def __repr__(self):
        pStr = ("Hydra Render Job: {0}\n"+
                "\tName: {1}\n"+
                "\tProject: {2}\n"+
                "\tOwner: {3}\n"
                "\tStatus: {4}\n")
        return pStr.format(self.id, self.niceName, self.projectName,
                            self.owner, self.status)
