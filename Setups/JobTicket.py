"""Setup for job and task tickets which are submitted to the DB."""
#Hydra
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import *

#TODO:Handle test frames better
#TODO:Create task functions, maybe a TaskTicket.py?

def submitJob(niceName, projectName, owner, status, requirements, execName,
                baseCMD, startFrame, endFrame, byFrame, renderLayers, taskFile,
                priority, phase, maxNodes, timeout, maxAttempts):
    """A simple function for submitting a job to the jobBoard"""
    #Setup default renderLayerTracker
    renderLayerTracker = [str(startFrame) for x in renderLayers.split(",")]
    renderLayerTracker = ",".join(renderLayerTracker)
    niceName = "{0}_PHASE{1:02d}".format(niceName, phase)

    job = hydra_jobboard(niceName = niceName, projectName = projectName,
                        owner = owner, status = status,
                        requirements = requirements, execName = execName,
                        baseCMD = baseCMD, startFrame = startFrame,
                        endFrame = endFrame, byFrame = byFrame,
                        renderLayers = renderLayers,
                        renderLayerTracker = renderLayerTracker,
                        taskFile = taskFile, priority = priority,
                        phase = phase, maxNodes = maxNodes, timeout = timeout,
                        maxAttempts = maxAttempts)

    with transaction() as t:
        job.insert(transaction=t)

    return job

def testJobs():
    prompt = raw_input("Create test Job? ")
    if prompt.lower() == "yes" or prompt == "y":
        niceName = "TestJob"
        projectName = "HydraTestProject"
        owner = "dduvoisin"
        requirements = ""
        execName = "maya2015"
        baseCMD = "-rd \"//this/is a test/directory/with/spaces\" -x 1920 -y 1080 -cam Anim:shotCam"
        startFrame = 101
        endFrame = 150
        renderLayers = "Beauty,Sky,FX"
        taskFile = "//path/to/maya/file/renderFile_001.ma"
        priority = 0
        maxNodes = 0
        timeout = 10200
        maxAttempts = 999

        phase01 = submitJob(niceName, projectName, owner, "R", requirements, execName,
                        baseCMD, startFrame, endFrame, 10, renderLayers, taskFile,
                        priority, 1, maxNodes, timeout, maxAttempts)

        phase02 = submitJob(niceName, projectName, owner, "U", requirements, execName,
                        baseCMD, startFrame, endFrame, 1, renderLayers, taskFile,
                        priority, 2, maxNodes, timeout, maxAttempts)


    raw_input("DONE...")
