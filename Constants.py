"""Things that will remain constant. Also makes them easy to change in here..."""
#Standard
import os
import sys
import getpass

#Logging
if sys.platform == "win32":
    BASEDIR = r"C:\Hydra"
else:
    user = getpass.getuser()
    BASEDIR = os.path.join("/home", user, "Hydra")

BASELOGDIR = os.path.join(BASEDIR, "logs")
RENDERLOGDIR = os.path.join(BASELOGDIR, "render")
SETTINGS = os.path.join(BASEDIR, "HydraSettings.cfg")

#Connections
MANYBYTES = 1 << 20

#Long strings that are annoying to keep in other files
SQLERR_STRING = "There was a problem while trying to fetch info from the database. Check the FarmView log file for more details about the error."
DOESNOTEXISTERR_STRING = "Information about this node cannot be displayed because it is not registered on the render farm. You may continue to use Farm View, but it must be restarted after this node is registered if you wish to see this node's information."
RESETNODEMGMT_STRING = "Are you sure you want to reset node managment on the selected Job?\nThis will hold all Tasks above the max node count set on the Job."
GETOFF_STRING = "<B>WARNING</B>: All progress on current tasks will be lost for the selected render nodes. Are you sure you want to stop these nodes?\n"
GETOFFLOCAL_STRING = "All progress on the current job will be lost. Are you sure you want to stop it?"
SOCKETERR_STRING = "There was a problem communicating with the render node software. Either it's not running, or it has become unresponsive."
MULTINODEEDIT_STRING = "Are you sure you want to edit multiple nodes? A box will open for each node checked."
NOLOG_STRING = "No log on file for task: {0}\nJob was probably never started or was recently reset."
