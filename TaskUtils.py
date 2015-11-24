#Standard
import sys

#3rd party
from MySQLdb import Error as sqlerror

#RenderAgent
#from tableHelpers import *                      #@UnusedWildImport
from MySQLSetup import *                        #@UnusedWildImport
from LoggingSetup import logger                 #@Reimport
import Utils                                    #@Reimport


def changeStatusViaJobID(job_id, new_status, old_status_list=[]):
    if type(old_status_list) is not list:
        logger.error("Bad Old Status List in TaskUtils!")
        raise Exception("Please use a list for old statuses")
    command = """update renderagent_rendertask set status = '%s' where job_id = '%d'""" % (new_status, job_id)
    if len(old_status_list) > 0:
        command = command + """ and status = '%s'""" % old_status_list[0]
        for status in old_status_list[1:]:
            command = command + """ or status = '%s'""" % status
    
    with transaction() as t:
        t.cur.execute(command)
        
def unstick(taskID=None, newTaskStatus=READY, host=None, newHostStatus=IDLE):
    with transaction () as t:
        if taskID:
            [task] = renderagent_rendertask.fetch("where id = %d" % taskID)
            #If the task is marked, say, CRASHED, leave the host name alone.
            #Only READY would be confusing with a host named filled in. I think.
            if newTaskStatus == READY:
                task.host = None

            task.status = newTaskStatus
            task.startTime = None
            task.endTime = None
            task.update (t)
        if host:
            [host] = renderagent_rendernode.fetch ("where host = '%s'" % host)
            host.task_id = None
            host.status = newHostStatus
            host.update (t)
