"""Classes representing submitted jobs. These contain extra information that's
not strictly necessary to getting the jobs executed."""
#Standard
import pickle
from datetime import datetime

#Hydra
from LoggingSetup import logger
from MySQLSetup import hydra_job, hydra_rendertask, READY, transaction

#Original Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

#Note:Probably needs overhaul

class JobTicket:
    """A generic job ticket"""
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
        starts = range( self.startFrame, self.endFrame + 1, self.batchSize )
        ends = [min( start + self.batchSize - 1,
                     self.endFrame )
                for start in starts
                ]
        for start, end in zip( starts, ends ):
            command = self.renderCommand(start, end)
            logger.debug( command )
            task = hydra_rendertask( status = READY, 
                                     command = repr( command ),
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
