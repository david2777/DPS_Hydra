"""A collection of utilities to be run on Jobs (the parent of an individual task)"""
#Standard
import sys
from socket import error as socketerror

#Third Party
from MySQLdb import Error as sqlerror

#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
import Utilities.Utils as Utils
import Utilities.TaskUtils as TaskUtils

def updateJobTaskCount(job_id, tasks = None, commit = True):
    """Update the task count and status of a job. Return the task count and
    number of complete tasks.

    Keyword Arguments:
        tasks -- For passing a list of the task objs to avoid querying the DB (default None)
        commit -- If False the results will not be commited to databse (default True)
    """
    if not tasks:
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                        multiReturn = True, cols = ["id", "status"])
    taskCount = len(tasks)
    statusList = [task.status for task in tasks]
    errorList = [ERROR, CRASHED, TIMEOUT]

    tasksComplete = statusList.count(FINISHED)
    if any([s in statusList for s in errorList]):
        jobStatus = ERROR
    elif tasksComplete == taskCount:
        jobStatus = FINISHED
    elif STARTED in statusList:
        jobStatus = STARTED
    elif READY in statusList:
        jobStatus = READY
    elif KILLED in statusList:
        jobStatus = KILLED
    else:
        jobStatus = PAUSED

    if commit:
        command = "UPDATE hydra_jobboard SET tasksComplete = %s, tasksTotal = %s, job_status = %s WHERE id = %s"
        commandTuple = (tasksComplete, taskCount, jobStatus, job_id)
        with transaction() as t:
            t.cur.execute(command, commandTuple)

    return taskCount, tasksComplete


def startJob(job_id):
    """Start every subtask of a job."""
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                    multiReturn = True,
                                    cols = ["id", "status"])
    map(TaskUtils.startTask, [task.id for task in tasks])
    setupNodeLimit(job_id)
    updateJobTaskCount(job_id, tasks)

def killJob(job_id, newStatus = KILLED):
    """Kill every subtask of a job. Return True if successful, else False.

    Keyword Arguments:
        newStatus -- The status each task should assume after it's death. (default KILLED)
    """
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                    multiReturn = True, cols = ["id", "status"])
    if tasks:
        responses = [TaskUtils.killTask(task.id, newStatus) for task in tasks]
        updateJobTaskCount(job_id, tasks)
        return False if False in responses else True
    else:
        return True

def resetJob(job_id, newStatus = READY):
    """Reset every subtask of a job. Return True if successful, else False.

    Keyword Arguments:
        newStatus -- The status each task should assume after it's been reset. (default READY)
    """
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                    multiReturn = True, cols = ["id", "job_id", "status"])
    responses = [TaskUtils.resetTask(task.id, newStatus) for task in tasks]
    updateJobTaskCount(job_id, tasks)
    return False if False in responses else True

def prioritizeJob(job_id, priority):
    """Update the priority of a job and all of it's subtasks"""
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET priority = %s WHERE id = %s", (priority, job_id))
        t.cur.execute("UPDATE hydra_taskboard SET priority = %s WHERE job_id = %s", (priority, job_id))

def setupNodeLimit(job_id, hold_status = MANAGED):
    """Start the maximum number of concurant tasks allowed for a job. Pause the remainder.

    Keyword Arguments:
        hold_status -- The status of the remainder (paused) tasks. (default MANAGED)
    """
    job = hydra_jobboard.fetch("WHERE id = %s", (job_id,), cols = ["maxNodes", "id"])
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                    multiReturn = True, cols = ["id"])
    startTasks = tasks[0:taskLimit]
    startTasks = [int(task.id) for task in startTasks]
    holdTasks = tasks[taskLimit:]

    map(TaskUtils.startTask, startTasks)

    with transaction() as t:
        for task in holdTasks:
            t.cur.execute("UPDATE hydra_taskboard SET status = %s WHERE id = %s AND status = %s", (hold_status, task.id, READY))

def manageNodeLimit(job_id, hold_status = MANAGED):
    """Start managed tasks if the number of started tasks is below the concurant task limit.

    Keyword Arguments:
        hold_status -- The status of the remainder (paused) tasks. (default MANAGED)
    """
    job = hydra_jobboard.fetch("WHERE id = %s", (job_id,), cols = ["maxNodes", "id"])
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,),
                                    multiReturn = True, cols = ["status", "id"])
    startList = []

    for task in tasks:
        if task.status == STARTED or task.status == READY:
            taskLimit -= 1
        elif task.status == hold_status:
            startList.append(task.id)
    if taskLimit > 0:
        for task_id in startList[0:taskLimit]:
            TaskUtils.startTask(task_id)

    logger.debug("Node Limit managed on Job: {0}".format(job_id))
