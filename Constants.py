import os

PORT = 3606
HOSTNAME = "localhost" # for testing on a single machine
#HOSTNAME = "154-01"    # for testing on another machine
MANYBYTES = 1 << 20
BASEDIR = r"C:\Hydra"
BASELOGDIR = os.path.join(BASEDIR, "logs")
RENDERLOGDIR = os.path.join(BASELOGDIR, "render")
SETTINGS = os.path.join(BASEDIR, "HydraSettings.cfg")

EXECUTEABLES = {"maya2014_Render": "C:/Program Files/Autodesk/maya2014/bin/render.exe",
                "maya2014_Proper": "C:/Program Files/Autodesk/maya2014/bin/maya.exe",
                "maya2015_Render": "C:/Program Files/Autodesk/maya2015/bin/render.exe",
                }
