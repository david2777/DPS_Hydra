"""Classes representing submitted jobs. These contain extra information that's
not strictly necessary to getting the jobs executed."""
#Standard
import pickle
from datetime import datetime

#Hydra
from LoggingSetup import logger
from MySQLSetup import hydra_job, hydra_jobboard, hydra_taskboard, hydra_rendertask, READY, transaction

#Original Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

#Note:Probably needs overhaul

class UberJobTicket:
    """
    A new Ticket Class for creating jobs and tasks
    """
    def __init__(self, baseCMD, startFrame, endFrame, byFrame, taskFile, priority,
                phase, jobStatus, niceName, owner, compatabilityPattern):
        #Verify data input here! Raise errors before they hit the DB!
        self.baseCMD = baseCMD          #VARCHAR(255)
        self.startFrame = startFrame    #SMALLINT   ie.(0-65535)
        self.endFrame = endFrame        #SMALLINT   ie.(0-65535)
        self.byFrame = byFrame          #TINYINT   ie.(0-255)
        self.taskFile = taskFile        #VARCHAR(60)
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
        frameRange = range(self.startFrame, self.endFrame)
        frameList = frameRange[0::self.byFrame]
        if self.endFrame not in frameList:
            frameList.append(self.endFrame)
        for task in frameList:
            command = self.commandBuilder(task, task)
            logger.debug(command)
            task = hydra_taskboard(command = repr(command),
                                  job_id = self.job_id,
                                  task_status = self.jobStatus,
                                  priority = self.priority,
                                  createTime = self.createTime,
                                  requirements = self.compatabilityPattern
                                  )
            
            with transaction() as t:
                task.insert(transaction=t)
                  
    def doSubmit(self):
        job = self.createJob()
        self.job_id = job.job_id
        self.createTasks()
        logger.info("Submitted!")
            

class JobTicket:
    """
    *****DEPRECATED****** 
    A generic job ticket
    """
    def __init__(self, priority, owner, niceName, capability_pattern):
        self.priority = priority
        self.capability_pattern = capability_pattern
        self.owner = owner
        self.niceName = niceName
    
    def submit( self ):
        job = self.createJob()
        self.createTasks(job)

    def createJob( self ):
        job = hydra_job( pickledTicket = pickle.dumps(self), 
                         priority = self.priority, 
                         requirements = self.capability_pattern,
                         createTime = datetime.now(),
                         owner = self.owner,
                         niceName = self.niceName)
        
        with transaction() as t:
            job.insert(transaction=t)
            
        return job

    def createTasks(self, job):
        raise NotImplemented

    def name (self):
        return 'unnamed generic'

class MayaTicket(JobTicket):
    """
    *****DEPRECATED****** 
    """
    def __init__( self, sceneFile, mayaProjectPath, startFrame, endFrame, 
                  batchSize, priority, owner, niceName, capability_pattern):
        print ('initializing', self)
        JobTicket.__init__(self, priority, owner, niceName, capability_pattern)
        self.sceneFile = sceneFile
        self.mayaProjectPath = mayaProjectPath
        self.startFrame = startFrame
        self.endFrame = endFrame
        self.batchSize = batchSize

    def name (self):
        return self.sceneFile

    def renderCommand(self, start, end):
        return [self.executable,
                '-mr:v', '5',
                '-s', str( start ),
                '-e', str( end ),
                '-proj', self.mayaProjectPath,
                self.sceneFile
                ]

    def createTasks( self, job ):
        starts = range( self.startFrame, self.endFrame + 1, self.batchSize)
        ends = [min( start + self.batchSize - 1,
                     self.endFrame )
                for start in starts
                ]
        for start, end in zip( starts, ends ):
            command = self.renderCommand(start, end)
            logger.debug( command )
            task = hydra_rendertask( status = READY, 
                                     command = repr(command),
                                     job_id = job.id, 
                                     priority = self.priority, 
                                     createTime = job.createTime,
                                     requirements = job.requirements,
                                     )
            with transaction() as t:
                task.insert(transaction=t)

# these classes are selected by the submitter GUI
class Maya2011 (MayaTicket):
    executable = r'c:\program files\autodesk\maya2011\bin\render.exe'

class Maya2013 (MayaTicket):
    executable = r'c:\program files\autodesk\maya2013\bin\render.exe'

class Maya2014 (MayaTicket):
    executable = r'c:\program files\autodesk\maya2014\bin\render.exe'

class CMDTicket(JobTicket):
    """A job ticket for shoehorning arbitrary commands into the task list. You 
    know, just in case you wanted to do something like that."""
    
    def __init__(self, cmd):
        self.command = cmd
        self.priority = 50

    def name (self):
        return str (self.command)
        
    def createTasks(self, job):
        task = hydra_rendertask( status = READY,
                                 command = repr( self.command ),
                                 job_id = job.id, 
                                 priority = self.priority,
                                 createTime = job.createTime)
        with transaction() as t:
            task.insert(transaction=t)
            
if __name__ == "__main__":
    prompt = raw_input("Create test Job? ").lower()
    if prompt == "yes" or prompt == "y":
        baseCMD = r"$Maya/bin/render.exe -proj \\test\test"
        mayaFile = r"\\test\test\test.ma"
        startFrame = 101
        endFrame = 175
        priority = 55
        jobStatus = "U"
        niceName = "TEST JOB"
        owner = "dduvoisin"
        compatabilityPattern = ""
        
        uberPhase01 = UberJobTicket(baseCMD, startFrame, endFrame, 10, mayaFile,
        priority, "1", jobStatus, niceName + "_PHASE_01", owner, compatabilityPattern)
        uberPhase01.doSubmit()
        
    raw_input("DONE...")
