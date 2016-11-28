#Standard
import os
import sys
import threading
import datetime
import subprocess

#Third Party
import psutil

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
import Setups.LogParsers as LogParsers
from Setups.SingleInstanceLocker import InstanceLock
from Setups.Threads import stoppableThread
import Constants
from Networking.Servers import TCPServer
import Utilities.Utils as Utils
from Utilities.NodeUtils import getThisNodeOBJ

class RenderTCPServer(TCPServer):
    """RenderTCPServer waits for a TCP connection from the RenderManagerServer
    telling it to start a render task. The render task is processed and the results
    updated in the databse."""
    def __init__(self):
        #Setup Class Variables
        self.renderThread = None
        self.childProcess = None
        self.PSUtilProc = None
        self.statusAfterDeath = None
        self.childKilled = 0
        self.HydraJob = None
        self.HydraTask = None
        self.logPath = None

        #Get this node data from the database and make sure it exists
        self.thisNode = getThisNodeOBJ()
        logger.debug(self.thisNode)
        if not self.thisNode:
            logger.critical("This node does not exist in the database! Please Register this node and try again.")
            sys.exit(-1)
            return

        #Detect RedShift GPUs
        self.rsGPUs = Utils.getRedshiftPreference("SelectedCudaDevices")
        if self.rsGPUs:
            self.rsGPUs = self.rsGPUs.split(",")[:-1]
            self.rsGPUids = [x.split(":")[0] for x in self.rsGPUs]
            if len(self.rsGPUs) != len(self.rsGPUids):
                logger.warning("Problems parsing Redshift Preferences")
            logger.info("%s Redshift Enabled GPU(s) found on this node", len(self.rsGPUs))
            logger.debug("GPUs available for rendering are %s", self.rsGPUs)
        else:
            logger.warning("Could not find available Redshift GPUs")

        #Create RenderLog Directory if it doesn't exit
        if not os.path.isdir(Constants.RENDERLOGDIR):
            os.makedirs(Constants.RENDERLOGDIR)

        self.unstickTask()
        self.thisNode.software_version = Constants.VERSION

        with transaction() as t:
            self.thisNode.update(t)

        #Run The Server
        port = int(Utils.getInfoFromCFG("network", "port"))
        self.startServerThread(port)

    @staticmethod
    def getNewRLTracker(HydraJob, HydraTask):
        """Makes a new RenderLayer tracker for the RenderJob"""
        rls = HydraJob.renderLayers.split(",")
        idx = rls.index(HydraTask.renderLayer)
        rlTracker = HydraJob.renderLayerTracker.split(",")
        rlTracker[idx] = str(HydraTask.currentFrame)
        return ",".join(rlTracker)

    def unstickTask(self):
        """Cleanup task if the node starts with one assigned to it
        (Like if the node crashed/restarted)"""
        #self.thisNode will be updated in in init statement
        if self.thisNode.task_id:
            logger.info("Rouge task discovered. Unsticking...")

            self.HydraTask = hydra_taskboard.fetch("WHERE id = %s", (self.thisNode.task_id,),
                                            cols=["id", "job_id", "renderLayer",
                                                    "status", "exitCode",
                                                    "endTime", "host",
                                                    "currentFrame"],
                                            multiReturn=False)

            self.HydraJob = hydra_jobboard.fetch("WHERE id = %s", (self.HydraTask.job_id,),
                                            cols=["jobType", "renderLayerTracker"],
                                            multiReturn=False)

            self.HydraTask.kill(CRASHED, False)

            self.progressUpdate()

            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE
            self.thisNode.task_id = None

        elif self.thisNode.status in [STARTED, PENDING]:
            logger.warning("Reseting bad status, node set %s but no task found!", self.thisNode.status)
            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE

    def shutdown(self):
        """Offline node, Kill current job, shutdown servers, reset node status"""
        currentStatus = self.thisNode.status
        self.thisNode.offline()
        if currentStatus in [STARTED, PENDING]:
            logger.info("Attempting to kill current job.")
            self.killCurrentJob(KILLED)
            logger.info("Kill Response Code: %s", self.childKilled)
        TCPServer.shutdown(self)
        #Online AFTER servers are shutdown
        if currentStatus == STARTED:
            self.thisNode.online()
        logger.info("RenderNode Servers Shutdown")

    def startRenderTask(self, HydraJob, HydraTask):
        """Command sent to the RenderTCPServer, starts the render task in a new
        thread to prevent thread locking during the render."""
        self.renderThread = threading.Thread(target=self.launchRenderTask,
                                                args=(HydraJob, HydraTask))
        self.renderThread.start()
        return self.renderThread.isAlive()

    def launchRenderTask(self, HydraJob, HydraTask):
        """Does the actual rendering, then records the results on the database"""
        logger.info("Starting task with id %s on job with id %s", HydraTask.id, HydraJob.id)
        self.HydraJob = HydraJob
        self.HydraTask = HydraTask
        self.childKilled = 0
        self.statusAfterDeath = None
        self.childProcess = None
        self.PSUtilProc = None

        originalCurrentFrame = int(self.HydraTask.currentFrame)
        renderTaskCMD = self.HydraTask.createTaskCMD(self.HydraJob, sys.platform)
        logger.debug(renderTaskCMD)

        self.logPath = self.HydraTask.getLogPath()
        logger.info("Starting render task %s", self.HydraTask.id)
        try:
            log = file(self.logPath, 'w')
        except (IOError, OSError, WindowsError) as e:
            logger.error(e)
            self.thisNode.getOff()
            return
        log.write('Hydra log file {0} on {1}\n'.format(self.logPath, self.HydraTask.host))
        log.write('RenderNode is {0}\n'.format(sys.argv))
        log.write('Command: {0}\n\n'.format(renderTaskCMD))
        Utils.flushOut(log)

        progressUpdateThread = stoppableThread(self.progressUpdate, 300,
                                                "Progress_Update_Thread")

        #Run the job and keep track of the process
        self.childProcess = subprocess.Popen(renderTaskCMD,
                                            stdout=log, stderr=log,
                                            **Utils.buildSubprocessArgs(False))

        logger.info("Started PID %s to do Task %s", self.childProcess.pid, self.HydraTask.id)

        self.PSUtilProc = psutil.Process(self.childProcess.pid)
        #Wait for task to finish
        self.childProcess.communicate()

        #Record the results
        logString = "\nProcess exited with code {0} at {1} on {2}\n"
        nowTime = datetime.datetime.now().replace(microsecond=0)
        log.write(logString.format(self.childProcess.returncode, nowTime,
                                    self.thisNode.host))

        progressUpdateThread.terminate()

        #Update HydraTask and HydraJob with currentFrame, MPF, and RLTracker
        self.progressUpdate(commit=False)

        #EndTime, ExitCode
        self.HydraTask.endTime = datetime.datetime.now()
        self.HydraTask.exitCode = self.childProcess.returncode if self.childProcess else 1

        #Status, Attempts. Failures
        if self.childKilled == 1:
            self.HydraTask.status = self.statusAfterDeath
            self.HydraTask.exitCode = 1

        else:
            if self.HydraTask.exitCode == 0 and self.HydraTask.currentFrame >= originalCurrentFrame:
                status = FINISHED
            else:
                if self.HydraTask.exitCode == 0:
                    log.write("\n\nERROR: Task returned exit code 0 but it appears to have not actually rendered any frames.")
                status = ERROR
                self.HydraJob.attempts += 1
                if not self.HydraJob.failures or self.HydraJob.failures == "":
                    self.HydraJob.failures = self.thisNode.host
                else:
                    self.HydraJob.failures += ",{0}".format(self.thisNode.host)

            self.HydraTask.status = status

        #Update data on the DB
        with transaction() as t:
            self.HydraTask.update(t)
            self.HydraJob.update(t)

        self.resetThisNode()
        log.close()
        logger.info("Done with render task %s", self.HydraTask.id)
        self.childProcess = None
        self.PSUtilProc = None
        self.HydraJob = None
        self.HydraTask = None
        self.logPath = None

    def progressUpdate(self, commit=True):
        """Parse the render log file and update the databse with the currently
        rendering frame, MPF (minutes per frame) and the renderLayerTracker.
        Optional commit can stop the data from being updated on the databse if
        set to False."""
        if not all([self.childProcess, self.HydraTask,
                    self.HydraJob, self.logPath]):
            logger.debug("Could not update progress")
            return

        #Get Log Parser and find the highest rendered frame
        HydraLogObject = LogParsers.getLog(self.HydraJob, self.logPath)
        newCurrentFrame = HydraLogObject.getNewCurrentFrame()
        if not newCurrentFrame:
            newCurrentFrame = self.HydraTask.currentFrame
        else:
            #If we have a valid new currentFrame add one since it's now on the next frame
            newCurrentFrame += 1

        mpf = HydraLogObject.getAverageRenderTime()

        #currentFrame, renderLayerTracker
        self.HydraTask.currentFrame = newCurrentFrame
        self.HydraJob.renderLayerTracker = self.getNewRLTracker(self.HydraJob,
                                                            self.HydraTask)
        #MintuesPerFrame
        if mpf:
            self.HydraTask.mpf = mpf
            if self.HydraJob.mpf:
                tSecs = int((self.HydraJob.mpf.total_seconds() + mpf.total_seconds()) / 2)
                self.HydraJob.mpf = datetime.timedelta(seconds=tSecs)
            else:
                self.HydraJob.mpf = mpf

        if commit:
            with transaction() as t:
                self.HydraJob.update(t)
                self.HydraTask.update(t)

    def resetThisNode(self):
        """Resets node after render, sets current task to None and updates
        node status."""
        with transaction() as t:
            self.thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                                    (self.thisNode.host,),
                                                    explicitTransaction=t)
            status = IDLE if self.thisNode.status == STARTED else OFFLINE
            self.thisNode.status = status
            logger.debug("New Node Status: %s", self.thisNode.status)
            self.thisNode.task_id = None
            self.thisNode.update(t)

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one.
        Return Codes: 1 = process killed, -1 = parent could not be killed,
        -9 = child could not be killed, -10 = child and parent could not be killed"""
        self.statusAfterDeath = statusAfterDeath
        self.childKilled = 1
        if not self.childProcess or not self.PSUtilProc:
            logger.info("No task is running!")
            return

        #Gather subprocesses just in case
        if self.PSUtilProc.is_running():
            childrenProcs = self.PSUtilProc.children(recursive=True)
        else:
            logger.info("PID '%s' could not be found! Task is probably already dead.", self.childProcess.pid)
            return

        #Try to kill the main process
        #terminate() = SIGTERM, kill() = SIGKILL
        logger.info("Killing main task with PID %s", self.PSUtilProc.pid)
        self.PSUtilProc.terminate()
        _, alive = psutil.wait_procs([self.PSUtilProc], timeout=15)
        if len(alive) > 0:
            self.PSUtilProc.kill()
            _, alive = psutil.wait_procs([self.PSUtilProc], timeout=15)
            if len(alive) > 0:
                logger.error("Could not kill PID %s", self.PSUtilProc.pid)
                self.childKilled = -1

        #Try to kill the children if they are still running
        _ = [proc.terminate() for proc in childrenProcs if proc.is_running()]
        _, alive = psutil.wait_procs(childrenProcs, timeout=15)
        if len(alive) > 0:
            _ = [proc.kill() for proc in alive]
            _, alive = psutil.wait_procs(alive, timeout=15)

        if len(alive) > 0:
            #ADD negative 10 to the return code
            self.childKilled += -10

def heartbeat():
    """Updates a column on the node's database with the current time, signifying
    that the node software is still running."""
    host = Utils.myHostName()
    with transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = %s",
                    (host,))

def softwareUpdaterLoop():
    """Checks for a new verison in the HYDRA environ, if one is found it starts
    a batch process to start the new verison and kills the current one running."""
    logger.debug("Checking for updates...")
    updateAnswer = Utils.softwareUpdater()
    if updateAnswer:
        logger.debug("Update found!")
        Utils.launchHydraApp("RenderNodeConsole", 10)
        socketServer.shutdown()
        sys.exit(0)
    else:
        logger.debug("No updates found")

if __name__ == "__main__":
    logger.info("Starting in %s", os.getcwd())
    logger.info("arglist %s", sys.argv)

    #Check for other RenderNode isntances
    lockFile = InstanceLock("HydraRenderNode")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderNode is allowed to run at a time! Exiting...")
        sys.exit(-1)

    #Start the Render Server and Heartbeat Thread
    socketServer = RenderTCPServer()
    socketServer.createIdleLoop("Pulse_Thread", heartbeat, 60)
    #If this is an exe, start the software updater thread
    if sys.argv[0].endswith(".exe") and os.getenv("HYDRA"):
        socketServer.createIdleLoop("Software_Updater_Thread", softwareUpdaterLoop, 900)
