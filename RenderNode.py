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

#3rd Party
import psutil

#Hydra
from Servers import TCPServer
from LoggingSetup import logger
from Answers import RenderAnswer
from MySQLSetup import *
import Constants
import Utils
import JobUtils
import TaskUtils

class RenderTCPServer(TCPServer):
    def __init__(self, *arglist, **kwargs):
        #Check for another instance of RenderNodeMain.exe
        nInstances = len(filter(lambda line: 'RenderNode' in line,
                                  subprocess.check_output('tasklist').split('\n')))
        logger.info("{0} RenderNodeMain instances running.".format(nInstances))
        if nInstances > 1:
            logger.error("Blocked RenderNodeMain from running because another"
                        " instance already exists.")
            sys.exit(1)
        if nInstances == 0 and not sys.argv[0].endswith('.py'):
            logger.warning("Can't find running RenderNodeMain.")

        #Initiate TCP Server
        self.renderServ = TCPServer.__init__(self, *arglist, **kwargs)

        #Setup class variables
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        self.childProcess = None
        self.childKilled = False
        self.statusAfterDeath = None
        self.thisNodeName = Utils.myHostName()

        #Cleanup job if we start with it assigned to us (Like if the node crashed/restarted)
        [thisNode] = hydra_rendernode.fetch("WHERE host = '{0}'".format(self.thisNodeName))
        if thisNode.task_id:
            logger.info("Unsticking...")
            [task] = hydra_taskboard.fetch("WHERE id = '{0}'".format(thisNode.task_id))
            if thisNode.status == PENDING or thisNode.status == OFFLINE:
                newStatus = OFFLINE
            else:
                newStatus = IDLE
            TaskUtils.unstick(taskID=thisNode.task_id, newTaskStatus=CRASHED,
                              host=thisNode.host, newHostStatus=newStatus)
            JobUtils.manageNodeLimit(task.job_id)

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
        [thisNode] = hydra_rendernode.fetch("WHERE host = '{0}'".format(self.thisNodeName))

        logger.debug("Host: {0} Status: {1} Capabilities {2}".format(thisNode.host, niceNames[thisNode.status], thisNode.capabilities))

        #If this node is not idle, don't try to find a new job

        if thisNode.status != IDLE:
            return


        #Otherwise, get a job that's:
        #-Ready to be run and
        #-Has a high enough priority level for this particular node and
        #-Is able to meet to jobs required capabilities
        queryString = "WHERE status = '{0}'".format(READY)
        queryString += "AND priority >= '{0}'".format(thisNode.minPriority)
        queryString += " AND '{0}' LIKE requirements".format(thisNode.capabilities)
        queryString += " AND archived = '0'"
        queryString += " ORDER BY priority DESC, id ASC"

        with transaction() as t:
            render_tasks = hydra_taskboard.fetch(queryString,
                                                limit = 1,
                                                explicitTransaction = t)
            if not render_tasks:
                return
            render_task = render_tasks[0]
            [render_job] = hydra_jobboard.fetch("WHERE id = '{0}'".format(render_task.job_id),
                                                explicitTransaction = t)

            self.taskFile = '"{0}"'.format(render_job.taskFile)
            self.renderCMD = " ".join([self.execsDict[render_job.execName],
                                    render_job.baseCMD,
                                    '-mr:v', '5',
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
            self.childProcess = subprocess.Popen(self.renderCMD,
                                                stdout = log,
                                                stderr = subprocess.STDOUT)
            logger.info('Started PID {0} to do Task {1}'.format(self.childProcess.pid,
                                                                render_task.id))

            #Wait until the job is finished or terminated
            #NOTE: This lockes up the main thread!
            #TODO:Communicate prevents deadlocking but seems to cause a window
            #     to popup for a split second after rendering. Will check out later
            self.childProcess.communicate()
            render_task.exitCode = self.childProcess.returncode
            logString = "\nProcess exited with code {0} at {1} on {2}\n"
            log.write(logString.format(render_task.exitCode,
                                        datetime.datetime.now().replace(microsecond=0),
                                        self.thisNodeName))
            return RenderAnswer()

        except Exception, e:
            traceback.print_exc(e, log)
            raise

        finally:
            #Get the latest info about this render node
            with transaction() as t:
                [thisNode] = hydra_rendernode.fetch("WHERE host = '{0}'".format(self.thisNodeName),
                                                    explicitTransaction=t)

                #Check if job was killed, update the job board accordingly
                if self.childKilled:
                    #Reset the rendertask
                    render_task.status = self.statusAfterDeath
                    #render_task.startTime = None
                    #render_task.host = None
                    self.childKilled = False
                else:
                    #Report that the job was finished if exit code is 0
                    if render_task.exitCode == 0:
                        render_task.status = FINISHED
                    #Else, report error
                    else:
                        render_task.status = ERROR
                    #Get the datetime
                    render_task.endTime = datetime.datetime.now()

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

        #Using a while statement to get around the thread being locked by STDOUT
        while self.childProcess:
            #Log and kill all of the subprocesses
            for proc in children_procs:
                logger.info("Killing subtask with PID of {0}".format(proc.pid))
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                except WindowsError as err:
                    logger.error("Could not kill PID {0} due to a WindowsError")
                    logger.error(str(err))
            #Log and kill the main child process
            logger.info("Killing main task with PID of {0}".format(self.childProcess.pid))
            os.kill(self.childProcess.pid, signal.SIGTERM)
            #Set status as killed
            self.childKilled = True
            self.statusAfterDeath = statusAfterDeath
        else:
            logger.warning("No process was running.")

    def monitorThread(self, interval):
        """This will be a thread running to do things like check file output
        and watch for timeouts.
        Note: Will need to be run by RenderNodeExternals for RenderNodeService"""
        raise NotImplementedError


def heartbeat(interval = 5):
    host = Utils.myHostName()
    while True:
        try:
            with transaction() as t:
                t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() WHERE host = '{0}'".format(host))
        except Exception, e:
            logger.error(traceback.format_exc(e))
        time.sleep(interval)

def main():
    logger.info('Starting in {0}'.format(os.getcwd()))
    logger.info('arglist {0}'.format(sys.argv))
    socketServer = RenderTCPServer()
    socketServer.createIdleLoop(5, socketServer.processRenderTasks)
    pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
    pulseThread.start()

if __name__ == '__main__':
    main()
