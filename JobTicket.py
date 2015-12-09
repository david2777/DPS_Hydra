#Standard
from datetime import datetime

#Hydra
from LoggingSetup import logger
from MySQLSetup import hydra_jobboard, hydra_taskboard, transaction

"""
Contains a class with functions for submitting a job to the DB.
Also has a main function for generating test data. 
"""

class UberJobTicket:
    """A Ticket Class for submitting jobs and their subtasks."""
    def __init__(self, baseCMD, startFrame, endFrame, byFrame, taskFile, priority,
                phase, jobStatus, niceName, owner, compatabilityPattern):
        #Let's verify the data we just got from the user
        if len(baseCMD) > 255:
            raise Exception("baseCMD too long! baseCMD must be less than 255 characters!")
        if startFrame > endFrame:
            raise Exception("startFrame is greater than endFrame!")
        if 0 < startFrame > 65535 or 0 < endFrame > 65535:
            raise Exception("Frame range out of range! Start/End frames must be between 0 and 65535!")
        if 0 < byFrame > 255:
            raise Exception("byFrame out of range! byFrame must be between 0 and 255!")
        if len(taskFile) > 255:
            raise Exception("taskFile out of range! taskFile path must be less than 255 characters!")
        if 0 < priority > 255:
            raise Exception("Priority out of range! Priority must be between 0 and 255!") 
        if 0 < phase > 255:
            raise Exception("Phase out of range! Phase must be between 0 and 255!")
        if len(jobStatus) > 1:
            raise Exception("jobStatus out of range! jobStatus must only be one character!")
        if len(niceName) > 60:
            raise Exception("NiceName out of range! NiceName must be less than 60 characters!")
        if len(owner) > 45:
            raise Exception("Owner out of range! Owner must be less than 45 characters!")
        if len(compatabilityPattern) > 255:
            raise Exception("compatabilityPattern out of range! compatabilityPattern must be less than 255 characters!")
        
        #Looks good, let's setup our class variables
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
        self.compatabilityPattern = compatabilityPattern    #VARCHAR(255)
        self.createTime = datetime.now()
        
    def commandBuilder(self, startFrame, endFrame):
        """Returns a command as a list for sending to subprocess.call on RenderNode"""
        #Using -mr:v 5 to get a more verbose log, render should still use correct engine
        return [self.baseCMD, '-mr:v', '5', '-s', str(startFrame), '-e', str(endFrame), self.taskFile]    
    
    def createJob(self):
        """Function for building and inserting a job.
        Returns the job so we can use the ID for the tasks""" 
        job = hydra_jobboard(baseCMD = self.baseCMD,
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
                            requirements = self.compatabilityPattern)
                            
        with transaction() as t:
            job.insert(transaction=t)
            
        return job
        
    def createTasks(self):
        """Function for creating and inserting tasks for a range of frames."""
        frameRange = range(self.startFrame, self.endFrame)
        frameList = frameRange[0::self.byFrame]
        if self.endFrame not in frameList:
            frameList.append(self.endFrame)
        for frame in frameList:
            command = self.commandBuilder(frame, frame)
            logger.debug(command)
            task = hydra_taskboard(command = repr(command),
                                  job_id = self.job_id,
                                  status = self.jobStatus,
                                  priority = self.priority,
                                  createTime = self.createTime,
                                  requirements = self.compatabilityPattern,
                                  frame = frame)
            
            with transaction() as t:
                task.insert(transaction=t)
                  
    def doSubmit(self):
        """The actual function to submit the job and tasks to the DB"""
        job = self.createJob()
        self.job_id = job.id
        self.createTasks()
        logger.info("Submitted UberTicket job with id %d" % self.job_id)
        
    def createCMDTicketTask(self):
        """Command for making a task for a CMD Ticket.
        
        Not sure why you'd ever need a CMD Ticket but it was in the original
        Hydra so I figured I'd include it in the new UberTicket
        
        ***UNTESTED***"""
        command = [self.baseCMD]
        logger.debug(command)
        task = hydra_taskboard(command = repr(command),
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
        logger.info("Submitted UberTicket CMDTicket job with id %d" % self.job_id)

            
if __name__ == "__main__":
    prompt = raw_input("Create test Job? ").lower()
    if prompt == "yes" or prompt == "y":
        baseCMD = r"$Maya/bin/render.exe -proj \\test\test"
        mayaFile = r"\\test\test\test.ma"
        startFrame = 101
        endFrame = 110
        priority = 55
        jobStatus = "U"
        niceName = "TEST JOB"
        owner = "dduvoisin"
        compatabilityPattern = "Redshift, Maya2015, SOUP"
        
        uberPhase01 = UberJobTicket(baseCMD, startFrame, endFrame, 1, mayaFile,
        priority, 1, jobStatus, niceName + "_PHASE_02", owner, compatabilityPattern)
        uberPhase01.doSubmit()
        
    raw_input("DONE...")
