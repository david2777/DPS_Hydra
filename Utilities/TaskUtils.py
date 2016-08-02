"""A collection of utilities to be run on Tasks (the children of Jobs)"""
#Standard
import sys

#Third Party
from MySQLdb import Error as sqlerror

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
from Networking.Questions import KillCurrentTaskQuestion
from Networking.Connections import TCPConnection
import Utilities.Utils as Utils

def startTask(task_id):
    """Start task if it is paused, ressurect task if it is killed/errored."""
    task = hydra_taskboard.fetch("WHERE id = %s", (task_id,), cols = ["status", "id"])
    if task.status in [PAUSED, MANAGED, KILLED]:
        logger.debug("Starting Task {0}".format(task_id))
        task.status = READY
        with transaction() as t:
            task.update(t)

def resetTask(task_id, newStatus = READY):
    """Reset a task. Returns True if successful, else False.

    Keyword Arguments:
        newStatus -- The status the task should assume after it's been reset. (default READY)
    """
    task = hydra_taskboard.fetch("WHERE id = %s", (task_id,),
                                    cols = ["status", "host", "startTime",
                                            "endTime", "logFile", "exitCode", "id"])
    logger.debug("Reseting Task {0}".format(task_id))
    if task.status == STARTED:
        if not killTask(task.id):
            logger.error("Could not kill task {0}, unable to reset!".format(task_id))
            return False
    task.status = newStatus
    task.host = None
    task.startTime = None
    task.endTime = None
    task.logFile = None
    task.exitCode = None
    with transaction() as t:
        task.update(t)
    return True

def sendKillQuestion(renderhost, newStatus=KILLED):
    """Kill the current task running on the renderhost. Return True if successful,
    else False"""
    logger.debug('Kill task on {0}'.format(renderhost))
    connection = TCPConnection(hostname=renderhost)
    answer = connection.getAnswer(KillCurrentTaskQuestion(newStatus))
    if answer is None:
        logger.debug("{0} appears to be offline or unresponsive. Treating as dead.".format(renderhost))
    else:
        logger.debug("Child killed: {0}".format(answer.childKilled))
        if answer and not answer.childKilled:
            logger.warning("{0} tried to kill its job but failed for some reason.".format(renderhost))
    return None if answer == None else answer.childKilled

def killTask(task_id, newStatus = KILLED):
    """Kill a task given it's task id. Return True if successful, else False."""
    task = hydra_taskboard.fetch("WHERE id = %s", (task_id,),
                                    cols = ["status", "startTime", "endTime",
                                            "exitCode", "host", "id"])
    if task.status == READY or task.status == PAUSED or task.status == MANAGED:
        task.status = newStatus
        task.startTime = None
        task.endTime = None
        task.exitCode = None
        with transaction() as t:
            task.update(t)
        return True
    elif task.status == STARTED:
        #Kill if task is in progress
        killed = sendKillQuestion(task.host, newStatus)
        if killed is None:
            task.status = newStatus
            task.startTime = None
            task.endTime = None
            task.exitCode = None
            with transaction() as t:
                task.update(t)
            return True
        else:
            return killed
    else:
        logger.debug("Task Kill is skipping task {0} because of status {1}".format(task.id, task.status))
        return True
