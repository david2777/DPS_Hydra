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
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = """update hydra_taskboard set status = '%s' where id = '%d'""" % (new_status, task_id)
    if len(old_status_list) > 0:
        command = command + """ and status = '%s'""" % old_status_list[0]
        for status in old_status_list[1:]:
            command = command + """ or status = '%s'""" % status

    with transaction() as t:
        t.cur.execute(command)

def startTask(task_id):
    """Start task if it is paused, ressurect task if it is killed/errored.
    Pass over task if it is already Ready or Started"""
    with transaction() as t:
        [task] = hydra_taskboard.fetch("where id = '%d'" % task_id)
        if task.status == "R" or task.status == "S" or task.status == "F":
            logger.info("Pass Task %d because it is either already started or ready" % task_id)
            return None
        elif task.status == "U":
            logger.info("Setting paused Task %d to Ready" % task_id)
            task.status = "R"
        else:
            resetTask(task_id, "R")

        task.update(t)
        
def resetTask(task_id, newStatus = "U"):
    """Resets a task and puts it back on the job board with a new status."""
    with transaction() as t:
        [task] = hydra_taskboard.fetch("where id = '%d'" % task_id)
        logger.info("Reseting Task %d" % task_id)
        task.status = newStatus
        task.host = None
        task.startTime = None
        task.endTime = None
        
        task.update(t)
        

def unstick(taskID=None, newTaskStatus=READY, host=None, newHostStatus=IDLE):
    with transaction() as t:
        if taskID:
            [task] = hydra_taskboard.fetch("where id = %d" % taskID)
            #If the task is marked, say, CRASHED, leave the host name alone.
            #Only READY would be confusing with a host named filled in. I think.
            if newTaskStatus == READY:
                task.host = None

            task.status = newTaskStatus
            task.startTime = None
            task.endTime = None
            task.update(t)
        if host:
            [host] = hydra_rendernode.fetch("where host = '%s'" % host)
            host.task_id = None
            host.status = newHostStatus
            host.update(t)

def sendKillQuestion(renderhost, newStatus="K"):
    """Tries to kill the current task running on the renderhost. Returns True if successful, otherwise False"""
    logger.debug ('kill job on %s' % renderhost)
    connection = TCPConnection(hostname=renderhost)
    answer = connection.getAnswer(KillCurrentTaskQuestion(newStatus))
    if answer == None:
        return None
    logger.debug("child killed: %s" % answer.childKilled)
    if not answer.childKilled:
        logger.debug("%r tried to kill its job but failed for some reason." % renderhost)
    return answer.childKilled

def killTask(task_id):
    """Kills the task with the specified id. If the task has been started, a
    kill request is sent to the node running it.
    @return: True if there were no errors killing the task, else False."""
    [task] = hydra_taskboard.fetch("where id = '%d'" % task_id)
    if task.status == "R" or task.status == "U":
        task.status = "K"
        with transaction() as t:
            task.update(t)
        #If we reach this point: transaction successful, no exception raised
        return True
    elif task.status == "S":
        killed = sendKillQuestion(renderhost = task.host)
        #If we reach this point: TCPconnection successful, no exception raised
        return killed
    elif task.status == "K" or task.status == "F":
        return True
    return False
