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
    command = """update hydra_taskboard set status = '%s' where job_id = '%d'""" % (new_status, job_id)
    if len(old_status_list) > 0:
        command = command + """ and status = '%s'""" % old_status_list[0]
        for status in old_status_list[1:]:
            command = command + """ or status = '%s'""" % status

    with transaction() as t:
        t.cur.execute(command)

def updateJobTaskCount(job_id, tasks = None):
    """Function for updating the job task count.
    Takes job_id and optional tasks so we don't have to hit the DB server 2x"""
    if tasks == None:
        tasks = hydra_taskboard.fetch("where job_id = %d" % job_id)
    taskCount = len(tasks)
    taskDone = 0
    for task in tasks:
        if task.status == "F":
            taskDone += 1
    with transaction() as t:
        [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
        job.taskDone = taskDone
        job.totalTask = taskCount
        if taskDone == taskCount:
            job.job_status =  "F"
        job.update(t)

    return taskCount, taskDone
