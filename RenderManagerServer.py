#Standard
import os
import sys
import datetime

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

    def processRenderTasks(self):
        logger.info("Processing Render Tasks")
        self.allJobs = hydra_jobboard.fetch("WHERE archived = 0", multiReturn = True)

        taskList = hydra_taskboard.fetch("WHERE archived = 0 AND status = 'R'",
                                            multiReturn = True)
        self.allTasks = {int(x.id) : x for x in taskList}
        self.createRenderTasks()

        nodeList = hydra_rendernode.fetch(multiReturn = True)
        self.allNodes = {str(x.host) : x for x in nodeList}
        self.idleNodes = [k for k,v in self.allNodes.iteritems() if v.status == IDLE]
        self.checkNodeStatus()

        result = self.assignRenderTasks()

    def createRenderTasks(self):
        logger.info("Creating Render Tasks")
        #TODO:Sorting!
        self.renderTasks = [x for x in self.allTasks.keys()]

    def checkNodeStatus(self):
        logger.info("Checking Node Status on Idle Nodes")
        for node in self.idleNodes:
            connection = TCPConnection(hostname = node)
            answer = connection.getAnswer(IsAliveQuestion())
            if not answer:
                logger.debug("{0} could not be reached! Removing from Idle Nodes.".format(node))
                self.idleNodes.remove(node)

    def assignRenderTasks(self):
        logger.info("Assigning Render Tasks")
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
                    taskOBJ.logFile = os.path.join(Constants.RENDERLOGDIR, '{:0>10}.log.txt'.format(taskOBJ.id))
                    with transaction() as t:
                        nodeOBJ.update(t)
                        taskOBJ.update(t)
                    updateJobTaskCount(taskOBJ.job_id)
                    result = self.assignTask(nodeOBJ, taskOBJ, jobOBJ)
                    resultList.append(result)
                    self.renderTasks.remove(task)
                    break
        return all(resultList)

    def filterTask(self, task, job, node):
        returnList = []
        #Check reqs
        taskReqs = task.requirements.split("%")[1:-1]
        taskReqs = [x for x in taskReqs if x != ""]
        returnList += [x in node.capabilities.split(" ") for x in taskReqs]
        logger.info(returnList)
        logger.info(node.capabilities.split(" "))
        logger.info(task.requirements.split("%")[1:-1])
        #Check min priority
        returnList.append(int(task.priority) >= int(node.minPriority))
        logger.info([int(task.priority), int(node.minPriority)])
        #TODO:Check failures
        return all(returnList)

    def shutdownCMD(self):
        self.managmentServer.shutdown()

    def assignTask(self, node, task, job):
        logger.info("Assigning task with id {0} to node {1}".format(task.id, node.host))
        connection = TCPConnection(hostname = node.host)
        response = connection.sendQuestion(StartRenderQuestion(job, task))
        if response:
            logger.info("Task {0} was accepted on {1}".format(task.id, node.host))
        else:
            logger.error("Task {0} was declined on {1}".format(task.id, node.host))

    def killTask(self, node, statusAfterDeath = KILLED):
        logger.info("Killing task on node: {0}".format(node.host))

    def onlineNode(self, node):
        logger.info("Onlining node: {0}".format(node.host))

    def offlineNode(self, node):
        logger.info("Offlining node: {0}".format(node.host))

    def getOffNode(self, node):
        logger.info("Getting off node: {0}".format(node.host))

    def startTimeoutThread(self, node, timeout):
        logger.info("Starting timeout thread for node: {0}".format(node.host))

def main():
    logger.debug('Starting in {0}'.format(os.getcwd()))
    logger.debug('arglist {0}'.format(sys.argv))
    port = int(getInfoFromCFG("manager", "port"))
    socketServer = RenderManagementServer(port = port)
    socketServer.createIdleLoop(15, socketServer.processRenderTasks)

if __name__ == "__main__":
    main()
