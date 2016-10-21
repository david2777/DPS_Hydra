#Standard
import subprocess
import re
import os

#Third Party
#Fix can't import maya
#pylint: disable=E0401
import maya.cmds as cmds
import maya.mel as mel

#-----------------Get Data from Maya------------------#
reqsList = []
renderLayersList = []
engineDict = {"redshift":"Redshift", "mentalRay":"MentalRay"}

typeDict = {"redshift":"RedshiftRender", "mentalRay":"MentalRayRender"}

notYetSupported = {"vray":"VRay", "renderMan":"RenderMan",
                    "renderManRIS":"RenderMan", "arnold":"Arnold"}

engineCMDDict = {"redshift":"redshift", "mentalRay":"mr", "vray":"vray",
                "renderMan":"rman", "renderManRIS":"rman", "arnold":"arnold",
                "mayaHardware2":"hw2", "software":"sw"}

sceneFile = cmds.file(q=True, exn=True)
sceneName = sceneFile.split("/")[-1]
projectDir = cmds.workspace(q=True, rd=True)
startFrame = cmds.playbackOptions(q=True, minTime=True)
endFrame = cmds.playbackOptions(q=True, maxTime=True)
camList = [x for x in cmds.ls(type="camera") if cmds.getAttr(x+".renderable")]
try:
    renderCam = camList[0]
    msgString = "Is this the correct render camera?\n\n{0}"
    response = cmds.confirmDialog(title='Confirm',
                                    message=msgString.format(renderCam),
                                    button=["Yes", "No"],
                                    defaultButton="Yes",
                                    cancelButton="No",
                                    dismissString="No")
    if response == "No":
        cmds.error("Please change render cam and try again.")
except IndexError:
    cmds.confirmDialog(title="Error",
                        message="No Renderable Cameras were found! Aborting...")
    raise

currentEngine = mel.eval("currentRenderer")
if currentEngine in engineDict.keys():
    reqsList.append(engineDict[currentEngine])
reqsReturn = ",".join(reqsList)

renderLayers = cmds.listConnections("renderLayerManager")
for layer in renderLayers:
    if cmds.getAttr(layer + ".renderable"):
        renderLayersList.append(str(layer))
renderLayersReturn = ",".join(renderLayersList)

#----------Setup Base Submitter Command Line Args----------#
command = "python %USERPROFILE%\\Documents\\GitHub\\DPS_Hydra\\SubmitterMain.py \"{0}\" -s \"{1}\" -e \"{2}\" -p \"{3}\"".format(sceneFile, startFrame, endFrame, projectDir)

#------------Build Extra Maya Command Line Args------------#
extraCmdList = []

try:
    extraCmdList.append("-r {0}".format(engineCMDDict[currentEngine]))
except KeyError:
    cmds.error("Render Engine {} not yet supported!".format(currentEngine))

extraCmdList.append("-cam {0}".format(renderCam))

if extraCmdList != []:
    command += " -m \"{0}\"".format(" ".join(extraCmdList))

#----------Setup Extra Submitter Command Line Args----------#
projectName = re.search("_[0-9]{3}_[0-9]{4}.+$", sceneName)
if projectName:
    projectName = sceneName.replace(projectName.group(0), "")
else:
    projectName = "UnkownProject"

command += " -q \"{0}\"".format(projectName)

command += " -t {}".format(typeDict[currentEngine])

try:
    renderDir = mel.eval("source GetRenderPath;string $renderDirectory = GetRenderPath();")
    renderDir = os.path.join(renderDir, "mayaRenders")
    if renderDir != "":
        command += " -d \"{0}\"".format(renderDir)
except RuntimeError:
    pass

if reqsReturn != "":
    command += " -c \"{0}\"".format(reqsReturn)

if renderLayersReturn != "":
    command += " -l \"{0}\"".format(renderLayersReturn)

print command
subprocess.Popen(command, shell=True)
