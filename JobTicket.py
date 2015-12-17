#Standard
from datetime import datetime

#Hydra
from LoggingSetup import logger
from MySQLSetup import hydra_jobboard, hydra_taskboard, transaction
from Constants import EXECUTEABLES

"""
Contains a class with functions for submitting a job to the DB.
Also has a main function for generating test data. 
"""

class UberJobTicket:
    """A Ticket Class for submitting jobs and their subtasks."""
    def __init__(self, execName, baseCMD, startFrame, endFrame, byFrame, taskFile, priority,
                phase, jobStatus, niceName, owner, compatabilityList):
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
        
        #Check this after we run it through the builder function
        if len(self.compatabilityPattern) > 255:
            raise Exception("compatabilityPattern out of range! Must be less than 255 characters after conversion!")
        
    def commandBuilder(self, startFrame, endFrame):
        """Returns a command as a list for sending to subprocess.call on RenderNode"""
        #Using -mr:v 5 to get a more verbose log, render should still use correct engine
        return " ".join([EXECUTEABLES[self.execName], self.baseCMD, '-mr:v', '5', '-s',
                str(startFrame), '-e', str(endFrame), self.taskFile])
                
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
            task = hydra_taskboard(command = command,
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
        logger.info("Submitted UberTicket CMDTicket job with id %d" % self.job_id)

            
if __name__ == "__main__":
    prompt = raw_input("Create test Job? ").lower()
    if prompt == "yes" or prompt == "y":
        baseCMD = r"-proj F:/Projects/Fruits"
        mayaFile = r"F:/Projects/Fruits/scenes/orangeSliceTest.ma"
        startFrame = 101
        endFrame = 115
        priority = 50
        niceName = "orangeSliceTest"
        owner = "dduvoisin"
        compatabilityList = ["SOUP", "Maya2015", "Substance"]
        
        uberPhase01 = UberJobTicket("maya2014Render", baseCMD, startFrame, endFrame, 10, mayaFile,
        priority, 1, "R", niceName + "_PHASE_01", owner, compatabilityList)
        uberPhase01.doSubmit()
        
        #uberPhase02 = UberJobTicket("maya2014Render", baseCMD, proj, startFrame, endFrame, 1, mayaFile,
        #priority, 2, "U", niceName + "_PHASE_02", owner, compatabilityList)
        #uberPhase02.doSubmit()
        
    raw_input("DONE...")
