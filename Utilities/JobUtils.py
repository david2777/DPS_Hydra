"""A collection of utilities to be run on Jobs (the parent of an individual task)"""
#Hydra
from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger
import Utilities.TaskUtils as TaskUtils

#TODO: Reset and Remove Render Layers from a Job

def startJob(jobID):
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET status = 'R' WHERE id = %s", (jobID,))

def pauseJob(jobID):
    with transaction() as t:
        t.cur.execute("UPDATE hydra_jobboard SET status = 'U' WHERE id = %s", (jobID,))

def killJob(jobID, newStatus):
    tasks = hydra_taskboard.fetch("WHERE job_id = %s", (jobID,),
                                    multiReturn = True, cols = ["id", "renderLayers"])
    idList = [int(ta.id) for ta in tasks]
    responses = [TaskUtils.killTask(taskID, newStatus) for taskID in idList]
    jobUpdate = "UPDATE hydra_jobboard SET status = 'U'"
    if newStatus == RESET:
        rlTracker = ",".join(["0" for x in len(job.renderLayers.split(","))])
        jobUpdate += ", renderLayerTracker = '{}'".format(rlTracker)
    jobUpdate += " WHERE id = %s"
    with transaction() as t:
        t.cur.execute(jobUpdate, (jobID,))
    return all(responses)

def archiveJob(jobID, mode):
    jobCommand = "UPDATE hydra_jobboard SET archived = %s WHERE id = %s"
    with transaction() as t:
        t.cur.execute(jobCommand, (mode, jobID))
    return True
