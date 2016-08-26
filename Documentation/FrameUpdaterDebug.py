#Standard
import os
import subprocess

#Maya
import maya.cmds as cmds

frameUpdaterEXE = "\\\\Zed\\Apps\\_Hydra_RenderFarm\\Dist_0.1\\FrameUpdater.exe"

def FrameUpdaterDebugger():
    if not os.path.isfile(frameUpdaterEXE):
        return 211
    proc = subprocess.Popen([frameUpdaterEXE, 999])
    proc.communicate()
    return proc.returncode
