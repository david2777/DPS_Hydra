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

def changeStatusViaTaskID(task_id, new_status, old_status_list = []):
    """Change the status of a task given it's ID.

    Keyword Arguments:
        old_status_list -- A list of stauses subject to change, will change all
            if left as the default. (default [])
    """
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = "UPDATE hydra_taskboard SET status = %s WHERE id = %s"
    commandTuple = (new_status, task_id)
    if len(old_status_list) > 0:
        command += " AND status = %s"
        commandTuple += (old_status_list[0],)
        for status in old_status_list[1:]:
            command += " OR status = %s"
            commandTuple += (status,)

    with transaction() as t:
        t.cur.execute(command, commandTuple)

def startTask(task_id):
    """Start task if it is paused, ressurect task if it is killed/errored."""
    [task] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id,))
    if task.status == READY or task.status == STARTED or task.status == FINISHED:
        logger.info("Passing Task {0} because it is either already started or ready".format(task_id))
    elif task.status == PAUSED or task.status == MANAGED:
        logger.info("Setting paused Task {0} to Ready".format(task_id))
        task.status = READY
        with transaction() as t:
            task.update(t)
    else:
        logger.info("Skipping...")

def resetTask(task_id, newStatus = READY):
    """Reset a task. Returns True if successful, else False.

    Keyword Arguments:
        newStatus -- The status the task should assume after it's been reset. (default READY)
    """
    [task] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id,))
    logger.info("Reseting Task {0}".format(task_id))
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


def unstick(taskID = None, newTaskStatus = READY, host = None, newHostStatus = IDLE):
    """Unstick and rests a task. Useful for when a node crashes."""
    #Not sure why this function has so many optional arguments
    if taskID:
        [task] = hydra_taskboard.secureFetch("WHERE id = %s", (taskID,))
        if newTaskStatus == READY:
            task.host = None
        task.status = newTaskStatus
        task.startTime = None
        task.endTime = None
        if host:
            [host] = hydra_rendernode.secureFetch("WHERE host = %s", (host,))
            host.task_id = None
            host.status = newHostStatus
        with transaction() as t:
            task.update(t)
            if host:
                host.update(t)

def sendKillQuestion(renderhost, newStatus=KILLED):
    """Kill the current task running on the renderhost. Return True if successful,
    else False"""
    logger.info('Kill task on {0}'.format(renderhost))
    connection = TCPConnection(hostname=renderhost)
    answer = connection.getAnswer(KillCurrentTaskQuestion(newStatus))
    if answer == None:
        return False
    logger.info("Child killed: {0}".format(answer.childKilled))
    if not answer.childKilled:
        logger.warning("{0} tried to kill its job but failed for some reason.".format(renderhost))
    #answer.childKilled should be True when successfully killed and False otherwise
    return answer.childKilled

def killTask(task_id, newStatus = KILLED):
    """Kill a task given it's task id. Return True if successful, else False."""
    [task] = hydra_taskboard.secureFetch("WHERE id = %s", (task_id,))
    if task.status == READY or task.status == PAUSED or task.status == MANAGED:
        #Change info in DB if it isn't already running
        task.status = newStatus
        task.host = None
        task.startTime = None
        task.endTime = None
        task.logFile = None
        task.exitCode = None
        with transaction() as t:
            task.update(t)
        return True
    elif task.status == STARTED:
        #Kill if task is in progress
        killed = sendKillQuestion(task.host, newStatus)
        #This is the only way this function could return an error
        return killed
    else:
        #Else, skip it
        logger.info("Task Kill is skipping task {0} because of status {1}".format(task.id, task.status))
        return True
