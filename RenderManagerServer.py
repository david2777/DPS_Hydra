#Standard
import os
import sys
import datetime
from operator import attrgetter

#Hydra
import Constants
from Setups.LoggingSetup import logger
from Networking.Servers import TCPServer
from Networking.Questions import IsAliveQuestion, StartRenderQuestion
from Networking.Connections import TCPConnection
from Utilities.JobUtils import updateJobTaskCount
from Utilities.Utils import getInfoFromCFG
from Setups.MySQLSetup import *

class RenderManagementServer(TCPServer):
    def __init__(self, *arglist, **kwargs):
        self.managmentServer = TCPServer.__init__(self, *arglist, **kwargs)

        self.allJobs = {}
        self.allTasks = {}
        self.renderTasks = []
        self.allNodes = {}
        self.idleNodes = []
        self.timeouts = {}
        self.nowTime = datetime.datetime.now()
        self.lastTimeoutCheck = None

    def processRenderTasks(self):
        logger.debug("Processing Render Tasks")
        #Fetch all Jobs
        jobList = hydra_jobboard.fetch("WHERE archived = 0", multiReturn = True)
        self.allJobs = {x.id : x for x in jobList}

        #Fetch all Tasks and sort them
        idStr = ",".join(str(x) for x in self.allJobs.keys())
        query = "WHERE status = 'R'"
        if idStr != "":
            query += " AND job_id IN ({0})".format(idStr)
        else:
            logger.info("There appears to be no active jobs in the jobboard!")
            #Giving it an impossible query, job_ids start at 1
            query += " AND job_id = '0'"
        taskList = hydra_taskboard.fetch(query, multiReturn = True)
        self.allTasks = {x.id : x for x in taskList}
        self.renderTasks = self.createRenderTasks()

        #Fetch all Nodes and find out which ones are online
        nodeList = hydra_rendernode.fetch(multiReturn = True)
        self.allNodes = {str(x.host) : x for x in nodeList}
        self.idleNodes = [k for k,v in self.allNodes.iteritems() if v.status == IDLE]
        self.idleNodes = self.checkNodeStatus()

        #Assign Tasks to Nodes
        self.assignRenderTasks()

        #Check on timeouts
        self.checkOnTimeouts()

        #Done! Wait to loop through again.
        logger.debug("End of loop. Waiting...")

    def createRenderTasks(self):
        logger.debug("Creating Render Tasks")
        #TODO: Advanced sorting for things like every x frame
        sortedTasks = sorted(self.allTasks.values(), key = attrgetter("priority"), reverse = True)
        sorted(sortedTasks, key = attrgetter("id"))
        return [x.id for x in sortedTasks]

    def checkNodeStatus(self):
        logger.debug("Checking Node Status on Idle Nodes")
        onlineList = []
        for node in self.idleNodes:
            connection = TCPConnection(hostname = node)
            answer = connection.getAnswer(IsAliveQuestion())
            if not answer:
                logger.debug("{0} could not be reached! Removing from Idle Nodes.".format(node))
            else:
                onlineList.append(node)
        return onlineList

    def assignRenderTasks(self):
        if len(self.renderTasks) < 1 or len(self.idleNodes) < 1:
            logger.debug("No Idle Nodes or Ready Tasks found. Skipping assignment...")
            return True
        logger.debug("Assigning Render Tasks")
        resultList = []
        i = 0
        for node in self.idleNodes:
            for task in self.renderTasks:
                taskOBJ = self.allTasks[task]
                jobOBJ = self.allJobs[taskOBJ.job_id]
                nodeOBJ = self.allNodes[node]
                response = self.filterTask(taskOBJ, jobOBJ, nodeOBJ)
                if response:
                    nodeOBJ.status = STARTED
                    nodeOBJ.task_id = taskOBJ.id
                    taskOBJ.status = STARTED
                    taskOBJ.host = nodeOBJ.host
                    taskOBJ.startTime = datetime.datetime.now()
                    taskOBJ.logFile = os.path.join(Constants.RENDERLOGDIR,
                                                    '{:0>10}.log.txt'.format(taskOBJ.id))
                    with transaction() as t:
                        nodeOBJ.update(t)
                        taskOBJ.update(t)
                    updateJobTaskCount(taskOBJ.job_id)
                    if jobOBJ.timeout > 1:
                        self.timeouts[taskOBJ.id] = jobOBJ.timeout
                    result = self.assignTask(nodeOBJ, taskOBJ, jobOBJ)
                    resultList.append(result)
                    self.renderTasks.remove(task)
                    break
        return all(resultList)

    def filterTask(self, task, job, node):
        returnList = []
        #Check min priority
        returnList.append(int(task.priority) >= int(node.minPriority))
        logger.debug([int(task.priority), int(node.minPriority)])
        #TODO:Check failures
        return all(returnList)

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

    def checkOnTimeouts(self):
        logger.debug("Checking on Tasks in progress with timeouts")
        #TODO:See if this works
        if not self.lastTimeoutCheck:
            self.lastTimeoutCheck = self.nowTime
        self.nowTime = datetime.datetime.now()
        timeDelta = (self.nowTime - self.lastTimeoutCheck).total_seconds()
        for taskID, timeout in self.timeouts.iteritems():
            task = hydra_taskboard.fetch("WHERE id = %s", (taskID,))
            if task.status != "S":
                self.timeouts.pop(taskID, None)
            else:
                self.timeouts[taskID] = timeout - timeDelta
                if self.timeouts[taskID] < 0:
                    logger.debug("Kill job should go here...")

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
