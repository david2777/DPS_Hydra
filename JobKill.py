#Standard
from sys import argv
from socket import error as socketerror

#Hydra
from MySQLSetup import hydra_rendertask, transaction, KILLED, READY, STARTED, PAUSED
from Connections import TCPConnection
from Questions import KillCurrentJobQuestion
from LoggingSetup import logger
import TaskUtils

#Original Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

def sendKillQuestion(renderhost, newStatus=KILLED):
    """Tries to kill the current task running on the renderhost. Returns True if successful, otherwise False"""
    logger.debug ('kill job on %s' % renderhost)
    connection = TCPConnection(hostname=renderhost)
    answer = connection.getAnswer(KillCurrentJobQuestion(newStatus))
    logger.debug("child killed: %s" % answer.childKilled)
    if not answer.childKilled:
        logger.debug("%r tried to kill its job but failed for some reason." % renderhost)
    return answer.childKilled
    
def killJob(job_id):
    """Kills every task associated with job_id. Killed tasks have status code 
    'K'. If a task was already started, an a kill request is sent to the host 
    running it.
    @return: False if no errors while killing started tasks, else True"""
    #Mark all of the Ready tasks as Killed
    TaskUtils.changeStatusViaJobID(job_id, "K", ["R", "U", "H"])
    
    #Get hostnames for tasks that were already started
    tuples = None # @UnusedVariable
    with transaction() as t:
        t.cur.execute("""select host from hydra_rendertask 
                        where job_id = '%d' and status = 'S'""" % job_id)
        tuples = t.cur.fetchall()
        
    #Make flat list out of single-element tuples fetched from db
    hosts = [t for (t,) in tuples]
    
    #Send a kill request to each host, note if any failures occurred
    error = False
    for host in hosts:
        try:
            error = error or not sendKillQuestion(host)
        except socketerror:
            logger.debug("There was a problem communicating with {:s}"
                         .format(host))
            error = True
    
    return error
    
    
def killTask(task_id):
    """Kills the task with the specified id. If the task has been started, a 
    kill request is sent to the node running it.
    @return: True if there were no errors killing the task, else False."""
    
    [task] = hydra_rendertask.fetch("where id = '%d'" % task_id)
    if task.status == READY or task.status == PAUSED:
        task.status = KILLED
        with transaction() as t:
            task.update(t)
        #If we reach this point: transaction successful, no exception raised
        return True
    elif task.status == STARTED:
        killed = sendKillQuestion(renderhost = task.host, newStatus = KILLED)
        #If we reach this point: TCPconnection successful, no exception raised
        return killed
    return False
    
def resurrectJob(job_id):
    """Resurrects job with the given id. Tasks marked 'K' or 'F' will have 
    their data cleared and their statuses set to 'R'"""
    with transaction() as t:
        t.cur.execute("""select id from hydra_rendertask 
                        where job_id = '%d'""" % job_id)
        tuples = t.cur.fetchall()
        
    task_ids = [t for (t,) in tuples]
    errorList = []
    
    for task_id in task_ids:
        errorList.append(resurrectTask(task_id))
    
    if True in errorList:
        return True
    else:
        return False

def resurrectTask(task_id, ignoreStarted = False):
    """Resurrects the task with the specified id. 
    @return: True if there was an error, such as when the user tries to 
             resurrect a task that is marked as Started, else False."""
    
    [task] = hydra_rendertask.fetch("where id = '%d'" % task_id)
    if (
            task.status == 'K' or task.status == 'F' or task.status == 'C' or 
            (task.status == 'S' and ignoreStarted == True)
        ):
        task.status = 'R'
        task.host = None
        task.startTime = None
        task.endTime = None
    else:
        return True

    with transaction() as t:
        task.update(t)
    
    return False

if __name__ == '__main__':
    if len(argv) == 3:
        cmd, job_id = argv[1], int(argv[2])
        if cmd == 'kill':
            killJob(job_id)
        elif cmd == 'resurrect':
            resurrectJob(job_id)
    else:
        print "Command line args: ['kill' or 'resurrect'] [job_id]"
