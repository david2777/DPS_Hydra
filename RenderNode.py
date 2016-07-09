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
        #Check for another instance of RenderNodeMain.exe
        inst = checkRenderNodeInstances()
        if not inst:
            sys.exit(1)
        #Initiate TCP Server
        self.renderServ = TCPServer.__init__(self, *arglist, **kwargs)
        if sys.platform == "win32":
            self.si = subprocess.STARTUPINFO()
            self.si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        self.rsGPUs = Utils.getRedshiftPreference("SelectedCudaDevices")
        self.rsGPUs = self.rsGPUs.split(",")[:-1]
        self.rsGPUids = [x.split(":")[0] for x in self.rsGPUs]
        if len(self.rsGPUs) != len(self.rsGPUids):
            logger.error("Problems parsing RS Preferences")
            raise Exception("Problems parsing RS Preferences")
        logger.info("{0} Redshift Enabled GPU(s) found on this node".format(len(self.rsGPUs)))
        logger.debug("GPUs available for rendering are {0}".format(self.rsGPUs))

        #Setup class variables
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        self.childProcess = None
        self.childKilled = False
        self.statusAfterDeath = None
        self.thisNodeName = Utils.myHostName()

        #Cleanup job if we start with it assigned to us (Like if the node crashed/restarted)
        logger.debug("Housekeeping...")
        [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (self.thisNodeName,))
        query = "UPDATE hydra_rendernode SET status = %s WHERE host = %s"
        if thisNode.task_id:
            logger.warning("Rouge task discovered. Unsticking...")
            [task] = hydra_taskboard.secureFetch("WHERE id = %s", (thisNode.task_id,))
            if thisNode.status == PENDING or thisNode.status == OFFLINE:
                newStatus = OFFLINE
            else:
                newStatus = IDLE
            TaskUtils.unstick(taskID=thisNode.task_id, newTaskStatus=CRASHED,
                              host=thisNode.host, newHostStatus=newStatus)
            JobUtils.manageNodeLimit(task.job_id)
        elif thisNode.status == STARTED and not thisNode.task_id:
            logger.warning("Reseting bad status.")
            with transaction() as t:
                t.cur.execute(query, (READY, self.thisNodeName,))
        elif thisNode.status == PENDING and not thisNode.task_id:
            logger.warning("Reseting bad status.")
            with transaction() as t:
                t.cur.execute(query, (OFFLINE, self.thisNodeName,))

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
        the job's requirements (Priority & Capabilities)"""
        [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s",(self.thisNodeName,))
        debugStr = "Host: {0} Status: {1} Capabilities {2}"
        logger.debug(debugStr.format(thisNode.host,
                                    niceNames[thisNode.status],
                                    thisNode.capabilities))

        #If this node is not idle, don't try to find a new job
        if thisNode.status != IDLE:
            return


        #Otherwise, get a job that's:
        #-Ready to be run and
        #-Has a high enough priority level for this particular node and
        #-Is able to meet to jobs required capabilities
        #TODO:Secure This?
        queryString = "WHERE status = '{0}'".format(READY)
        queryString += "AND priority >= '{0}'".format(thisNode.minPriority)
        queryString += " AND '{0}' LIKE requirements".format(thisNode.capabilities)
        queryString += " AND archived = '0'"
        queryString += " AND failures NOT LIKE '%{0}%'".format(thisNode.host)
        queryString += " ORDER BY priority DESC, id ASC"

        with transaction() as t:
            render_tasks = hydra_taskboard.fetch(queryString,
                                                limit = 1,
                                                explicitTransaction = t)
            if not render_tasks:
                return
            render_task = render_tasks[0]
            [render_job] = hydra_jobboard.secureFetch("WHERE id = %s",
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
            if sys.platform == "win32":
                self.childProcess = subprocess.Popen(self.renderCMD,
                                                    stdout = log,
                                                    **Utils.buildSubprocessArgs(False))
            else:
                self.childProcess = subprocess.Popen(self.renderCMD,
                                                    stdout = log,
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

            #Gather info on exit and record
            render_task.exitCode = self.childProcess.returncode
            if tThread:
                self.timeoutThread.cancel()
            logString = "\nProcess exited with code {0} at {1} on {2}\n"
            log.write(logString.format(render_task.exitCode,
                                        datetime.datetime.now().replace(microsecond=0),
                                        self.thisNodeName))

        except Exception, e:
            traceback.print_exc(e, log)
            raise

        finally:
            #Get the latest info about this render node
            with transaction() as t:
                [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s",
                                                            (self.thisNodeName,),
                                                            explicitTransaction=t)

                error = False
                #Check if job was killed, update the job board accordingly
                if self.childKilled:
                    #Reset the rendertask
                    render_task.status = self.statusAfterDeath
                    #render_task.startTime = None
                    #render_task.host = None
                    self.childKilled = False
                    #Mark error if task has timedout
                    if self.statusAfterDeath == TIMEOUT:
                        error = True
                else:
                    #Report that the job was finished if exit code is 0
                    if render_task.exitCode == 0:
                        render_task.status = FINISHED
                        render_task.endTime = datetime.datetime.now()
                    #Else, mark error
                    else:
                        error = True
                #Set as error
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
                        render_task.host = None
                        render_task.logFile = None
                        render_task.startTime = None
                        render_task.endTime = None
                        render_task.exitCode = None


                #Return to 'IDLE' IF current status is 'STARTED'
                if thisNode.status == STARTED:
                    thisNode.status = IDLE
                elif thisNode.status == PENDING:
                    thisNode.status = OFFLINE
                logger.debug("Node Status: {0}".format(thisNode.status))
                thisNode.task_id = None

                #Update the records
                render_task.update(t)
                thisNode.update(t)

            log.close()
            #Discard info about the previous child process
            self.childProcess = None
            #Update taskCount
            JobUtils.updateJobTaskCount(render_task.job_id)
            JobUtils.manageNodeLimit(render_task.job_id)
            logger.info('Done with render task {0}'.format(render_task.id))

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one."""
        #Get the subprocesses of the main child process
        try:
            psutil_proc = psutil.Process(self.childProcess.pid)
            children_procs = psutil_proc.children(recursive=True)
        except psutil.NoSuchProcess:
            children_procs = []

        for proc in children_procs:
            try:
                logger.info("Killing subtask with PID of {0}".format(proc.pid))
                os.kill(proc.pid, signal.SIGTERM)
            except WindowsError as err:
                logger.error("Could not kill PID {0} due to a WindowsError")
                logger.error(str(err))

        try:
            logger.info("Killing main task with PID of {0}".format(self.childProcess.pid))
            os.kill(self.childProcess.pid, signal.SIGTERM)
        except WindowsError as err:
            logger.error("Could not kill PID {0} due to a WindowsError")
            logger.error(str(err))
        self.childKilled = True
        self.statusAfterDeath = statusAfterDeath

    def timeoutCurrentJob(self):
        logger.warning("Current job is timed out, killing...")
        self.timeoutThread.cancel()
        self.killCurrentJob(TIMEOUT)
        if self.statusAfterDeath == TIMEOUT:
            logger.info("Job timed out!")
        else:
            logger.info("Job was not timed out!")

    def startTimeoutThread(self, timeout):
        self.timeoutThread = threading.Timer(timeout, self.timeoutCurrentJob)
        try:
            self.timeoutThread.start()
            hours = timeout / 60
            minutes  = timeout % 60
            infoStr = "Starting Timeout Thread for {0} hours and {1} seconds"
            logger.info(infoStr.format(hours, minutes))
        except Exception as err:
            self.timeoutThread.cancel()
            logger.error("Could not start timeout thread!")
            logger.error(str(err))

def heartbeat(interval = 5):
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
    #TODO: Fix This
    if sys.platform == "win32":
        subprocessOutput = subprocess.check_output('tasklist', **Utils.buildSubprocessArgs(False))
        nInstances = len(filter(lambda line: 'RenderNode' in line,
                        subprocessOutput.split('\n')))
    else:
        nInstances = len(filter(lambda line: 'RenderNode' in line,
                        subprocess.check_output(["ps", "-af"], **Utils.buildSubprocessArgs(False)).split('\n')))
    logger.debug("{0} RenderNode instances running.".format(nInstances))

    if nInstances > 2:
        logger.error("Blocked RenderNodeMain from running because another"
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
