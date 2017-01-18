#Standard
import subprocess
import re
import os

#Third Party
#Fix can't import maya
#pylint: disable=E0401
import maya.cmds as cmds
import maya.mel as mel

def DPSHydra_MayaSubmitter():
    #-------------Variables and Static Data--------------#
    reqsList = []
    extraCmdList = []

    engineReqsDict = {"redshift":"Redshift", "mentalRay":"MentalRay"}

    jobTypeDict = {"redshift":"RedshiftRender", "mentalRay":"MentalRayRender"}

    engineCMDDict = {"redshift":"redshift", "mentalRay":"mr", "vray":"vray",
                    "renderMan":"rman", "renderManRIS":"rman", "arnold":"arnold",
                    "mayaHardware2":"hw2", "software":"sw"}

    _ = {"vray":"VRay", "renderMan":"RenderMan",
                        "renderManRIS":"RenderMan", "arnold":"Arnold"}

    #-----------------Get Data from Maya------------------#
    sceneFile = cmds.file(q=True, exn=True)
    sceneName = sceneFile.split("/")[-1]
    projectDir = cmds.workspace(q=True, rd=True)
    startFrame = cmds.playbackOptions(q=True, minTime=True)
    endFrame = cmds.playbackOptions(q=True, maxTime=True)
    camList = [x for x in cmds.ls(type="camera") if cmds.getAttr(x+".renderable")]

    #-------------------Build Command--------------------#
    command = "python %USERPROFILE%\\Documents\\GitHub\\DPS_Hydra\\SubmitterMain.py \"{0}\" -s \"{1}\" -e \"{2}\" -p \"{3}\"".format(sceneFile, startFrame, endFrame, projectDir)

    #Render Camera
    if not camList:
        cmds.confirmDialog(title="Error",
                            message="No Renderable Cameras were found! Aborting...")
        cmds.error("No Renderable Cameras were found! Aborting...")
    else:
        renderCam = camList[0]
        msgString = "Is this the correct render camera?\n\n{0}"
        response = cmds.confirmDialog(title='Confirm', button=["Yes", "No"],
                                        message=msgString.format(renderCam),
                                        defaultButton="Yes", cancelButton="No",
                                        dismissString="No")
        if response == "No":
            cmds.error("Please change render cam and try again.")

    #Render Engine, Job Type
    currentEngine = mel.eval("currentRenderer")
    if currentEngine in engineReqsDict.keys():
        reqsList.append(engineReqsDict[currentEngine])
        command += " -t {}".format(jobTypeDict[currentEngine])
        extraCmdList += ["-r {0}".format(engineCMDDict[currentEngine]),
                            "-cam {0}".format(renderCam)]
    else:
        cmds.error("{} is not supported by Hydra yet.".format(currentEngine))

    #Render Layers
    renderLayers = cmds.listConnections("renderLayerManager")
    renderLayers = [x for x in renderLayers if cmds.getAttr("{}.renderable".format(x))]
    renderLayersString = ",".join(renderLayers)
    command += " -l \"{0}\"".format(renderLayersString)

    #Maya Extra CMDs (Renderer, Cam, Etc)
    if extraCmdList:
        command += " -m \"{0}\"".format(" ".join(extraCmdList))

    #Project Name
    projectName = re.search(r"_\d{3}_\d{4}.+$", sceneName)
    if projectName:
        projectName = sceneName.replace(projectName.group(0), "")
    else:
        projectName = "UnkownProject"

    command += " -q \"{0}\"".format(projectName)

    #Render Image Directory
    try:
        renderDir = mel.eval("source GetRenderPath;string $renderDirectory = GetRenderPath();")
        renderDir = os.path.join(renderDir, "mayaRenders")
        if renderDir != "":
            command += " -d \"{0}\"".format(renderDir)
    except RuntimeError:
        pass

    #Requrements
    reqsString = ",".join(reqsList)
    if reqsString != "":
        command += " -c \"{0}\"".format(reqsString)

    #Run Command
    print command
    subprocess.Popen(command, shell=True)
