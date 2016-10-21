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
    def __init__(self, *arglist, **kwargs):
        self.managmentServer = TCPServer.__init__(self, *arglist, **kwargs)

        self.allJobs = {}
        self.renderJobs = []
        self.runningTasks = {}
        self.allNodes = {}
        self.idleNodes = []
        self.timeouts = {}
        self.nowTime = datetime.datetime.now()
        self.lastTimeoutCheck = None

    def processRenderTasks(self):
        logger.debug("Processing Render Tasks")
        #Fetch all Jobs
        jobList = hydra_jobboard.fetch("WHERE archived = 0 AND status IN ('R','S','X')", multiReturn=True)
        self.allJobs = {x.id : x for x in jobList}

        taskList = hydra_taskboard.fetch("WHERE status = 'S'", multiReturn=True)
        self.runningTasks = defaultdict(list)
        for task in taskList:
            self.runningTasks[int(task.job_id)].append(task)

        self.renderJobs = self.createRenderJobs(self.allJobs)
        logger.debug(self.renderJobs)

        #Fetch all Nodes and find out which ones are online
        nodeList = hydra_rendernode.fetch(multiReturn=True)
        self.allNodes = {str(x.host) : x for x in nodeList}
        self.idleNodes = [k for k, v in self.allNodes.iteritems() if v.status == IDLE]
        self.idleNodes = self.checkNodeStatus(self.idleNodes)

        #Assign Tasks to Nodes
        self.assignRenderJobs(self.renderJobs, self.idleNodes, self.allJobs,
                                self.allNodes)

        #Check on timeouts
        #reutrnList = self.checkOnTimeouts(self.timeouts)
        #self.timeouts = returnList[0]
        #self.lastTimeoutCheck = returnList[1]
        #self.nowTime = returnList[2]

        #Done! Wait to loop through again.
        logger.debug("End of loop. Waiting...")

    def createRenderJobs(self, allJobs):
        logger.debug("Creating Render Jobs")
        #Sorting
        sortedJobs = sorted(allJobs.values(), key=attrgetter("priority"), reverse=True)
        sortedJobs = sorted(sortedJobs, key=attrgetter("id"))
        #Filtering
        renderJobs = []
        for job in sortedJobs:
            renderLayers = job.renderLayers.split(",")
            renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]

            if all([int(x) == int(job.endFrame) for x in renderLayerTracker]):
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'F' WHERE id = %s", (job.id,))



            if len(renderLayers) != len(renderLayerTracker):
                logger.critical("Malformed renderLayers or renderLayerTracker on job with id %d", job.id)
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'E' WHERE id = %s", (job.id,))
                break

            runningRenderLayers = [x.renderLayer for x in self.runningTasks[int(job.id)]]
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
                if job.endFrame != renderLayerTracker[i]:
                    if renderLayers[i] not in runningRenderLayers:
                        renderJobs.append([int(job.id), str(renderLayers[i])])
        return renderJobs

    @staticmethod
    def checkNodeStatus(idleNodes):
        logger.debug("Checking Node Status on Idle Nodes")
        onlineList = []
        for node in idleNodes:
            connection = TCPConnection(hostname=node)
            answer = connection.getAnswer(IsAliveQuestion())
            if not answer:
                logger.debug("%s could not be reached! Removing from Idle Nodes.", node)
            else:
                onlineList.append(node)
        return onlineList

    def assignRenderJobs(self, renderJobs, idleNodes, allJobs, allNodes):
        if len(renderJobs) < 1 or len(idleNodes) < 1:
            logger.debug("No Idle Nodes or Ready Jobs found. Skipping assignment...")
            return True
        logger.debug("Assigning Render Tasks")
        for node in self.idleNodes:
            for jobID, renderLayer in self.renderJobs:
                jobOBJ = allJobs[jobID]
                nodeOBJ = allNodes[node]
                response = self.filterTask(jobOBJ, nodeOBJ)
                if response:
                    startFrame = self.getStartFrame(jobOBJ, renderLayer)
                    taskOBJ = hydra_taskboard(job_id=jobID, status="S",
                                            startTime=datetime.datetime.now(),
                                            host=node,
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
                        self.renderJobs.remove([jobID, renderLayer])
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

    def shutdownCMD(self):
        self.managmentServer.shutdown()

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
    def checkOnTimeouts(timeouts, lastTimeoutCheck, nowTime):
        logger.debug("Checking on Tasks in progress with timeouts")
        #TODO: See if this works
        if not lastTimeoutCheck:
            lastTimeoutCheck = nowTime
        nowTime = datetime.datetime.now()
        timeDelta = (nowTime - lastTimeoutCheck).total_seconds()
        iterList = [[k, v] for k, v in timeouts.iteritems()]
        for taskID, timeout in iterList:
            task = hydra_taskboard.fetch("WHERE id = %s", (taskID,))
            if task.status != "S":
                timeouts.pop(taskID, None)
            else:
                timeouts[taskID] = timeout - timeDelta
                if timeouts[taskID] < 0:
                    logger.debug("Kill job should go here...")
        return timeouts, lastTimeoutCheck, nowTime

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

    @staticmethod
    def startTimeoutThread(node, timeout):
        logger.debug("Starting timeout thread for node: %s for : %d seconds", node.host, timeout)

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

    port = int(getInfoFromCFG("manager", "port"))
    socketServer = RenderManagementServer(port=port)
    socketServer.createIdleLoop(15, socketServer.processRenderTasks)

if __name__ == "__main__":
    main()
