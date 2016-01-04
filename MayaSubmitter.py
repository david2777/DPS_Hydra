#Standard
import subprocess
#from base64 import b64encode

#Third Party
import maya.cmds as cmds
import maya.mel as mel

#Get data from Maya
reqsList = []
renderLayersList = []
engineDict = {"redshift":"Redshift", "mentalRay":"MentalRay", "vray":"VRay", "renderMan":"RenderMan", "renderManRIS":"RenderMan", "arnold":"Arnold"}
sceneFile = cmds.file(q = True, exn = True)
project = cmds.workspace(q = True, rd = True)
startFrame = cmds.getAttr("defaultRenderGlobals.startFrame")
endFrame = cmds.getAttr("defaultRenderGlobals.endFrame")
#Get renderable camera here
cmd = ""

currentEngine = mel.eval("currentRenderer")
if currentEngine in engineDict.keys():
    reqsList.append(engineDict[currentEngine])
       
renderLayers = cmds.listConnections("renderLayerManager")
for layer in renderLayers:
    if cmds.getAttr(layer + ".renderable"):
        renderLayersList.append(str(layer))
renderLayersReturn = ",".join(renderLayersList)

reqsReturn  = ",".join(reqsList)

command = "python C:\\Users\\David\\Documents\\GitHub\\DPS_Hydra\\SubmitterMain.py %s -s %d -e %d -p %s" % (sceneFile, startFrame, endFrame, project)
if cmd != "":
    command += " -m %s" % cmd
if reqsReturn != "":
    command += " -c %s" % reqsReturn
if renderLayersReturn != "":
    command += " -r %s" % renderLayersReturn
    
print command
subprocess.check_call(command)
        
