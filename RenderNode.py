#Standard
import os
import sys
import time
import threading
import datetime
import traceback
import subprocess
import signal

#Third Party
import psutil

#Hydra
import Constants
from Networking.Servers import TCPServer
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *
import Utilities.Utils as Utils
import Utilities.NodeUtils as NodeUtils
import Utilities.JobUtils as JobUtils
import Utilities.TaskUtils as TaskUtils

class RenderTCPServer(TCPServer):
    def __init__(self, *arglist, **kwargs):
        #Check for other instances of RenderNode running
        inst = checkRenderNodeInstances()
        if not inst:
            sys.exit(1)

        #Startup TCP Server
        self.renderServ = TCPServer.__init__(self, *arglist, **kwargs)

        #Setup Subprocess STARTUPINFO
        if sys.platform == "win32":
            self.si = subprocess.STARTUPINFO()
            self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        #Detect RedShift GPUs
        self.rsGPUs = Utils.getRedshiftPreference("SelectedCudaDevices")
        self.rsGPUs = self.rsGPUs.split(",")[:-1]
        self.rsGPUids = [x.split(":")[0] for x in self.rsGPUs]
        if len(self.rsGPUs) != len(self.rsGPUids):
            logger.warning("Problems parsing Redshift Preferences")
        logger.info("{0} Redshift Enabled GPU(s) found on this node".format(len(self.rsGPUs)))
        logger.debug("GPUs available for rendering are {0}".format(self.rsGPUs))

        #Create RenderLog Directory
        if not os.path.isdir(Constants.RENDERLOGDIR):
            os.makedirs(Constants.RENDERLOGDIR)

        #Load executeables from DB
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}
        logger.debug(self.execsDict)

        #Setup Class Variables
        self.childProcess = None
        self.statusAfterDeath = None
        self.childKilled = False
        self.thisNode = hydra_rendernode.fetch("WHERE host = %s", (Utils.myHostName(),))

        #Cleanup job if we start with it assigned to us (Like if the node crashed/restarted)
        if self.thisNode.task_id:
            logger.warning("Rouge task discovered. Unsticking...")
            TaskUtils.killTask(self.thisNode.task_id, "C", False)
            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE
            self.thisNode.task_id = None
        elif self.thisNode.status in [STARTED, PENDING]:
            logger.warning("Reseting bad status, node set {0} but no task found!".format(self.thisNode.status))
            self.thisNode.status = IDLE if self.thisNode.status == STARTED else OFFLINE

        #Update self.thisNode software_version
        self.thisNode.software_version = Constants.VERSION

        #Commit any changes we just made to self.thisNode
        with transaction() as t:
            self.thisNode.update(t)

    def shutdownCMD(self):
        self.renderServ.shutdown()

    def startRenderTask(self, renderJob, renderTask):
        self.renderThread = threading.Thread(target = self.launchRenderTask,
                                                args = (renderJob, renderTask))
        self.renderThread.start()
        return self.renderThread.isAlive()

    def launchRenderTask(self, renderJob, renderTask):
        logger.info("Starting task with id {0} on job with id {1}".format(renderTask.id, renderJob.id))
        self.childKilled = False
        self.statusAfterDeath = None
        taskFile = "\"{0}\"".format(renderJob.taskFile)
        renderList = [self.execsDict[renderJob.execName], renderJob.baseCMD,
                        "-s", str(renderTask.startFrame), "-e",
                        str(renderTask.endFrame), "-b", str(renderJob.byFrame),
                         "-rl", str(renderTask.renderLayer), taskFile]
        renderCMD = " ".join(renderList)

        logFile = os.path.join(Constants.RENDERLOGDIR, '{:0>10}.log.txt'.format(renderTask.id))
        logger.info('Starting render task {0}'.format(renderTask.id))
        log = file(logFile, 'w')
        log.write('Hydra log file {0} on {1}\n'.format(logFile, renderTask.host))
        log.write('RenderNode is {0}\n'.format(sys.argv))
        log.write('Command: {0}\n\n'.format(renderCMD))
        Utils.flushOut(log)

        try:
            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(renderCMD, stdout = log,
                                                    **Utils.buildSubprocessArgs(False))
            logger.info('Started PID {0} to do Task {1}'.format(self.childProcess.pid,
                                                                renderTask.id))
            #Wait for task to finish
            self.childProcess.communicate()

            #Record the results
            logString = "\nProcess exited with code {0} at {1} on {2}\n"
            nowTime = datetime.datetime.now().replace(microsecond = 0)
            log.write(logString.format(self.childProcess.returncode, nowTime,
                                        self.thisNode.host))

        except Exception as e:
            traceback.print_exc(e, log)
            logger.error(e)
            raise e

        #Finally, update the DB with the information from the task
        finally:
            #Get the latest info about this render node
            with transaction() as t:
                self.thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                                        (self.thisNode.host,),
                                                        explicitTransaction = t)

                renderTask.exitCode = self.childProcess.returncode
                renderTask.endTime = datetime.datetime.now()
                if self.childKilled:
                    renderTask.status = self.statusAfterDeath
                    renderTask.exitCode = 1
                    renderTask.endTime = datetime.datetime.now()
                else:
                    if renderTask.exitCode == 0:
                        status = FINISHED
                    else:
                        status = ERROR
                        renderJob.attempts += 1
                        if not renderJob.failures or renderJob.failures == "":
                            renderJob.failures = self.thisNode.host
                        else:
                            renderJob.failures += ",{0}".format(self.thisNode.host)

                    renderTask.status = status


                status = IDLE if self.thisNode.status == STARTED else OFFLINE
                self.thisNode.status = status
                logger.debug("New Node Status: {0}".format(self.thisNode.status))
                self.thisNode.task_id = None

                renderTask.update(t)
                renderJob.update(t)
                self.thisNode.update(t)

            log.close()
            self.childProcess = None
            logger.info("Done with render task {0}".format(renderTask.id))

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one."""
        self.childKilled = True
        self.statusAfterDeath = statusAfterDeath
        #Gather subprocesses just in case
        if not self.childProcess:
            logger.info("No task is running!")
            return
        children_procs = []
        if psutil.pid_exists(self.childProcess.pid):
            psutil_proc = psutil.Process(self.childProcess.pid)
            children_procs = psutil_proc.children(recursive=True)
        else:
            logger.info("PID {0} could not be found! Task is probably already dead.".format(self.childProcess.pid))
            return

        #Try to kill the main process
        try:
            logger.info("Killing main task with PID {0}".format(self.childProcess.pid))
            os.kill(self.childProcess.pid, signal.SIGTERM)
        except WindowsError as err:
            logger.error("Could not kill PID {0} due to a WindowsError".format(self.childProcess.pid))
            logger.error(str(err))
            self.childKilled = False

        #Kill the children if they still exist
        for proc in children_procs:
            if psutil.pid_exists(proc.pid):
                try:
                    logger.info("Killing subtask with PID of {0}".format(proc.pid))
                    os.kill(proc.pid, signal.SIGTERM)
                except WindowsError as err:
                    #Logging this errors as debug since it probably means they're already dead
                    logger.debug("Could not kill PID {0} due to a WindowsError".format(proc.pid))
                    logger.debug(str(err))
            else:
                logger.debug("Skipping PID {0} because it is probably already dead.".format(proc.pid))

        if any(psutil.pid_exists(proc.pid) for proc in children_procs):
            logger.error("Could not kill all render processes for some reason!")
            self.childKilled = False

def heartbeat(interval = 60):
    host = Utils.myHostName()
    while True:
        try:
            with transaction() as t:
                t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = %s",
                            (host,))
        except Exception as e:
            logger.error(traceback.format_exc(e))
        time.sleep(interval)

def checkRenderNodeInstances():
    if sys.platform == "win32":
        subprocessOutput = subprocess.check_output('tasklist', **Utils.buildSubprocessArgs(False))
        nInstances = len(filter(lambda line: 'RenderNode' in line,
                        subprocessOutput.split('\n')))
    else:
        subprocessOutput = subprocess.check_output(["ps", "-af"], **Utils.buildSubprocessArgs(False))
        nInstances = len(filter(lambda line: 'RenderNode' in line,
                        subprocessOutput.split('\n')))
    logger.debug("{0} RenderNode instances running.".format(nInstances))

    if nInstances > 2:
        logger.critical("Blocked RenderNodeMain from running because another"
                    " instance already exists.")
        return False

    elif nInstances == 0 and not sys.argv[0].endswith('.py'):
        logger.warning("Can't find running RenderNodeMain.")

    return True

def main():
    logger.debug('Starting in {0}'.format(os.getcwd()))
    logger.debug('arglist {0}'.format(sys.argv))
    socketServer = RenderTCPServer()
    pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
    pulseThread.start()

if __name__ == '__main__':
    main()
