from __future__ import division
#Standard
import os
import sys
import datetime
from operator import attrgetter
from collections import defaultdict

#Hydra
from Setups.LoggingSetup import logger
from Setups.SingleInstanceLocker import InstanceLock
from Setups.MySQLSetup import *
from Networking.Servers import TCPServer
from Networking.Questions import IsAliveQuestion, StartRenderQuestion
from Networking.Connections import TCPConnection
from Utilities.Utils import getInfoFromCFG

#pylint: disable=C0200

class RenderManagementServer(TCPServer):
    def __init__(self):
        port = int(getInfoFromCFG("manager", "port"))
        self.startServerThread(port)

    def processRenderTasks(self):
        logger.debug("Processing Render Tasks")
        #Fetch all Jobs
        jobList = hydra_jobboard.fetch("WHERE archived = 0 AND status IN ('R','S')", multiReturn=True)
        allJobs = {x.id : x for x in jobList}

        #Find all running tasks
        taskList = hydra_taskboard.fetch("WHERE status = 'S'", multiReturn=True)
        runningTasks = defaultdict(list)
        for task in taskList:
            runningTasks[int(task.job_id)].append(task)

        self.updateJobStatuses(allJobs)
        renderJobs = self.createRenderJobs(allJobs, runningTasks)
        logger.debug("RenderJobs: %s", str(renderJobs))
        #if renderJobs:
            #renderJobsList = [x[0] for x in renderJobs]
            #renderJobOBJList = [v for k, v in allJobs.iteritems() if k in renderJobsList]
            #Tasks have no priority!
            #self.shuffleQueue(renderJobOBJList, taskList)

        #Fetch all Nodes and find out which ones are online
        nodeList = hydra_rendernode.fetch(multiReturn=True)
        runningNodes = [x for x in nodeList if x.status == STARTED]
        if renderJobs:
            idleNodes = [x for x in nodeList if x.status == IDLE]
            idleNodes = self.checkNodeStatus(idleNodes)

        #Check on node timeouts
        self.checkOnTimeouts(runningNodes)

        if renderJobs:
            #Assign Tasks to Nodes
            self.assignRenderJobs(renderJobs, idleNodes, allJobs)

        #Done! Wait to loop through again.
        logger.debug("End of loop. Waiting...")

    def shutdownCMD(self):
        self.shutdown()

    def assignRenderJobs(self, renderJobs, idleNodes, allJobs):
        if len(renderJobs) < 1 or len(idleNodes) < 1:
            logger.debug("No Idle Nodes or Ready Jobs found. Skipping assignment...")
            return True
        logger.debug("Assigning Render Tasks")
        for nodeOBJ in idleNodes:
            for jobID, renderLayer in renderJobs:
                jobOBJ = allJobs[jobID]
                response = self.filterTask(jobOBJ, nodeOBJ)
                if response:
                    startFrame = self.getStartFrame(jobOBJ, renderLayer)
                    taskOBJ = hydra_taskboard(job_id=jobID, status="S",
                                            startTime=datetime.datetime.now(),
                                            host=nodeOBJ.host,
                                            renderLayer=renderLayer,
                                            startFrame=startFrame,
                                            endFrame=jobOBJ.endFrame,
                                            currentFrame=startFrame)
                    with transaction() as t:
                        taskOBJ.insert(t)
                    result = self.assignTask(nodeOBJ, taskOBJ, jobOBJ)
                    #pylint: disable=E1101
                    if result:
                        with transaction() as t:
                            nodeOBJ.status = STARTED
                            nodeOBJ.task_id = taskOBJ.id
                            nodeOBJ.update(t)
                        renderJobs.remove([jobID, renderLayer])
                        break
                    else:
                        logger.debug("Cleaning up task %s", taskOBJ.id)
                        taskOBJ.status = KILLED
                        taskOBJ.endTime = datetime.datetime.now()
                        taskOBJ.exitCode = 101
                        #Mark job failure? Offline node?
                        with transaction() as t:
                            taskOBJ.update(t)
                        break

    def checkOnTimeouts(self, runningNodes):
        logger.debug("Checking on running Nodes for timeouts")
        now = datetime.datetime.now()
        for nodeOBJ in runningNodes:
            if (now - nodeOBJ.pulse) > datetime.timedelta(hours=3):
                logger.debug("Node %s is timed out!", nodeOBJ.host)
                self.getOffNode(nodeOBJ)

    @staticmethod
    def shuffleQueue(jobList, taskList):
        ########################################################################
        ########################################################################
        #TODO: UNTESTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        ########################################################################
        ########################################################################
        logger.debug("Shuffling Render Tasks")
        sortedTasks = sorted(taskList, key=attrgetter("priority"))
        sortedJobs = sorted(jobList, key=attrgetter("priority"))
        for task in sortedTasks:
            for job in sortedJobs:
                logger.debug((task.priority / job.priority))
                #If the job priority is 25% or more higher than the task's,
                #   kill the task to make room for the new job
                if (task.priority / job.priority) < .75:
                    logger.debug("Killing task %s", task.id)
                    break
                else:
                    return

    @staticmethod
    def updateJobStatuses(allJobs):
        updateList = []
        for job in allJobs.values():
            renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]

            tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job.id,), multiReturn=True,
                                            cols=["id", "status"])

            statusList = [t.status for t in tasks]
            #If one task is started and job is not listed as started, call job started
            if STARTED in statusList and job.status != STARTED:
                updateList.append([int(job.id), STARTED])

            #Elif all of the RlTrackers are above the job end frame, job is finished
            elif all([int(x) > int(job.endFrame) for x in renderLayerTracker]):
                updateList.append([int(job.id), FINISHED])

            #Else if it says it's started it's probably just waiting so mark as ready
            elif job.status == STARTED:
                updateList.append([int(job.id), READY])

        for job_id, status in updateList:
            with transaction() as t:
                t.cur.execute("UPDATE hydra_jobboard SET status = %s WHERE id = %s",
                                (status, job_id))

    @staticmethod
    def createRenderJobs(allJobs, runningTasks):
        logger.debug("Creating Render Jobs")
        #Sorting
        sortedJobs = sorted(allJobs.values(), key=attrgetter("priority"), reverse=True)
        sortedJobs = sorted(sortedJobs, key=attrgetter("id"))
        #Filtering
        renderJobs = []
        for job in sortedJobs:
            renderLayers = job.renderLayers.split(",")
            renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]

            if len(renderLayers) != len(renderLayerTracker):
                logger.critical("Malformed renderLayers or renderLayerTracker on job with id %d", job.id)
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'E' WHERE id = %s", (job.id,))
                break

            runningRenderLayers = [x.renderLayer for x in runningTasks[int(job.id)]]

            if job.maxNodes > 0 and len(runningRenderLayers) > 0:
                if len(runningRenderLayers) >= int(job.maxNodes):
                    logger.debug("Skipping job %d because it is over node limit", job.id)
                    break

            if job.attempts >= job.maxAttempts:
                logger.debug("Skipping job %d because it is over attempt limit", job.id)
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'E' WHERE id = %s", (job.id,))
                break

            for i in range(len(renderLayers)):
                if renderLayerTracker[i] <= job.endFrame:
                    if renderLayers[i] not in runningRenderLayers:
                        renderJobs.append([int(job.id), str(renderLayers[i])])

        return renderJobs

    @staticmethod
    def checkNodeStatus(idleNodes):
        logger.debug("Checking Node Status on Idle Nodes")
        onlineList = []
        for nodeOBJ in idleNodes:
            connection = TCPConnection(hostname=nodeOBJ.host)
            answer = connection.getAnswer(IsAliveQuestion())
            if not answer:
                logger.debug("%s could not be reached! Removing from Idle Nodes.", nodeOBJ.host)
            else:
                onlineList.append(nodeOBJ)
        return onlineList

    @staticmethod
    def filterTask(job, node):
        if job.priority < node.minPriority:
            logger.debug("Skipping job %d because it does not meet %s's minPriority requirement", job.id, node.host)
            return False

        if job.failures and job.failures != "":
            failures = job.failures.split(",")
            if node.host in failures:
                logger.debug("Skipping job %d because it has failed on node %s in the past", job.id, node.host)
                return False

        if job.requirements and job.requirements != "":
            jobReqs = job.requirements.split(",")
            nodeCaps = node.capabilities.split(" ")
            checker = [x in nodeCaps for x in jobReqs]
            if not all(checker):
                logger.debug("Skipping job %d because node %s cannot meet its feature requirements", job.id, node.host)
                return False

        #If all of the above tests pass
        return True

    @staticmethod
    def getStartFrame(jobOBJ, renderLayer):
        renderLayers = jobOBJ.renderLayers.split(",")
        frameList = jobOBJ.renderLayerTracker.split(",")
        idx = renderLayers.index(renderLayer)
        frame = int(frameList[idx])
        if frame < jobOBJ.startFrame:
            frame = jobOBJ.startFrame
        return frame

    @staticmethod
    def assignTask(node, task, job):
        logger.debug("Assigning task with id %d to node %s", task.id, node.host)
        connection = TCPConnection(hostname=node.host)
        response = connection.getAnswer(StartRenderQuestion(job, task))
        if response:
            logger.debug("Task %d was accepted on %s", task.id, node.host)
        else:
            logger.error("Task %d was declined on %s", task.id, node.host)
        return response

    @staticmethod
    def killTask(node, statusAfterDeath=KILLED):
        logger.debug("Killing task on node: %s", node.host)
        if node.task_id:
            node.killTask(statusAfterDeath)

    @staticmethod
    def onlineNode(node):
        logger.debug("Onlining node: %s", node.host)

    @staticmethod
    def offlineNode(node):
        logger.debug("Offlining node: %s", node.host)

    @staticmethod
    def getOffNode(node):
        logger.debug("Getting off node: %s", node.host)

def main():
    logger.info("Starting in %s", os.getcwd())
    logger.info("arglist %s", sys.argv)

    #Check for other RenderNode isntances
    lockFile = InstanceLock("HydraRenderManager")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderManager is allowed to run at a time! Exiting...")
        sys.exit(-1)

    socketServer = RenderManagementServer()
    socketServer.createIdleLoop("Process_Render_Tasks_Thread",
                                socketServer.processRenderTasks,
                                interval=15)

if __name__ == "__main__":
    main()
