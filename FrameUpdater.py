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
    if answer:
        logger.debug("Frame updated successfully")
    else:
        logger.error("Frame {0} was not updated successfully on node {1}".format(frame, node))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("Must pass frame number via command line!")
        sys.exit(1)
    frame = sys.argv[1]
    try:
        frame = int(frame)
    except ValueError:
        logger.error("Frame must be an int!")
        sys.exit(1)
    main(frame)
