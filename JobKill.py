#Standard
from sys import argv
from socket import error as socketerror

#Hydra
from MySQLSetup import hydra_taskboard, transaction, KILLED, READY, STARTED, PAUSED
from Connections import TCPConnection
from Questions import KillCurrentJobQuestion
from LoggingSetup import logger
import TaskUtils
import JobUtils

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
    JobUtils.changeStatusViaJobID(job_id, "K", ["R", "U", "H"])
    
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
            error = error or not sendKillQuestion(host)
        except socketerror:
            logger.debug("There was a problem communicating with {:s}"
                         .format(host))
            error = True
    
    return error

if __name__ == '__main__':
    if len(argv) == 3:
        cmd, job_id = argv[1], int(argv[2])
        if cmd == 'kill':
            killJob(job_id)
    else:
        print "Command line args: ['kill'] [job_id]"
