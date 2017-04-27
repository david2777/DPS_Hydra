#Standard
import os
import sys
import datetime
import subprocess
import traceback

#Third Party
import psutil

#Hydra
import Constants
from hydra.logging_setup import logger
import hydra.hydra_sql as sql
import hydra.single_instance as single_instance
import hydra.hydra_utils as hydra_utils
import networking.servers as servers

class RenderTCPServer(servers.TCPServer):
    """RenderTCPServer waits for a TCP connection from the RenderManagerServer
    telling it to start a render task. The render task is processed and the results
    updated in the database."""
    def __init__(self):
        #Setup Class Variables
        self.renderThread = None
        self.childProcess = None
        self.PSUtilProc = None
        self.statusAfterDeath = None
        self.childKilled = 0

        #Get this node data from the database and make sure it exists
        self.thisNode = sql.get_this_node()
        logger.debug(self.thisNode)
        if not self.thisNode:
            logger.critical("This node does not exist in the database! Please Register this node and try again.")
            sys.exit(-1)
            return

        self.keepAllLogs = hydra_utils.get_info_from_cfg("hydra", "keep_all_render_logs")
        self.keepAllLogs = True if self.keepAllLogs.lower().startswith("t") else False

        #Create RenderLog Directory if it doesn't exit
        if not os.path.isdir(Constants.RENDERLOGDIR):
            os.makedirs(Constants.RENDERLOGDIR)

        self.unstick_task()

        #Run The Server
        port = int(hydra_utils.get_info_from_cfg("network", "port"))
        self.startServerThread(port)
        self.createIdleLoop("Render_Loop_Thread", self.render_loop, 5)

    def render_loop(self):
        self.thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (self.thisNode.host,),
                                                    multiReturn=False)

        if self.thisNode.status in [sql.OFFLINE, sql.PENDING, sql.STARTED]:
            return

        #TODO: Figure out a way to keep phase 02 from starting too many tasks at the same time

        sqlQuery = """SELECT T.* FROM hydra.hydra_taskboard T
                        JOIN (SELECT id, failedNodes, attempts, maxAttempts,
                                    maxNodes, requirements, archived
                                FROM hydra.hydra_jobboard) J
                        ON (T.job_id = J.id)
                        WHERE T.status = 'R'
                            AND J.archived = 0
                            AND T.priority > %s
                            AND J.maxAttempts > J.attempts
                            AND J.failedNodes NOT LIKE %s
                            AND %s LIKE J.requirements
                            AND (J.maxNodes = 0
                                OR J.maxNodes > (SELECT COUNT(*)
                                                FROM hydra.hydra_taskboard
                                                WHERE job_id = T.job_id
                                                    AND status = 'S'))
                        ORDER BY T.priority DESC, T.id ASC
                        LIMIT 1;"""

        sqlTuple = (self.thisNode.minPriority, self.thisNode.get_sql_selector(), self.thisNode.capabilities)

        with sql.transaction() as t:
            logger.debug("Checking for tasks")
            renderTask = sql.hydra_taskboard.doFetch(t, sqlQuery, sqlTuple,
                                                        multiReturn=False)
            if renderTask:
                logger.debug("RenderTask found %s", renderTask)
                renderJob = renderTask.get_job()
                #Task Updates
                renderTask.status = "S"
                renderTask.host = self.thisNode.host
                renderTask.startTime = datetime.datetime.now().replace(microsecond=0)
                #Job Updates
                renderJob.status = "S"
                #Node Updates
                self.thisNode.status = "S"
                self.thisNode.task_id = renderTask.id
                #Push updates to the db
                renderTask.update(t)
                renderJob.update(t)
                self.thisNode.update(t)

        if renderTask and renderJob:
            self.launch_render_task(renderJob, renderTask)

    def unstick_task(self, statusAfterDeath=sql.READY):
        """Cleanup task if the node starts with one assigned to it
        (Like if the node crashed/restarted)"""
        task = None
        with sql.transaction() as t:
            if self.thisNode.status in [sql.STARTED, sql.PENDING]:
                self.thisNode.status = sql.IDLE if self.thisNode.status == sql.STARTED else sql.OFFLINE

            if self.thisNode.task_id:
                task = sql.hydra_taskboard.fetch("WHERE id = %s", (self.thisNode.task_id,),
                                                multiReturn=False, explicitTransaction=t)
                task.status = statusAfterDeath
                task.endTime = datetime.datetime.now().replace(microsecond=0)
                task.exitCode = 999
                self.thisNode.task_id = None

            self.thisNode.update(t)
            if task:
                task.update(t)

    def shutdown(self):
        """Offline node, Kill current job, shutdown servers, reset node status"""
        self.thisNode = sql.get_this_node()
        currentStatus = self.thisNode.status
        newStatus = sql.IDLE if currentStatus in [sql.IDLE, sql.STARTED] else sql.OFFLINE
        if currentStatus in [sql.STARTED, sql.PENDING] or self.childProcess:
            self.thisNode.get_off()
        else:
            self.thisNode.offline()

        servers.TCPServer.shutdown(self)

        if newStatus == sql.IDLE:
            self.thisNode.online()
        else:
            self.thisNode.offline()

        logger.info("RenderNode servers Shutdown")

    def reboot(self):
        """Shutdown and restart node"""
        self.shutdown()
        if sys.platform.startswith("win"):
            os.system("shutdown -r -f -t 60 -c \"Rebooting to update RenderNode software\"")
        else:
            os.system("reboot now")

    def launch_render_task(self, job, task):
        """Does the actual rendering, then records the results on the database"""
        logger.info("Starting task with id %s on job with id %s", task.id, task.job_id)
        self.childKilled = 0
        self.statusAfterDeath = None
        self.childProcess = None
        self.PSUtilProc = None

        renderTaskCMD = task.create_task_cmd(job, sys.platform)
        logPath = task.get_log_path()
        logger.debug(renderTaskCMD)

        try:
            log = file(logPath, 'w')
        except (IOError, OSError, WindowsError) as e:
            logger.error(e)
            self.thisNode.offline()
            self.shutdown()
            return

        log.write('Hydra log file {0} on {1}\n'.format(logPath, self.thisNode.host))
        log.write('RenderNode is {0}\n'.format(sys.argv))
        log.write('Command: {0}\n\n'.format(renderTaskCMD))
        flush_out(log)

        try:
            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(renderTaskCMD,
                                                stdout=log, stderr=log,
                                                **build_subprocess_args(False))

            logger.info("Started PID %s to do Task %s", self.childProcess.pid, task.id)

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
            #unstick_task will update all info on the DB and cleanup variables
            self.unstick_task()
            return

        with sql.transaction() as t:
            #Task
            logger.debug("childKilled = %s", self.childKilled)
            task.endTime = datetime.datetime.now().replace(microsecond=0)
            if self.childProcess:
                if self.childKilled == 0:
                    task.exitCode = self.childProcess.returncode
                else:
                    task.exitCode = 1
            else:
                task.exitCode = 1234

            if task.exitCode == 0:
                task.status = sql.FINISHED
                task.mpf = (task.endTime - task.startTime)
            else:
                task.status = sql.READY
                task.host = ""
            task.update(t)
            #Job
            taskList = task.get_other_subtasks(["status"], t)
            taskList += [task]
            allTaskDone = all([ta.status == sql.FINISHED for ta in taskList])
            anyTaskStart = any([ta.status == sql.STARTED for ta in taskList])
            anyTaskReady = any([ta.status == sql.READY for ta in taskList])
            anyTaskError = any([ta.status == sql.ERROR for ta in taskList])
            if allTaskDone:
                job.status = sql.FINISHED
            elif anyTaskStart:
                job.status = sql.STARTED
            elif anyTaskReady:
                job.status = sql.READY
            elif anyTaskError:
                job.status = sql.ERROR
            else:
                job.status = sql.PAUSED

            if task.exitCode != 0 and self.childKilled == 0:
                job.attempts += 1
                job.failedNodes += "{} ".format(self.thisNode.host)

            if job.attempts >= job.maxAttempts:
                job.status = sql.ERROR

            if task.exitCode == 0:
                if job.mpf:
                    job.mpf = ((job.mpf + task.mpf) / 2)
                else:
                    job.mpf = task.mpf
            job.update(t)
            #Node
            self.thisNode = sql.hydra_rendernode.fetch("WHERE host = %s", (self.thisNode.host,))
            self.thisNode.task_id = None
            self.thisNode.status = sql.OFFLINE if self.thisNode.status == sql.PENDING else sql.IDLE
            self.thisNode.update(t)

        logString = "\nProcess exited with code {0} at {1} on {2}\n"
        log.write(logString.format(task.exitCode, task.endTime, self.thisNode.host))
        self.childProcess = None
        self.PSUtilProc = None

        log.close()
        if not self.keepAllLogs and task.exitCode == 0:
            try:
                os.remove(logPath)
            except (OSError, WindowsError):
                logger.warning("Unable to remove log")

        logPath = None

        logger.info("Done with render task %s", task.id)
        return

    #--------------------------------------------------------------------------#
    #-------------------------Incoming TCP Handlers----------------------------#
    #--------------------------------------------------------------------------#

    def kill_current_job(self, statusAfterDeath):
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
    host = hydra_utils.my_host_name()
    with sql.transaction() as t:
        t.cur.execute("UPDATE hydra_rendernode SET pulse = NOW() "
                    "WHERE host = '{0}'".format(host))

def build_subprocess_args(include_stdout=False):
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        env = os.environ
    else:
        si = None
        env = None

    ret = {'stdin': subprocess.PIPE,
            'startupinfo': si, 'env': env}

    if include_stdout:
        ret.update({'stdout:': subprocess.PIPE})

    return ret

def flush_out(f):
    """Flush and sync a file to disk"""
    f.flush()
    os.fsync(f.fileno())

if __name__ == "__main__":
    logger.info("Starting in %s", os.getcwd())
    logger.info("arglist %s", sys.argv)

    #Check for other RenderNode isntances
    lockFile = single_instance.InstanceLock("HydraRenderNode")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderNode is allowed to run at a time! Exiting...")
        sys.exit(-1)

    #Start the Render Server and Heartbeat Thread
    socketServer = RenderTCPServer()
    #socketServer.createIdleLoop("Pulse_Thread", heartbeat, 60)
