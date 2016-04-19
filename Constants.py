"""Things that will remain constant. Also makes them easy to change in here..."""
#Standard
import os
import sys
import getpass

PORT = 3606
HOSTNAME = "localhost" #For testing on a single machine
#HOSTNAME = "154-01"    #For testing on another machine
MANYBYTES = 1 << 20

if sys.platform == "win32":
    BASEDIR = r"C:\Hydra"
else:
    user = getpass.getuser()
    BASEDIR = os.path.join("/home", user, "Hydra")

BASELOGDIR = os.path.join(BASEDIR, "logs")
RENDERLOGDIR = os.path.join(BASELOGDIR, "render")
SETTINGS = os.path.join(BASEDIR, "HydraSettings.cfg")
