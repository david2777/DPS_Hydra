#Standard
import sys

#3rd party
from MySQLdb import Error as sqlerror

#Hydra
from MySQLSetup import *
from LoggingSetup import logger
import Utils


def changeStatusViaJobID(job_id, new_status, old_status_list=[]):
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = """update hydra_rendertask set status = '%s' where job_id = '%d'""" % (new_status, job_id)
    if len(old_status_list) > 0:
        command = command + """ and status = '%s'""" % old_status_list[0]
        for status in old_status_list[1:]:
            command = command + """ or status = '%s'""" % status

    with transaction() as t:
        t.cur.execute(command)


def changeStatusViaTaskID(task_id, new_status, old_status_list=[]):
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = """update hydra_rendertask set status = '%s' where id = '%d'""" % (new_status, task_id)
    if len(old_status_list) > 0:
        command = command + """ and status = '%s'""" % old_status_list[0]
        for status in old_status_list[1:]:
            command = command + """ or status = '%s'""" % status

    with transaction() as t:
        t.cur.execute(command)

def unstick(taskID=None, newTaskStatus=READY, host=None, newHostStatus=IDLE):
    with transaction () as t:
        if taskID:
            [task] = hydra_rendertask.fetch("where id = %d" % taskID)
            #If the task is marked, say, CRASHED, leave the host name alone.
            #Only READY would be confusing with a host named filled in. I think.
            if newTaskStatus == READY:
                task.host = None

            task.status = newTaskStatus
            task.startTime = None
            task.endTime = None
            task.update (t)
        if host:
            [host] = hydra_rendernode.fetch ("where host = '%s'" % host)
            host.task_id = None
            host.status = newHostStatus
            host.update (t)

def updateJobTaskCount(job_id, tasks = None):
    if tasks == None:
        tasks = hydra_taskboard.fetch("where job_id = %d" % job_id)
    taskCount = len(tasks)
    taskDone = 0
    for task in tasks:
        if task.status == "F":
            taskDone += 1
    #TODO: Update DB, change Job Status
    return taskCount, taskDone
