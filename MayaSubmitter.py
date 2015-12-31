#Standard
import subprocess
from base64 import b64encode

#Third Party
import maya.cmds as cmds

#Get data from Maya
sceneFile = cmds.file(q = True, exn = True)
project = cmds.workspace(q = True, rd = True)
