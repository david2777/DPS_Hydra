#Standard
import os
import sys

#Hydra
from Setups.LoggingSetup import logger
from Networking.Servers import TCPServer
from Networking.Questions import IsAliveQuestion
from Networking.Connections import TCPConnection
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
        self.allJobs = hydra_jobboard.fetch("WHERE archived = 0")

        taskList = hydra_taskboard.fetch("WHERE archived = 0 AND status = 'R'")
        self.allTasks = {int(x.id) : x for x in taskList}
        self.createRenderTasks()

        nodeList = hydra_rendernode.fetch()
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
            localTasks = self.renderTasks
            for task in localTasks:
                taskOBJ = self.allTasks[task]
                nodeOBJ = self.allNodes[node]
                jobOBJ = self.allJobs[taskOBJ.job_id]
                #TODO:Check to make sure all reqs and stuff are met
                if True:
                    result = self.assignTask(nodeOBJ, taskOBJ)
                    resultList.append(result)
                    localTasks.remove(task)
                    break
            i += 1
        return all(resultList)

    def shutdownCMD(self):
        self.managmentServer.shutdown()

    def assignTask(self, node, task):
        logger.info("Assigning task with id {0} to node {1}".format(task.id, node.host))
        return True

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
    socketServer = RenderManagementServer()
    socketServer.createIdleLoop(15, socketServer.processRenderTasks)

if __name__ == "__main__":
    main()
