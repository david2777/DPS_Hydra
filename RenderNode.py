#Standard
import os
import sys
import threading
import datetime
import subprocess
import traceback

#Third Party
import psutil

#Hydra
from hydra.mysql_setup import *
from hydra.logging_setup import logger
from hydra.single_instance import InstanceLock
import constants
from networking.servers import TCPServer
import utils.hydra_utils as hydra_utils
from utils.node_utils import getThisNodeOBJ

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

        #Get this node data from the database and make sure it exists
        self.thisNode = getThisNodeOBJ()
        logger.debug(self.thisNode)
        if not self.thisNode:
            logger.critical("This node does not exist in the database! Please Register this node and try again.")
            sys.exit(-1)
            return

        #Create RenderLog Directory if it doesn't exit
        if not os.path.isdir(constants.RENDERLOGDIR):
            os.makedirs(constants.RENDERLOGDIR)

        self.unstickTask()

        #Run The Server
        port = int(hydra_utils.getInfoFromCFG("network", "port"))
        self.startServerThread(port)

    def unstickTask(self, statusAfterDeath=CRASHED):
        """Cleanup task if the node starts with one assigned to it
        (Like if the node crashed/restarted)"""
        pass

    def shutdown(self):
        """Offline node, Kill current job, shutdown servers, reset node status"""
        #TODO OFFLINE NODE
        currentStatus = None
        if currentStatus in [STARTED, PENDING] or self.childProcess:
            logger.info("Attempting to kill current job.")
            self.killCurrentJob(KILLED)
            logger.info("Kill Response Code: %s", self.childKilled)
        TCPServer.shutdown(self)
        #TODO ONLINE NODE
        logger.info("RenderNode servers Shutdown")

    def startRenderTask(self, renderCommand, logPath, task_id, job_id):
        """Command sent to the RenderTCPServer, starts the render task in a new
        thread to prevent thread locking during the render."""
        self.renderThread = threading.Thread(target=self.launchRenderTask,
                                                args=(renderCommand, logPath,
                                                        task_id, job_id))
        self.renderThread.start()
        return self.renderThread.isAlive()

    def launchRenderTask(self, renderTaskCMD, logPath, task_id, job_id):
        """Does the actual rendering, then records the results on the database"""
        logger.info("Starting task with id %s on job with id %s", task_id, job_id)
        self.childKilled = 0
        self.statusAfterDeath = None
        self.childProcess = None
        self.PSUtilProc = None

        logger.debug(renderTaskCMD)

        logger.info("Starting render task %s", self.HydraTask.id)
        try:
            log = file(logPath, 'w')
        except (IOError, OSError, WindowsError) as e:
            logger.error(e)
            #TODO OFFLINE THIS NODE
            return
        log.write('Hydra log file {0} on {1}\n'.format(logPath, self.thisNode.host))
        log.write('RenderNode is {0}\n'.format(sys.argv))
        log.write('Command: {0}\n\n'.format(renderTaskCMD))
        hydra_utils.flushOut(log)

        try:
            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(renderTaskCMD,
                                                stdout=log, stderr=log,
                                                **hydra_utils.buildSubprocessArgs(False))

            logger.info("Started PID %s to do Task %s", self.childProcess.pid, task_id)

            self.PSUtilProc = psutil.Process(self.childProcess.pid)
            #Wait for task to finish
            self.childProcess.communicate()
        #pylint: disable=W0702
        except:
            #Cleanup a crash
            e = traceback.format_exc()
            logger.critical(e)
            log.write("\n\n-----------Job crashed on startup!-----------\n")
            log.write(e)
            log.close()
            #unstickTask will update all info on the DB and cleanup variables
            self.unstickTask(ERROR)
            return

        #If it gets this far then the subprocess has exited for one reason or another
        #Get Exit Code, Record the results
        exitCode = self.childProcess.returncode if self.childProcess else 1234
        logString = "\nProcess exited with code {0} at {1} on {2}\n"
        nowTime = datetime.datetime.now().replace(microsecond=0)
        log.write(logString.format(exitCode, nowTime, self.thisNode.host))

        #TODO Update info DB

        log.close()
        logger.info("Done with render task %s", self.HydraTask.id)
        self.childProcess = None
        self.PSUtilProc = None
        logPath = None

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
    #TODO Make this do the thing
    pass

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
