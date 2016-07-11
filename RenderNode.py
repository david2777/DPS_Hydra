"""The functions that accept, process, and render tasks. It checks the Database
every x seconds for a new task using the query to determine if the task is
something it wants to run. If it gets a task it updates the DB and renders the
task. When it finishes it updates the task again on the DB and start looking for
a new task. This can be run as a standalone software or a win32service using
RenderNodeService."""
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
import Utilities.JobUtils as JobUtils
import Utilities.TaskUtils as TaskUtils

class RenderTCPServer(TCPServer):
    def __init__(self, *arglist, **kwargs):
        inst = checkRenderNodeInstances()
        if not inst:
            sys.exit(1)

        self.renderServ = TCPServer.__init__(self, *arglist, **kwargs)
        if sys.platform == "win32":
            self.si = subprocess.STARTUPINFO()
            self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.rsGPUs = Utils.getRedshiftPreference("SelectedCudaDevices")
        self.rsGPUs = self.rsGPUs.split(",")[:-1]
        self.rsGPUids = [x.split(":")[0] for x in self.rsGPUs]
        if len(self.rsGPUs) != len(self.rsGPUids):
            logger.warning("Problems parsing RS Preferences")
            logger.info("{0} Redshift Enabled GPU(s) found on this node".format(len(self.rsGPUs)))
            logger.debug("GPUs available for rendering are {0}".format(self.rsGPUs))

        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        self.childProcess = None
        self.childKilled = False
        self.statusAfterDeath = None
        self.thisNodeName = Utils.myHostName()

        #Cleanup job if we start with it assigned to us (Like if the node crashed/restarted)
        thisNode = hydra_rendernode.fetch("WHERE host = %s", (self.thisNodeName,))
        query = "UPDATE hydra_rendernode SET status = %s WHERE host = %s"
        if thisNode.task_id:
            logger.warning("Rouge task discovered. Unsticking...")
            task = hydra_taskboard.fetch("WHERE id = %s", (thisNode.task_id,))
            newStatus = OFFLINE if thisNode.status in [OFFLINE, PENDING] else ONLINE
            TaskUtils.unstickTask(taskID = thisNode.task_id, newTaskStatus = CRASHED,
                              host = thisNode.host, newHostStatus = newStatus)
            JobUtils.manageNodeLimit(task.job_id)
        elif thisNode.status in [STARTED, PENDING] and not thisNode.task_id:
            logger.warning("Reseting bad status, node set {0} but no task found!".format(thisNode.status))
            newStatus = READY if thisNode.status == STARTED else OFFLINE
            with transaction() as t:
                t.cur.execute(query, (newStatus, self.thisNodeName,))

        #Update current software version on the DB if necessary
        current_version = sys.argv[0]
        if thisNode.software_version != current_version:
            thisNode.software_version = current_version
            with transaction() as t:
                thisNode.update(t)

    def shutdownCMD(self):
        self.renderServ.shutdown()

    def processRenderTasks(self):
        """The loop that looks for jobs on the DB and runs them if the node meets
        the job's requirements"""
        thisNode = hydra_rendernode.fetch("WHERE host = %s",(self.thisNodeName,))
        debugStr = "Host: {0} Status: {1} Capabilities: {2}"
        logger.debug(debugStr.format(thisNode.host, niceNames[thisNode.status],
                                    thisNode.capabilities))

        #If this node is not idle, don't try to find a new job
        if thisNode.status != IDLE:
            return

        #Otherwise, get a job that's:
        #-Ready to be run and
        #-Has a high enough priority level for this particular node and
        #-Is able to meet to jobs required capabilities
        whereClause = "WHERE status = %s AND priority >= %s AND %s LIKE requirements AND archived = 0 AND failures NOT LIKE '%%{0}%%'".format(thisNode.host)
        whereTuple = (READY, thisNode.minPriority, thisNode.capabilities)
        orderTuples = (("priority", "DESC"), ("id", "ASC"))

        with transaction() as t:
            render_task = hydra_taskboard.fetch(whereClause = whereClause,
                                                        whereTuple = whereTuple,
                                                        orderTuples = orderTuples,
                                                        limit = 1,
                                                        explicitTransaction = t)
            #If not task is found, stop and wait to search again
            if not render_task:
                return

            #Otherwise, render the task
            render_job = hydra_jobboard.fetch("WHERE id = %s",
                                                (render_task.job_id,),
                                                explicitTransaction = t)

            self.taskFile = '"{0}"'.format(render_job.taskFile)
            self.renderCMD = " ".join([self.execsDict[render_job.execName],
                                    render_job.baseCMD,
                                    '-s', str(render_task.startFrame),
                                    '-e', str(render_task.endFrame),
                                    self.taskFile])

            #Create log for this task and update task entry in the DB
            if not os.path.isdir(Constants.RENDERLOGDIR):
                os.makedirs(Constants.RENDERLOGDIR)
            render_task.logFile = os.path.join(Constants.RENDERLOGDIR,
                                            '{:0>10}.log.txt'.format(render_task.id))
            render_task.status = STARTED
            render_task.host = thisNode.host
            thisNode.status = STARTED
            thisNode.task_id = render_task.id
            render_task.startTime = datetime.datetime.now()
            render_task.update(t)
            thisNode.update(t)
            JobUtils.updateJobTaskCount(render_task.job_id)

        logger.info('Starting render task {0}'.format(render_task.id))
        log = file(render_task.logFile, 'w')

        try:
            log.write('Hydra log file {0} on {1}\n'.format(render_task.logFile, render_task.host))
            log.write('RenderNodeMain is {0}\n'.format(sys.argv))
            log.write('Command: {0}\n\n'.format(self.renderCMD))
            Utils.flushOut(log)

            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(self.renderCMD, stdout = log,
                                                **Utils.buildSubprocessArgs(False))

            logger.info('Started PID {0} to do Task {1}'.format(self.childProcess.pid,
                                                                render_task.id))

            #Start the timeout thread
            tThread = False
            if render_job.timeout > 0:
                tThread = True
                self.startTimeoutThread(render_job.timeout)

            #Wait until the job is finished or terminated
            self.childProcess.communicate()

            #When finished, gather info on exit and record
            if tThread:
                self.timeoutThread.cancel()

            render_task.exitCode = self.childProcess.returncode
            logString = "\nProcess exited with code {0} at {1} on {2}\n"
            nowTime = datetime.datetime.now().replace(microsecond = 0)
            log.write(logString.format(render_task.exitCode, nowTime,
                                        self.thisNodeName))

        except Exception, e:
            traceback.print_exc(e, log)
            raise

        #Finally, update the DB with the information from the task
        finally:
            #Get the latest info about this render node
            with transaction() as t:
                thisNode = hydra_rendernode.fetch("WHERE host = %s",
                                                    (self.thisNodeName,),
                                                    explicitTransaction = t)

                error = False
                if self.childKilled:
                    render_task.status = self.statusAfterDeath
                    self.childKilled = False
                    if self.statusAfterDeath == TIMEOUT:
                        error = True
                else:
                    if render_task.exitCode == 0:
                        render_task.status = FINISHED
                        render_task.endTime = datetime.datetime.now()
                    else:
                        error = True

                if error:
                    render_task.attempts += 1
                    if render_task.failures == None:
                        render_task.failures = thisNode.host
                    else:
                        render_task.failures += " {0}".format(thisNode.host)

                    if render_task.attempts >= render_task.maxAttempts:
                        render_task.status = ERROR
                        render_task.endTime = datetime.datetime.now()
                    else:
                        render_task.status = READY
                        render_task.startTime = None
                        render_task.endTime = None

                if thisNode.status == STARTED:
                    thisNode.status = IDLE
                elif thisNode.status == PENDING:
                    thisNode.status = OFFLINE
                logger.debug("Node Status: {0}".format(thisNode.status))
                thisNode.task_id = None

                render_task.update(t)
                thisNode.update(t)

            log.close()
            self.childProcess = None
            self.childKilled = False
            self.statusAfterDeath = None
            JobUtils.updateJobTaskCount(render_task.job_id)
            JobUtils.manageNodeLimit(render_task.job_id)
            logger.info('Done with render task {0}'.format(render_task.id))

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one."""
        self.childKilled = True
        self.statusAfterDeath = statusAfterDeath
        #Gather subprocesses just in case
        if psutil.pid_exists(self.childProcess.pid):
            psutil_proc = psutil.Process(self.childProcess.pid)
            children_procs = psutil_proc.children(recursive=True)
        else:
            logger.error("PSUtil was unable to find process with PID {0}".format(self.childProcess.pid))
            children_procs = []

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

    def timeoutCurrentJob(self):
        logger.warning("Current job is timed out, killing...")
        self.timeoutThread.cancel()
        self.killCurrentJob(TIMEOUT)
        if self.childKilled:
            logger.info("Task was timed out")

    def startTimeoutThread(self, timeout):
        self.timeoutThread = threading.Timer(timeout, self.timeoutCurrentJob)
        try:
            self.timeoutThread.start()
            minutes = timeout / 60
            seconds  = timeout % 60
            infoStr = "Starting Timeout Thread for {0} minute(s) and {1} second(s)"
            logger.info(infoStr.format(minutes, seconds))
        except Exception as err:
            self.timeoutThread.cancel()
            logger.error("Could not start timeout thread!")
            logger.error(str(err))

def heartbeat(interval = 60):
    host = Utils.myHostName()
    while True:
        try:
            with transaction() as t:
                t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = %s",
                            (host,))
        except Exception, e:
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

    if nInstances > 1:
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
    socketServer.createIdleLoop(5, socketServer.processRenderTasks)
    pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
    pulseThread.start()

if __name__ == '__main__':
    main()
