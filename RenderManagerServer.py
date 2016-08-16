#Standard
import os
import sys
import datetime
from operator import attrgetter
from collections import defaultdict

#Hydra
import Constants
from Setups.LoggingSetup import logger
from Networking.Servers import TCPServer
from Networking.Questions import IsAliveQuestion, StartRenderQuestion
from Networking.Connections import TCPConnection
from Utilities.Utils import getInfoFromCFG
from Setups.MySQLSetup import *

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
        jobList = hydra_jobboard.fetch("WHERE archived = 0 AND status IN ('R','S','X')", multiReturn = True)
        self.allJobs = {x.id : x for x in jobList}

        taskList = hydra_taskboard.fetch("WHERE status = 'S'", multiReturn = True)
        self.runningTasks = defaultdict(list)
        for task in taskList:
            self.runningTasks[int(task.job_id)].append(task)

        self.renderJobs = self.createRenderJobs(self.allJobs)
        logger.debug(self.renderJobs)

        #Fetch all Nodes and find out which ones are online
        nodeList = hydra_rendernode.fetch(multiReturn = True)
        self.allNodes = {str(x.host) : x for x in nodeList}
        self.idleNodes = [k for k,v in self.allNodes.iteritems() if v.status == IDLE]
        self.idleNodes = self.checkNodeStatus(self.idleNodes)

        #Assign Tasks to Nodes
        self.timeouts = self.assignRenderJobs(self.renderJobs, self.idleNodes,
                                                self.allJobs, self.allNodes,
                                                self.timeouts)

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
        sortedJobs = sorted(allJobs.values(), key = attrgetter("priority"), reverse = True)
        sortedJobs = sorted(sortedJobs, key = attrgetter("id"))
        #Filtering
        renderJobs = []
        for job in sortedJobs:
            renderLayers = job.renderLayers.split(",")
            renderLayerTracker = [int(x) for x in job.renderLayerTracker.split(",")]

            if len(renderLayers) != len(renderLayerTracker):
                logger.critical("Malformed renderLayers or renderLayerTracker on job with id {0}".format(job.id))
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'E' WHERE id = %s", (job.id,))
                break

            runningRenderLayers = [x.renderLayer for x in self.runningTasks[int(job.id)]]
            if job.maxNodes > 0:
                if len(runningRenderLayers) < int(job.maxNodes):
                    logger.debug("Skipping job {0} because it is over node limit".format(job.id))
                    break

            if job.attempts >= job.maxAttempts:
                logger.debug("Skipping job {0} because it is over attempt limit".format(job.id))
                with transaction() as t:
                    t.cur.execute("UPDATE hydra_jobboard SET status = 'E' WHERE id = %s", (job.id,))
                break

            for i in range(len(renderLayers)):
                if job.endFrame != renderLayerTracker[i]:
                    if renderLayers[i] not in runningRenderLayers:
                        renderJobs.append([int(job.id), str(renderLayers[i])])
        return renderJobs

    def checkNodeStatus(self, idleNodes):
        logger.debug("Checking Node Status on Idle Nodes")
        onlineList = []
        for node in idleNodes:
            connection = TCPConnection(hostname = node)
            answer = connection.getAnswer(IsAliveQuestion())
            if not answer:
                logger.debug("{0} could not be reached! Removing from Idle Nodes.".format(node))
            else:
                onlineList.append(node)
        return onlineList

    def assignRenderJobs(self, renderJobs, idleNodes, allJobs, allNodes, timeouts):
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
                    taskOBJ = hydra_taskboard(job_id = jobID, status = "S",
                                            startTime = datetime.datetime.now(),
                                            host = node,
                                            renderLayer =  renderLayer,
                                            startFrame = startFrame,
                                            endFrame = jobOBJ.endFrame,
                                            currentFrame = startFrame)
                    nodeOBJ.status = STARTED
                    with transaction() as t:
                        taskOBJ.insert(t)
                        nodeOBJ.task_id = taskOBJ.id
                        nodeOBJ.update(t)
                    if jobOBJ.timeout > 1:
                        timeouts[taskOBJ.id] = jobOBJ.timeout
                    result = self.assignTask(nodeOBJ, taskOBJ, jobOBJ)
                    #TODO: Handle assigment exceptions

        return timeouts

    def filterTask(self, job, node):
        if job.priority < node.minPriority:
            logger.debug("Skipping job {0} because it does not meet {1}'s minPriority requirement".format(job.id, node.host))
            return False

        if job.failures and job.failures != "":
            failures = job.failures.split(",")
            if node.host in failures:
                logger.debug("Skipping job {0} because it has failed on node {1} in the past".format(job.id, node.host))
                return False

        if job.requirements and job.requirements != "":
            jobReqs = job.requirements.split(",")
            nodeCaps = node.capabilities.split(",")
            checker = [x in nodeCaps for x in jobReqs]
            if not all(checker):
                logger.debug("Skipping job {0} because node {1} cannot meet its feature requirements".format(job.id, node.host))
                return False

        #If all of the above tests pass
        return True


    def getStartFrame(self, jobOBJ, renderLayer):
        renderLayers = jobOBJ.renderLayers.split(",")
        frameList = jobOBJ.renderLayerTracker.split(",")
        idx = renderLayers.index(renderLayer)
        return int(frameList[idx])

    def shutdownCMD(self):
        self.managmentServer.shutdown()

    def assignTask(self, node, task, job):
        logger.debug("Assigning task with id {0} to node {1}".format(task.id, node.host))
        connection = TCPConnection(hostname = node.host)
        response = connection.sendQuestion(StartRenderQuestion(job, task))
        if response:
            logger.debug("Task {0} was accepted on {1}".format(task.id, node.host))
        else:
            logger.error("Task {0} was declined on {1}".format(task.id, node.host))

    def checkOnTimeouts(self, timeouts, lastTimeoutCheck, nowTime):
        logger.debug("Checking on Tasks in progress with timeouts")
        #TODO: See if this works
        if not lastTimeoutCheck:
            lastTimeoutCheck = nowTime
        nowTime = datetime.datetime.now()
        timeDelta = (nowTime - lastTimeoutCheck).total_seconds()
        iterList = [[k,v] for k,v in timeouts.iteritems()]
        for taskID, timeout in iterList:
            task = hydra_taskboard.fetch("WHERE id = %s", (taskID,))
            if task.status != "S":
                timeouts.pop(taskID, None)
            else:
                timeouts[taskID] = timeout - timeDelta
                if timeouts[taskID] < 0:
                    logger.debug("Kill job should go here...")
        return timeouts, lastTimeoutCheck, nowTime

    def killTask(self, node, statusAfterDeath = KILLED):
        logger.debug("Killing task on node: {0}".format(node.host))

    def onlineNode(self, node):
        logger.debug("Onlining node: {0}".format(node.host))

    def offlineNode(self, node):
        logger.debug("Offlining node: {0}".format(node.host))

    def getOffNode(self, node):
        logger.debug("Getting off node: {0}".format(node.host))

    def startTimeoutThread(self, node, timeout):
        logger.debug("Starting timeout thread for node: {0}".format(node.host))

    def updateCurrentFrame(self, node, frame):
        logger.debug("Updating current frame on task {0} to {1}".format(node, frame))
        try:
            thisNode = self.allNodes[node]
        except KeyError:
            logger.error("Could not find node '{0}'!".format(node))
            return False
        with transaction() as t:
            thisTask = hydra_taskboard.fetch("WHERE id = %s", (thisNode.task_id,),
                                                explicitTransaction = t)
            thisTask.currentFrame = frame
            thisTask.update(t)
        return True

def main():
    logger.debug('Starting in {0}'.format(os.getcwd()))
    logger.debug('arglist {0}'.format(sys.argv))
    port = int(getInfoFromCFG("manager", "port"))
    socketServer = RenderManagementServer(port = port)
    socketServer.createIdleLoop(15, socketServer.processRenderTasks)

if __name__ == "__main__":
    main()
