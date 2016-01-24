#Standard
from datetime import datetime

#Hydra
from LoggingSetup import logger
from MySQLSetup import hydra_jobboard, hydra_taskboard, hydra_executable, transaction

"""
Contains a class with functions for submitting a job to the DB.
Also has a main function for generating test data.
"""

class UberJobTicket:
    """A Ticket Class for submitting jobs and their subtasks."""
    def __init__(self, execName, baseCMD, startFrame, endFrame, byFrame, taskFile, priority,
                phase, jobStatus, niceName, owner, compatabilityList, maxNodes):

        #Looks good, let's setup our class variables
        self.execName = execName        #VARCHAR(20)
        self.baseCMD = baseCMD          #VARCHAR(255)
        self.startFrame = startFrame    #SMALLINT   ie.(0-65535)
        self.endFrame = endFrame        #SMALLINT   ie.(0-65535)
        self.byFrame = byFrame          #TINYINT   ie.(0-255)
        self.taskFile = taskFile        #VARCHAR(255)
        self.priority = priority        #TINYINT    ie.(0-255)
        self.phase = phase              #TINYINT    ie.(0-255)
        self.jobStatus = jobStatus      #CHAR(1)
        self.niceName = niceName        #VARCHAR(60)
        self.owner = owner              #VARCHAR(45)
        self.compatabilityPattern = self.compatabilityBuilder(compatabilityList)    #VARCHAR(255)
        self.createTime = datetime.now()
        self.maxNodes = maxNodes
        
        self.frameRange = range(self.startFrame, self.endFrame)
        self.frameList = self.frameRange[0::self.byFrame]
        if self.endFrame not in self.frameList:
            self.frameList.append(self.endFrame)
        self.frameCount = len(self.frameList)
        
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        #Check this after we run it through the builder function
        if len(self.compatabilityPattern) > 255:
            raise Exception("compatabilityPattern out of range! Must be less than 255 characters after conversion!")

    def compatabilityBuilder(self, compatabilityList):
        """Sorts compatabilityList and joins it with "%"s"""
        compStr = "%".join(sorted(compatabilityList))
        return "%" + compStr + "%"

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
                            maxNodes = self.maxNodes)

        with transaction() as t:
            job.insert(transaction=t)

        return job

    def createTasks(self):
        """Function for creating and inserting tasks for a range of frames."""
        for frame in self.frameList:
            task = hydra_taskboard(job_id = self.job_id,
                                  status = self.jobStatus,
                                  priority = self.priority,
                                  requirements = self.compatabilityPattern,
                                  startFrame = frame,
                                  endFrame = frame)

            with transaction() as t:
                task.insert(transaction=t)

    def doSubmit(self):
        """The actual function to submit the job and tasks to the DB"""
        job = self.createJob()
        self.job_id = job.id
        self.createTasks()
        logger.info("Submitted UberTicket job with id {0}".format(self.job_id))
        return self.job_id

    def createCMDTicketTask(self):
        """Command for making a task for a CMD Ticket.

        Not sure why you'd ever need a CMD Ticket but it was in the original
        Hydra so I figured I'd include it in the new UberTicket

        ***UNTESTED***"""
        command = [self.baseCMD]
        logger.debug(command)
        task = hydra_taskboard(command = command,
                              job_id = self.job_id,
                              status = self.jobStatus,
                              priority = self.priority,
                              createTime = self.createTime,
                              requirements = self.compatabilityPattern
                              )

        with transaction() as t:
            task.insert(transaction=t)

    def doSubmitCMDTicket(self):
        """Command for submitting a CMDTicket.

        Not sure why you'd ever need a CMD Ticket but it was in the original
        Hydra so I figured I'd include it in the new UberTicket

        ***UNTESTED***"""
        job = self.createJob()
        self.job_id = job.id
        self.createCMDTicketTask()
        logger.info("Submitted UberTicket CMDTicket job with id {0}".format(self.job_id))
        
    def __repr__(self):
        reprList = ["\nJob Ticket Repr:",
                    self.execName,
                    self.baseCMD,
                    self.startFrame,
                    self.endFrame,
                    self.byFrame,
                    self.taskFile,
                    self.priority,
                    self.phase,
                    self.jobStatus,
                    self.niceName,
                    self.owner,
                    self.createTime,
                    self.compatabilityPattern,
                    "\n"]
        reprList = [str(x) for x in reprList]
        return "\n".join(reprList)


if __name__ == "__main__":
    prompt = raw_input("Create test Job? ").lower()
    if prompt == "yes" or prompt == "y":
        baseCMD = "-x 640 -y 360 -rl Beauty -proj \\\\zed\\Lego -rd C:\\Users\DPSPurple\\Desktop\\testFrames"
        mayaFile = "\\\\zed\\Lego\\Legodk\\LEGO Minecraft\\1HY16_Loopable_Spins\\21125\\Animation\\seq_010\\shot_010_0010\\maya\\lighting\\Minecraft_21125_shot_010_0010_lit_v08.ma"
        startFrame = 101
        endFrame = 275
        byFrame = 30
        priority = 50
        niceName = "Minecraft_Test"
        owner = "dduvoisin"
        compatabilityList = ["MentalRay", "Maya2015"]

        uberPhase01 = UberJobTicket("maya2015Render", baseCMD, startFrame, endFrame, byFrame, mayaFile,
        priority, 1, "R", niceName + "_PHASE_01", owner, compatabilityList, 0)
        uberPhase01.doSubmit()

        #uberPhase02 = UberJobTicket("maya2014Render", baseCMD, proj, startFrame, endFrame, 1, mayaFile,
        #priority, 2, "U", niceName + "_PHASE_02", owner, compatabilityList, 0)
        #uberPhase02.doSubmit()

    raw_input("DONE...")
