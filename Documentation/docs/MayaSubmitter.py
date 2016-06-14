#Standard
import subprocess
#from base64 import b64encode

#Third Party
import maya.cmds as cmds
import maya.mel as mel

#-----------------Get Data from Maya------------------#
reqsList = []
renderLayersList = []
engineDict = {"redshift":"Redshift", "mentalRay":"MentalRay", "vray":"VRay", "renderMan":"RenderMan", "renderManRIS":"RenderMan", "arnold":"Arnold"}
sceneFile = cmds.file(q = True, exn = True)
projectDir = cmds.workspace(q = True, rd = True)
startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
camList = [x for x in cmds.ls(type="camera") if cmds.getAttr(x+".renderable")]
try:
    renderCam = camList[0]
except IndexError:
    renderCam = None

currentEngine = mel.eval("currentRenderer")
if currentEngine in engineDict.keys():
    reqsList.append(engineDict[currentEngine])
reqsReturn  = ",".join(reqsList)

renderLayers = cmds.listConnections("renderLayerManager")
for layer in renderLayers:
    if cmds.getAttr(layer + ".renderable"):
        renderLayersList.append(str(layer))
renderLayersReturn = ",".join(renderLayersList)

#----------Setup Base Submitter Command Line Args----------#
command = "python C:\\Users\\David\\Documents\\GitHub\\DPS_Hydra\\SubmitterMain.py \"{0}\" -s \"{1}\" -e \"{2}\" -p \"{3}\"".format(sceneFile, startFrame, endFrame, projectDir)

#------------Build Extra Maya Command Line Args------------#
extraCmdList = []
#Confirm Camera Here
if renderCam:
    extraCmdList.append("-cam {0}".format(renderCam))

#Build Render Directory here
renderDir = "//This/Is/A/Test"
if renderDir:
    extraCmdList.append("-rd {0}".format(renderDir))

if extraCmdList != []:
    command += " -m \"{0}\"".format(" ".join(extraCmdList))

#----------Setup Extra Submitter Command Line Args----------#
#Build Project Name Here
projectName = "TestProject"
if projectName:
    command += " -q \"{0}\"".format(projectName)

if reqsReturn != "":
    command += " -c \"{0}\"".format(reqsReturn)

if renderLayersReturn != "":
    command += " -r \"{0}\"".format(renderLayersReturn)

print command
subprocess.check_call(command)
