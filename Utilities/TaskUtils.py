"""A collection of utilities to be run on Tasks (the children of Jobs)"""
#Standard
import datetime

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
from Networking.Questions import KillCurrentTaskQuestion
from Networking.Connections import TCPConnection

def sendKillQuestion(renderhost, newStatus):
    """Kill the current task running on the renderhost. Return True if successful,
    else False"""
    #TODO: Cleanup kill status reporting
    logger.debug('Kill task on {0}'.format(renderhost))
    connection = TCPConnection(hostname = renderhost)
    answer = connection.getAnswer(KillCurrentTaskQuestion(newStatus))
    if answer is None:
        logger.debug("{0} appears to be offline or unresponsive. Treating as dead.".format(renderhost))
    else:
        logger.debug("Child killed: {0}".format(answer.childKilled))
        if answer and not answer.childKilled:
            logger.warning("{0} tried to kill its job but failed for some reason.".format(renderhost))
    return None if answer == None else answer.childKilled

def killTask(task_id, newStatus, TCPKill = True):
    """Kill a task given it's task id. Return True if successful, else False."""
    #TODO: Handle failed kill
    task = hydra_taskboard.fetch("WHERE id = %s", (task_id,),
                                    cols = ["id", "status", "host"])
    if task.status == STARTED:
        if TCPKill:
            killed = sendKillQuestion(task.host, newStatus)
        else:
            killed = True
        task.status = newStatus
        task.endTime = datetime.datetime.now()
        with transaction() as t:
            task.update(t)
        return True
    else:
        logger.debug("Task Kill is skipping task {0} because of status {1}".format(task.id, task.status))
        return True
