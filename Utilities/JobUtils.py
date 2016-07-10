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

def changeStatusViaJobID(job_id, new_status, old_status_list=[]):
    """Change all task's status for a given job id.

    Keyword Arguments:
        old_status_list -- A list of stauses subject to change, will change all
            if left as the default. (default [])
    """
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = "UPDATE hydra_taskboard SET status = %s WHERE job_id = %s"
    commandTuple = (new_status, job_id)
    if len(old_status_list) > 0:
        command += " AND status = %s"
        commandTuple += (old_status_list[0],)
        for status in old_status_list[1:]:
            command += " OR status = %s"
            commandTuple += (status,)
    with transaction() as t:
        t.cur.execute(command, commandTuple)

    updateJobTaskCount(job_id, tasks = None, commit = True)

def updateJobTaskCount(job_id, tasks = None, commit = True):
    """Update the task count and status of a job. Return the task count and
    number of complete tasks.

    Keyword Arguments:
        tasks -- For passing a list of the task objs to avoid querying the DB (default None)
        commit -- If False the results will not be commited to databse (default True)
    """
    if not tasks:
        tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
    taskCount = len(tasks)
    tasksComplete = 0
    error = False
    killed = False
    started = False
    ready = False
    for task in tasks:
        if task.status == FINISHED:
            tasksComplete += 1
        elif task.status == ERROR or task.status == CRASHED or task.status == TIMEOUT:
            error = True
        elif task.status == STARTED:
            started = True
        elif task.status == READY:
            ready = True
        elif task.status == KILLED:
            killed = True
    #If there is an error on any, mark job as error
    #Else, If total done == total tasks, mark job as done
    #Else, If there are any killed tasks, mark job as killed
    #Else, If there are any tasks started, mark job as started
    #Else, If there are any tasks marked as ready, mark job as ready
    #Else, mark as paused (I think that covers all of our bases)
    if error:
        jobStatus = ERROR
    elif tasksComplete == taskCount:
        jobStatus = FINISHED
    elif killed:
        jobStatus = KILLED
    elif started:
        jobStatus = STARTED
    elif ready:
        jobStatus = READY
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
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
    map(TaskUtils.startTask, [task.id for task in tasks])
    updateJobTaskCount(job_id, tasks)

def killJob(job_id, newStatus = KILLED):
    """Kill every subtask of a job. Return True if successful, else False.

    Keyword Arguments:
        newStatus -- The status each task should assume after it's death. (default KILLED)
    """
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
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
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
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
    job = hydra_jobboard.fetch("WHERE id = %s", (job_id,))
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
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
    job = hydra_jobboard.fetch("WHERE id = %s", (job_id,))
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (job_id,), multiReturn = True)
    startList = []

    for task in tasks:
        if task.status == STARTED or task.status == READY:
            taskLimit -= 1
        elif task.status == hold_status:
            startList.append(task.id)
    if taskLimit > 0:
        for task_id in startList[0:taskLimit]:
            TaskUtils.startTask(task_id)

    logger.info("Node Limit managed on Job: {0}".format(job_id))
