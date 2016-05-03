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
    """Function for updating the status of every task under a Job as well as the
    status of the job itself. Changes the status given a job_id, new status,
    and an optional list of old statuses to limit which statues can be changed."""
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

def updateJobTaskCount(job_id, tasks = None, commit = False):
    """Function for updating the job task count.
    Takes job_id and optional tasks so we don't have to hit the DB server 2x
    @return Total tasks and total complete tasks as intigers"""
    if not tasks:
        tasks = hydra_taskboard.fetch("WHERE job_id = '{0}'".format(job_id))
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
    """Start every task associated with a specified job if it is paused,
    ressurect task if it is killed/errored."""
    tasks = hydra_taskboard.fetch("WHERE job_id = '{0}'".format(job_id))
    map(TaskUtils.startTask, [task.id for task in tasks])
    updateJobTaskCount(job_id, tasks)

def killJob(job_id, newStatus = KILLED):
    """Kills every task associated with job_id. Killed tasks have status code
    set by newStatus. If a task was already started, an a kill request
    is sent to the host running it.
    @return: False if no errors while killing started tasks, else True"""
    tasks =  hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id,))
    if tasks:
        responses = [TaskUtils.killTask(task.id, newStatus) for task in tasks]
        updateJobTaskCount(job_id, tasks)
        return True if True in responses else False
    else:
        return False

def resetJob(job_id, newStatus = READY):
    """Resets every task associated with job_id. Reset jobs have the status code
    set by newStatus.
    @return: True means there was an error, false means there were not
    any errors."""
    tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id,))
    responses = [TaskUtils.resetTask(task.id, newStatus) for task in tasks]
    updateJobTaskCount(job_id, tasks)
    return True if True in responses else False

def prioritizeJob(job_id, priority):
    """Update a the priority for a job AND all of it's tasks"""
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET priority = %s WHERE id = %s", (priority, job_id))
        t.cur.execute("UPDATE hydra_taskboard SET priority = %s WHERE job_id = %s", (priority, job_id))

def setupNodeLimit(job_id, hold_status = MANAGED):
    """A function for setting up the node limit on a job. The node limiting system
    works by pausing tasks beyond the count of the limit. Ie if the limit is 3
    nodes then the job will only have a maxiumum of 3 tasks ready or started
    at a time. manageNodeLimit is run after every task and will ready a new task
    if applicable."""
    [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id,))
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id,))
    startTasks = tasks[0:taskLimit]
    holdTasks = tasks[taskLimit:]

    map(TaskUtils.startTask, startTasks)

    with transaction() as t:
        for task in holdTasks:
            t.cur.execute("UPDATE hydra_taskboard SET status = %s WHERE id = %s AND status = %s", (hold_status, task.id, READY))

def manageNodeLimit(job_id, hold_status = MANAGED):
    """The counterpart to setupNodeLimit. This is run by RenderNodeMain after
    every task. For more info see setupNodeLimit doc string."""
    [job] = hydra_jobboard.secureFetch("WHERE id = %s", (job_id,))
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return

    tasks = hydra_taskboard.secureFetch("WHERE job_id = %s", (job_id,))
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
