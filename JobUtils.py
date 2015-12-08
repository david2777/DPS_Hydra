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
    
def killJob(job_id):
    """Kills every task associated with job_id. Killed tasks have status code 
    'K'. If a task was already started, an a kill request is sent to the host 
    running it.
    @return: False if no errors while killing started tasks, else True"""
    #Mark all of the Ready tasks as Killed
    changeStatusViaJobID(job_id, "K", ["R", "U", "H"])
    
    #Get hostnames for tasks that were already started
    tuples = None # @UnusedVariable
    with transaction() as t:
        t.cur.execute("""select host from hydra_taskboard 
                        where job_id = '%d' and status = 'S'""" % job_id)
        tuples = t.cur.fetchall()
        
    #Make flat list out of single-element tuples fetched from db
    hosts = [t for (t,) in tuples]
    
    #Send a kill request to each host, note if any failures occurred
    error = False
    for host in hosts:
        try:
            error = error or not TaskUtils.sendKillQuestion(host)
        except socketerror:
            logger.debug("There was a problem communicating with {:s}"
                         .format(host))
            error = True
    return error
