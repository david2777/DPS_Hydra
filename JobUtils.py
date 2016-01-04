#Standard
import sys
from socket import error as socketerror

#3rd party
from MySQLdb import Error as sqlerror

#Hydra
from MySQLSetup import *
from LoggingSetup import logger
import Utils
import TaskUtils

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
    error = 0
    killed = 0
    started = 0
    ready = 0
    for task in tasks:
        if task.status == "F":
            taskDone += 1
        elif task.status == "E" or task.status == "C":
            error = 1
        elif task.status == "S":
            started = 1
        elif task.status == "R":
            ready = 1
        elif task.status == "K":
            killed = 1
    #If there is an error on any, mark job as error
    #Else, If total done == total tasks, mark job as done
    #Else, If there are any killed tasks, mark job as killed
    #Else, If there are any tasks started, mark job as started
    #Else, If there are any tasks marked as ready, mark job as ready 
    #Else, mark as paused (I think that covers all of our bases)
    if error == 1:
        jobStatus = "E"
    elif taskDone == taskCount:
        jobStatus = "F"
    elif killed == 1:
        jobStatus = "K"
    elif started == 1:
        jobStatus = "S"
    elif ready == 1:
        jobStatus = "R"
    else:
        jobStatus = "U"
    
    with transaction() as t:
        [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
        job.taskDone = taskDone
        job.totalTask = taskCount
        job.job_status = jobStatus
        job.update(t)

    return taskCount, taskDone


def startJob(job_id):
    """Start job if it is paused, ressurect task if it is killed/errored."""
    tasks = hydra_taskboard.fetch("where job_id = '%d'" % job_id)
    for task in tasks:
        TaskUtils.startTask(task.id)
    with transaction() as t:
        [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
        job.job_status = "R"
        job.update(t)

def killJob(job_id, newStatus = "K"):
    """Kills every task associated with job_id. Killed tasks have status code
    set by newStatus. If a task was already started, an a kill request
    is sent to the host running it.
    @return: False if no errors while killing started tasks, else True"""
    tasks =  hydra_taskboard.fetch("where job_id = '%d'" % job_id)
    no_errors = True
    for task in tasks:
        response = TaskUtils.killTask(task.id, newStatus)
        if response == False:
            no_errors = False
    with transaction() as t:
        [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
        job.job_status = newStatus
        job.update(t)
    return no_errors
    
def prioritizeJob(job_id, priority):
    with transaction() as t:
        t.cur.execute("""update hydra_jobboard
                        set priority = '%d'
                        where id = '%d'""" % (priority, job_id))
        t.cur.execute("""update hydra_taskboard
                        set priority = '%d'
                        where job_id = '%d'""" % (priority, job_id))
                        
def setupNodeLimit(job_id, hold_status = "U"):
    [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return
        
    tasks = hydra_taskboard.fetch("where job_id = '%d'" % job_id)
    startTasks = tasks[0:taskLimit]
    holdTasks = tasks[taskLimit:]
    
    for task in startTasks:
        TaskUtils.startTask(task.id)
    
    for task in holdTasks:
        with transaction() as t:
            t.cur.execute("update hydra_taskboard set status = '%s' where id = '%d'" % (hold_status, task.id))
                        
def manageNodeLimit(job_id, hold_status = "U"):
    [job] = hydra_jobboard.fetch("where id = '%d'" % job_id)
    taskLimit = job.maxNodes
    if taskLimit < 1:
        return
        
    tasks = hydra_taskboard.fetch("where job_id = '%d'" % job_id)
    startList = []
    
    for task in tasks:
        if task.status == "S" or task.status == "R":
            taskLimit -= 1
        elif task.status == hold_status:
            startList.append(task.id)
    if taskLimit > 0:
        for task_id in startList[0:taskLimit]:
            TaskUtils.startTask(task_id)
        
    logger.info("Node Limit managed on Job: %d" % job_id)
                
    
