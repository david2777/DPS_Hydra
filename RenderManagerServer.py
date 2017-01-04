from __future__ import division
#Standard
import os
import sys

#Hydra
import hydra.hydra_sql as sql
from hydra.logging_setup import logger
from hydra.single_instance import InstanceLock
from networking.servers import TCPServer
#from networking.connections import TCPConnection
from utils.hydra_utils import getInfoFromCFG

class RenderManagementServer(TCPServer):
    def __init__(self):
        port = int(getInfoFromCFG("manager", "port"))
        self.startServerThread(port)

    @staticmethod
    def processRenderTasks():
        logger.debug("Processing Render Tasks")
        allNodesList = sql.hydra_rendernode.fetch()
        logger.debug(allNodesList)

def main():
    logger.info("starting in %s", os.getcwd())
    logger.info("arglist is %s", sys.argv)

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
                                interval=5)

if __name__ == "__main__":
    main()
