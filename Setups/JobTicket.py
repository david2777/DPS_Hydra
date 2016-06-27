"""Setup for job and task tickets which are submitted to the DB."""
#Standard
from datetime import datetime

#Hydra
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *
from Utilities.JobUtils import setupNodeLimit

class UberJobTicket:
    """A Ticket Class for submitting jobs and their subtasks."""
    def __init__(self, execName, baseCMD, startFrame, endFrame, byFrame,
                taskFile, priority, phase, jobStatus, niceName, owner,
                compatabilityList, maxNodes, timeout, project, singleTask):
        self.execName = execName        #VARCHAR(20)
        self.baseCMD = baseCMD          #VARCHAR(255)
        self.startFrame = startFrame    #SMALLINT(6)    ie.(0-65535)
        self.endFrame = endFrame        #SMALLINT(6)    ie.(0-65535)
        self.byFrame = byFrame          #TINYINT(4)     ie.(0-255)
        self.taskFile = taskFile        #VARCHAR(255)
        self.priority = priority        #TINYINT(4)     ie.(0-255)
        self.phase = phase              #TINYINT(4)     ie.(0-255)
        self.jobStatus = jobStatus      #CHAR(1)
        self.niceName = niceName        #VARCHAR(60)
        self.owner = owner              #VARCHAR(45)
        self.compatabilityPattern = ("%"+("%".join(sorted(compatabilityList)))+"%")#VARCHAR(255)
        self.createTime = datetime.now()#DATETIME
        self.maxNodes = maxNodes        #TINYINT(4)     ie.(0-255)
        self.timeout = int(timeout * 60)#SMALLINT(6)    ie.(0-65535)
        self.project = project          #VARCHAR(60)

        self.singleTask = singleTask    #Not in DB

        if not self.singleTask:
            self.frameRange = range(self.startFrame, self.endFrame)
            self.frameList = self.frameRange[0::self.byFrame]
            if self.endFrame not in self.frameList:
                self.frameList.append(self.endFrame)
            self.frameCount = len(self.frameList)
        else:
            self.frameList = [self.startFrame, self.endFrame]
            self.frameCount = 2

        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        if len(self.compatabilityPattern) > 255:
            raise Exception("compatabilityPattern out of range! Must be less than 255 characters after conversion!")

    def createJob(self):
        """Function for building and inserting a job.
        Returns the job so we can use the ID for the tasks"""
        job = hydra_jobboard(execName = self.execName,
                            baseCMD = self.baseCMD,
                            startFrame = self.startFrame,
                            endFrame = self.endFrame,
                            byFrame = self.byFrame,
                            taskFile = self.taskFile,
                            priority = self.priority,
                            phase = self.phase,
                            job_status = self.jobStatus,
                            niceName = self.niceName,
                            owner = self.owner,
                            creationTime = self.createTime,
                            requirements = self.compatabilityPattern,
                            tasksComplete = 0,
                            tasksTotal = self.frameCount,
                            maxNodes = self.maxNodes,
                            timeout = self.timeout,
                            projectName = self.project)

        with transaction() as t:
            job.insert(transaction=t)

        return job

    def createTasks(self):
        """Function for creating and inserting tasks for a range of frames."""
        taskList = []
        for frame in self.frameList:
            if not self.singleTask:
                startFrame = frame
                endFrame = frame
            else:
                startFrame = self.frameList[0]
                endFrame = self.frameList[1]

            task = hydra_taskboard(job_id = self.job_id,
                                    status = self.jobStatus,
                                    priority = self.priority,
                                    requirements = self.compatabilityPattern,
                                    startFrame = startFrame,
                                    endFrame = endFrame)
            taskList.append(task)

        with transaction() as t:
            logger.debug(taskList)
            if not self.singleTask:
                for task in taskList:
                    task.insert(transaction=t)
            else:
                taskList[0].insert(transaction=t)

    def doSubmit(self):
        """The actual function to submit the job and tasks to the DB"""
        job = self.createJob()
        self.job_id = job.id
        self.createTasks()
        setupNodeLimit(self.job_id)
        logger.info("Submitted UberTicket job with id {0}".format(self.job_id))
        return self.job_id


def testJobs():
    prompt = raw_input("Create test Job? ").lower()
    if prompt == "yes" or prompt == "y":
        baseCMD = "-cam RenderCam -rl Beauty -proj \\\\Sample\\Proj -rd \\\\This\\Is\\A\\Sample\\File\\Directory"
        mayaFile = "\\\\This\\Is\\A\\Sample\\File\\Directory\\Sample_Job_Test_010_0010_v01.ma"
        startFrame = 101
        endFrame = 125
        priority = 50
        niceName = "Sample_Job_Test_010_0010_v01"
        owner = "dduvoisin"
        compatabilityList = ["Maya2015", "Redshift", "SoUP"]

        uberPhase01 = UberJobTicket("maya2015Render", baseCMD + "-x 640 -y 360",
                                    startFrame, endFrame, 10, mayaFile, priority,
                                    1, READY, niceName + "_PHASE_01", owner,
                                    compatabilityList, 1, 170, "TEST_PROJECT_01",
                                    False)
        uberPhase01.doSubmit()

        uberPhase02 = UberJobTicket("maya2015Render", baseCMD, startFrame,
                                    endFrame, 1, mayaFile, priority, 2, PAUSED,
                                    niceName + "_PHASE_02", owner,
                                    compatabilityList, 0, 170, "TEST_PROJECT_01",
                                    False)
        uberPhase02.doSubmit()

    raw_input("DONE...")
