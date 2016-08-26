#Standard
import sys

#Hydra
from Setups.LoggingSetup import logger
from Networking.Questions import updateCurrentFrameQuestion
from Networking.Connections import TCPConnection
from Utilities.Utils import getInfoFromCFG, myHostName

def main(frame):
    renderManagerHost = getInfoFromCFG("manager", "host")
    renderManagerPort = getInfoFromCFG("manager", "port")
    node = myHostName()
    connection = TCPConnection(renderManagerHost, int(renderManagerPort))
    answer = connection.getAnswer(updateCurrentFrameQuestion(node, frame))
    if not answer:
        logger.critical("Frame {0} was not updated successfully on ManagerServer due to a connection failure".format(frame))
        return 11
    elif answer == 22:
        logger.critical("Frame {0} was not updated successfully on ManagerServer because RenderManagementServer could not find {1} in the database".format(frame, node))
        return answer
    elif answer == 33:
        logger.critical("Frame {0} was not updated successfully on ManagerServer because RenderManagementServer could not find a task for {1}".format(frame, node))
        return answer
    else:
        logger.debug("Frame updated successfully on ManagerServer")
        return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Must pass frame number via command line!")
        sys.exit(88)
    frame = sys.argv[1]
    try:
        frame = int(frame)
    except ValueError:
        logger.error("Frame must be a number!")
        sys.exit(99)

    exitCode = main(frame)
    sys.exit(exitCode)
