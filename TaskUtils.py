"""A collection of utilities to be run on Tasks (the children of Jobs)"""
#Standard
import sys

#3rd party
from MySQLdb import Error as sqlerror

#Hydra
from MySQLSetup import *
from LoggingSetup import logger
from Questions import KillCurrentTaskQuestion
from Connections import TCPConnection
import Utils

def changeStatusViaTaskID(task_id, new_status, old_status_list=[]):
    """Changes the status of a single task given a new status and an optional
    list of old statuses to limit which statuses are to be changed."""
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = "UPDATE hydra_taskboard SET status = '{0}' WHERE id = '{1}'".format(new_status, task_id)
    if len(old_status_list) > 0:
        command += " AND status = '{0}'".format(old_status_list[0])
        for status in old_status_list[1:]:
            command += " OR status = '{0}'".format(status)

    with transaction() as t:
        t.cur.execute(command)

def startTask(task_id):
    """Start task if it is paused, ressurect task if it is killed/errored.
    Pass over task if it is already Ready or Started"""
    with transaction() as t:
        [task] = hydra_taskboard.fetch("WHERE id = '{0}'".format(task_id))
        if task.status == "R" or task.status == "S" or task.status == "F":
            logger.info("Pass Task {0} because it is either already started or ready".format(task_id))
            return None
        elif task.status == "U":
            logger.info("Setting paused Task {0} to Ready".format(task_id))
            task.status = "R"
        else:
            logger.info("Skipping...")

        task.update(t)

def resetTask(task_id, newStatus = "R"):
    """Resets a task and puts it back on the job board with a new status.
    @return: True means there was an error, false means there was not"""
    with transaction() as t:
        [task] = hydra_taskboard.fetch("WHERE id = '{0}'".format(task_id))
        logger.info("Reseting Task {0}".format(task_id))
        if task.status == "S":
            if not killTask(task.id):
                logger.error("Could not kill task, unable to reset!")
                return True
        task.status = newStatus
        task.host = None
        task.startTime = None
        task.endTime = None
        task.logFile = None
        task.exitCode = None
        task.update(t)
    
    return False


def unstick(taskID=None, newTaskStatus=READY, host=None, newHostStatus=IDLE):
    """Unsticks and rests a task. Particularly useful for a node that wakes up
    with a task assinged to it that it has no memory of (like after an
    unexpected shutdown or crash)."""
    with transaction() as t:
        if taskID:
            [task] = hydra_taskboard.fetch("WHERE id = {0}".format(taskID))
            #If the task is marked, say, CRASHED, leave the host name alone.
            #Only READY would be confusing with a host named filled in. I think.
            if newTaskStatus == READY:
                task.host = None

            task.status = newTaskStatus
            task.startTime = None
            task.endTime = None
            task.update(t)
        if host:
            [host] = hydra_rendernode.fetch("WHERE host = '{0}'".format(host))
            host.task_id = None
            host.status = newHostStatus
            host.update(t)

def sendKillQuestion(renderhost, newStatus="K"):
    """Tries to kill the current task running on the renderhost.
    @return True if successful, otherwise False"""
    logger.info('Kill task on {0}'.format(renderhost))
    connection = TCPConnection(hostname=renderhost)
    answer = connection.getAnswer(KillCurrentTaskQuestion(newStatus))
    if answer == None:
        return None
    logger.info("Child killed: {0}".format(answer.childKilled))
    if not answer.childKilled:
        logger.warning("{0} tried to kill its job but failed for some reason.".format(renderhost))
    return answer.childKilled

def killTask(task_id, newStatus = "K"):
    """Kills the task with the specified id. If the task has been started, a
    kill request is sent to the node running it.
    @return: True if there were any errors, False if there were not."""
    [task] = hydra_taskboard.fetch("WHERE id = '{0}'".format(task_id))
    if task.status == newStatus:
        return False
    elif task.status == "R" or task.status == "U":
        task.status = newStatus
        with transaction() as t:
            task.update(t)
        #If we reach this point: transaction successful, no exception raised
        return False
    elif task.status == "S":
        killed = sendKillQuestion(task.host, newStatus)
        #If we reach this point: TCPconnection successful, no exception raised
        return killed
    elif task.status == "K" or task.status == "F":
        return False
    return True
