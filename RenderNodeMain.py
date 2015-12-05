#Standard
import os                           #@UnusedImport
import sys
import time
import threading
import datetime
import traceback
import subprocess

#Hydra
from Constants import *             #@UnusedWildImport
from Servers import TCPServer
from LoggingSetup import logger     #@UnusedImport
import Utils                        #@UnusedImport
from Answers import RenderAnswer    #Unused?
from MySQLSetup import *            #@UnusedWildImport
import TaskUtils

class RenderTCPServer(TCPServer):
    def __init__(self, *arglist, **kwargs):
        #Check for another instance of RenderNodeMain.exe
        nInstances = len (filter (lambda line: 'RenderNodeMain' in line,
                                  subprocess.check_output ('tasklist').split('\n')))
        logger.info ("%d RenderNodeMain instances running." % nInstances)
        if nInstances > 1:
            logger.info("Blocked RenderNodeMain from running because another"
                        " instance already exists.")
            sys.exit(1)
        if nInstances == 0 and not sys.argv[0].endswith('.py'):
            logger.error("Can't find running RenderNodeMain.")
            sys.exit(1)

        TCPServer.__init__(self, *arglist, **kwargs)
        self.childProcess = None
        self.childKilled = False
        self.statusAfterDeath = None #Must be a status from MySQLSetup

        #Clean up in case we had an unexpected termination last time around
        [thisNode] = hydra_rendernode.fetch ("where host = '%s'" % Utils.myHostName())

        if thisNode.task_id:
            if thisNode.status == PENDING or thisNode.status == OFFLINE:
                newStatus = OFFLINE
            else:
                newStatus = IDLE
            taskUtils.unstick(taskID=thisNode.task_id, newTaskStatus=CRASHED, host=thisNode.host, newHostStatus=newStatus)

        #Update current software version if necessary
        current_version = sys.argv[0]
        if thisNode.software_version != current_version:
            thisNode.software_version = current_version
            with transaction() as t:
                thisNode.update(t)

    def processRenderTasks(self):
        [thisNode] = hydra_rendernode.fetch ("where host = '%s'" % Utils.myHostName())
        logger.info("""Host: %r
         Status: %r
         Capabilities %r""", thisNode.host, thisNode.status, thisNode.capabilities)

        #If this node is not idle, don't try to find a new job
        if thisNode.status != IDLE:
            return

        #Otherwise, get a job that's:
        #-Ready to be run and
        #-Has a high enough priority level for this particular node and
        queryString = ("where status = '%s' and priority >= %s" % (READY, thisNode.minPriority))
        queryString += " and '%s' like requirements" % thisNode.capabilities

        with transaction() as t:
            render_tasks = hydra_rendertask.fetch (queryString, limit=1, explicitTransaction=t)
            if not render_tasks:
                return
            render_task = render_tasks[0]

            #Create log for this task and update task entry in the database
            if not os.path.isdir(RENDERLOGDIR):
                os.makedirs(RENDERLOGDIR)
            render_task.logFile = os.path.join(RENDERLOGDIR, '%010d.log.txt' % render_task.id )
            render_task.status = STARTED
            render_task.host = thisNode.host
            thisNode.status = STARTED
            thisNode.task_id = render_task.id
            render_task.startTime = datetime.datetime.now()
            render_task.update(t)
            thisNode.update(t)

        logger.debug ('working on render task %s', render_task.id)
        log = file(render_task.logFile, 'w')

        try:
            log.write('hydra log file %s on %s\n' % (render_task.logFile, render_task.host))
            log.write('RenderNodeMain is %s\n' % sys.argv)
            log.write('Command: %s\n\n' % (render_task.command))
            Utils.flushOut(log)

            #Run the job and keep track of the process
            self.childProcess = subprocess.Popen(eval( render_task.command ), stdout = log, stderr = subprocess.STDOUT )
            logger.debug('started PID %s to do task %s',
                          self.childProcess.pid, render_task.id)

            #Wait until the job is finished or terminated
            render_task.exitCode = self.childProcess.wait()

            log.write('\nProcess exited with code %d\n' % render_task.exitCode)
            return RenderAnswer()

        except Exception, e:
            traceback.print_exc( e, log )
            raise

        finally:
            #Get the latest info about this render node
            with transaction() as t:
                [thisNode] = hydra_rendernode.fetch ("where host = '%s'" % Utils.myHostName(), explicitTransaction=t)

                #Check if job was killed, update the job board accordingly
                if self.childKilled:
                    #Reset the rendertask
                    render_task.status = self.statusAfterDeath
                    render_task.startTime = None
                    render_task.host = None
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

                #Return to 'IDLE' IFF current status is 'STARTED'
                if thisNode.status == STARTED:
                    logger.debug("status: %r", thisNode.status)
                    thisNode.status = IDLE
                elif thisNode.status == PENDING:
                    thisNode.status = OFFLINE
                thisNode.task_id = None

                #Update the records
                render_task.update(t)
                thisNode.update(t)

            log.close()
            #Discard info about the previous child process
            self.childProcess = None
            logger.debug ('done with render task %s', render_task.id)

    def killCurrentJob(self, statusAfterDeath):
        """Kills the render node's current job if it's running one."""
        logger.debug("killing %r", self.childProcess)
        print "Status after death should be: {0:s}".format(statusAfterDeath)
        if self.childProcess:
            self.childProcess.kill()
            self.childKilled = True
            self.statusAfterDeath = statusAfterDeath
        else:
            logger.debug("no process was running.")

def heartbeat(interval = 5):
    host = Utils.myHostName()
    while True:
        try:
            with transaction() as t:
                t.cur.execute("update hydra_rendernode "
                    "set pulse = NOW() "
                    "where host = '%s'" % host)
        except Exception, e:
            logger.error (traceback.format_exc (e))
        time.sleep(interval)

def main():
    logger.info ('starting in %s', os.getcwd())
    logger.info ('arglist %s', sys.argv)
    socketServer = RenderTCPServer()
    socketServer.createIdleLoop (5, socketServer.processRenderTasks )
    pulseThread = threading.Thread(target = heartbeat, name = "heartbeat", args = (60,))
    pulseThread.start()

if __name__ == '__main__':
    main()