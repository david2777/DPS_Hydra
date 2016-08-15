"""A collection of utilities to be run on Jobs (the parent of an individual task)"""
#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
import Utilities.TaskUtils as TaskUtils

def startJob(jobID):
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET status = 'R' WHERE id = %s", (jobID,))

def killJob(jobID, newStatus):
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (jobID,),
                                    multiReturn = True, cols = ["id"])
    idList = [int(ta.id) for ta in tasks]
    responses = [TaskUtils.killTask(taskID, newStatus) for taskID in idList]
    jobUpdate = "UPDATE hydra_jobboard SET status = 'U' WHERE id = %s"
    with transaction() as t:
        t.cur.execute(jobUpdate, (jobID,))
    return all(responses)

def prioritizeJob(jobID, priority):
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET priority = %s WHERE id = %s", (priority, jobID))

def archiveJob(jobID, mode):
    jobCommand = "UPDATE hydra_jobboard SET archived = %s WHERE id = %s"
    with transaction() as t:
        t.cur.execute(jobCommand, (mode, jobID))
    return True
