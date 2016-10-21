#Standard
import os
import sys
import threading
import datetime
import traceback
import subprocess

#Third Party
import psutil

#Hydra
import Constants
from Networking.Servers import TCPServer
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *
from Setups.Threads import *
import Setups.LogParsers as LogParsers
from Setups.SingleInstanceLocker import InstanceLock
import Utilities.Utils as Utils

class RenderTCPServer(TCPServer):
    def __init__(self):
        #Startup TCP Server
        self.renderServ = TCPServer()

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

        #Create RenderLog Directory
        if not os.path.isdir(Constants.RENDERLOGDIR):
            os.makedirs(Constants.RENDERLOGDIR)

        #Setup Class Variables
        self.renderThread = None
        self.childProcess = None
        self.PSUtilProc = None
        self.statusAfterDeath = None
        self.childKilled = 0
        self.thisNode = hydra_rendernode.fetch("WHERE host = %s", (Utils.myHostName(),))

        #Cleanup job if we start with it assigned to us (Like if the node crashed/restarted)
        if self.thisNode.task_id:
            logger.warning("Rouge task discovered. Unsticking...")
            thisTask = hydra_taskboard.fetch("WHERE id = %s", (self.thisNode.task_id,),
                                            cols=["id", "status", "exitCode", "endTime", "host"])
            thisTask.kill("C", False)
            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE
            self.thisNode.task_id = None
        elif self.thisNode.status in [STARTED, PENDING]:
            logger.warning("Reseting bad status, node set %s but no task found!", self.thisNode.status)
            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE

        #Update self.thisNode software_version
        self.thisNode.software_version = Constants.VERSION

        #Commit any changes we just made to self.thisNode
        with transaction() as t:
            self.thisNode.update(t)

    def shutdown(self):
        self.renderServ.shutdown()

    def startRenderTask(self, HydraJob, HydraTask):
        self.renderThread = threading.Thread(target=self.launchRenderTask,
                                                args=(HydraJob, HydraTask))
        self.renderThread.start()
        return self.renderThread.isAlive()

    def launchRenderTask(self, HydraJob, HydraTask):
        logger.info("Starting task with id %s on job with id %s", HydraTask.id, HydraJob.id)
        self.childKilled = 0
        self.statusAfterDeath = None
        self.childProcess = None
        self.PSUtilProc = None

        originalCurrentFrame = int(HydraTask.currentFrame)
        renderTaskCMD = HydraTask.createTaskCMD(HydraJob, sys.platform)
        logger.debug(renderTaskCMD)

        logFile = HydraTask.getLogPath()
        logger.info("Starting render task %s", HydraTask.id)
        try:
            log = file(logFile, 'w')
        except (IOError, OSError, WindowsError) as e:
            logger.error(e)
            self.thisNode.getOff()
            return
        log.write('Hydra log file {0} on {1}\n'.format(logFile, HydraTask.host))
        log.write('RenderNode is {0}\n'.format(sys.argv))
        log.write('Command: {0}\n\n'.format(renderTaskCMD))
        Utils.flushOut(log)

        try:
            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(renderTaskCMD,
                                                stdout=log, stderr=log,
                                                **Utils.buildSubprocessArgs(False))

            logger.info("Started PID %s to do Task %s", self.childProcess.pid, HydraTask.id)

            self.PSUtilProc = psutil.Process(self.childProcess.pid)
            #Wait for task to finish
            self.childProcess.communicate()

            #Record the results
            logString = "\nProcess exited with code {0} at {1} on {2}\n"
            nowTime = datetime.datetime.now().replace(microsecond=0)
            log.write(logString.format(self.childProcess.returncode, nowTime,
                                        self.thisNode.host))

        except Exception as e:
            traceback.print_exc(e, log)
            logger.error(e)
            raise e

        #Finally, update the DB with the information from the task
        finally:
            HydraLogObject = LogParsers.getLog(HydraJob, logFile)
            renderedFrames = HydraLogObject.getSavedFrameNumbers()

            if not renderedFrames:
                renderedFrames = [-1]

            logger.debug(renderedFrames)
            newCurrentFrame = max(renderedFrames)
            logger.debug(newCurrentFrame)

            with transaction() as t:
                self.thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                                        (self.thisNode.host,),
                                                        explicitTransaction=t)

                HydraTask.endTime = datetime.datetime.now()
                HydraTask.exitCode = self.childProcess.returncode if self.childProcess else 1

                HydraTask.currentFrame = newCurrentFrame
                rls = HydraJob.renderLayers.split(",")
                idx = rls.index(HydraTask.renderLayer)
                rlTracker = HydraJob.renderLayerTracker.split(",")
                rlTracker[idx] = str(newCurrentFrame)
                HydraJob.renderLayerTracker = ",".join(rlTracker)

                if self.childKilled == 1:
                    HydraTask.status = self.statusAfterDeath
                    HydraTask.exitCode = 1
                else:
                    if HydraTask.exitCode == 0 and newCurrentFrame >= originalCurrentFrame:
                        status = FINISHED
                    else:
                        if HydraTask.exitCode == 0:
                            log.write("\n\nERROR: Task returned exit code 0 but it appears to have not actually rendered any frames.")
                        status = ERROR
                        HydraJob.attempts += 1
                        if not HydraJob.failures or HydraJob.failures == "":
                            HydraJob.failures = self.thisNode.host
                        else:
                            HydraJob.failures += ",{0}".format(self.thisNode.host)

                    HydraTask.status = status


                status = IDLE if self.thisNode.status == STARTED else OFFLINE
                self.thisNode.status = status
                logger.debug("New Node Status: %s", self.thisNode.status)
                self.thisNode.task_id = None

                HydraTask.update(t)
                HydraJob.update(t)
                self.thisNode.update(t)

            log.close()
            self.childProcess = None
            self.PSUtilProc = None
            logger.info("Done with render task %s", HydraTask.id)

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one.
        Return Codes: 1 = process killed, -1 = parent could not be killed,
        -9 = child could not be killed, -10 = child and parent could not be killed"""
        self.statusAfterDeath = statusAfterDeath
        self.childKilled = 1
        if not self.childProcess or self.PSUtilProc:
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
        [proc.terminate() for proc in childrenProcs if proc.is_running()]
        _, alive = psutil.wait_procs(childrenProcs, timeout=15)
        if len(alive) > 0:
            [proc.kill() for proc in alive]
            _, alive = psutil.wait_procs(alive, timeout=15)

        if len(alive) > 0:
            #ADD negative 10 to the return code
            self.childKilled += -10

def heartbeat():
    host = Utils.myHostName()
    with transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = %s",
                    (host,))

def softwareUpdaterLoop():
    logger.debug("Checking for updates...")
    updateAnswer = Utils.softwareUpdater()
    if updateAnswer:
        logger.debug("Update found!")
        socketServer.shutdown()
        pulseThread.terminate()
        Utils.launchHydraApp("RenderNodeConsole")
        updaterThread.terminate()
        sys.exit(0)
    else:
        logger.debug("No updates found.")

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
    pulseThread = stoppableThread(heartbeat, 60, "Pulse_Thread")
    #If this is an exe, start the software updater thread
    if sys.argv[0].endswith(".exe") and os.getenv("HYDRA"):
        updaterThread = stoppableThread(softwareUpdaterLoop, 900, "Updater_Thread")
