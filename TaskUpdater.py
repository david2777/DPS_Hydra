#Standard
import sys

#Hydra
from hydra.logging_setup import logger
import networking.questions as questions
import networking.connections as connections
import utils.hydra_utils as hydra_utils

#TODO:Needs BuildScript

def main():
    args = sys.argv
    if len(args) < 2:
        logger.error("Not enough arguments given!")
        return None

    managerPort = int(hydra_utils.getInfoFromCFG("manager", "port"))
    managerAddress = str(hydra_utils.getInfoFromCFG("manager", "host"))

    updateType = str(args[1])
    data = {}
    if updateType == "TaskProgress" or updateType == "tp":
        if len(args) < 4:
            logger.error("Not enough arguments given!")
            return None
        data["thisNode"] = hydra_utils.myHostName()
        data["currentFrame"] = int(args[2])
        data["renderLayer"] = str(args[3])

        conn = connections.TCPConnection(managerAddress, managerPort)
        question = questions.ProgressUpdateQuestion("TaskProgress", data)
        response = conn.get_answer(question)
        if not response:
            logger.critical("An error occured while sending the update data to the manager!")
        return response
    else:
        logger.error("Bad update type given!")
        return None

if __name__ == "__main__":
    main()
    #raw_input()
