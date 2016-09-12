#Standard
import sys

#Hydra
from Constants import FRAMELOGPATH
from Setups.LoggingSetup import logger
from Networking.Questions import updateCurrentFrameQuestion
from Networking.Connections import TCPConnection
from Utilities.Utils import getInfoFromCFG, myHostName

def main(frame):
    #Update DB
    renderManagerHost = getInfoFromCFG("manager", "host")
    renderManagerPort = getInfoFromCFG("manager", "port")
    domain = getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
    if domain != "" and renderManagerHost != "localhost":
        renderManagerHost += ".{}".format(domain)
    node = myHostName()
    connection = TCPConnection(renderManagerHost, int(renderManagerPort))
    answer = connection.getAnswer(updateCurrentFrameQuestion(node, frame))
    #Interperate Response
    if not answer:
        logger.critical("Frame {0} was not updated successfully on ManagerServer due to a connection failure".format(frame))
        retcode = 11
    elif answer == 22:
        logger.critical("Frame {0} was not updated successfully on ManagerServer because RenderManagementServer could not find {1} in the database".format(frame, node))
        retcode = answer
    elif answer == 33:
        logger.critical("Frame {0} was not updated successfully on ManagerServer because RenderManagementServer could not find a task for {1}".format(frame, node))
        retcode = answer
    else:
        logger.debug("Frame updated successfully on ManagerServer")
        retcode = 0

    #Write to local log file
    try:
        with open(FRAMELOGPATH, "w") as f:
            f.write(str(frame))
    except IOError:
        logger.critical("IO Error while trying to open FRAMELOGPATH")
        if retcode == 0:
            return 211
        else:
            return int("2110" + str(retcode))
    return retcode


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
