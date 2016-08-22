"""Things that will remain constant. Also makes them easy to change in here..."""
#Standard
import os
import sys
import getpass

#Versioning
VERSION  = 0.1

#Files
if sys.platform == "win32":
    BASEDIR = r"C:\Hydra"
else:
    user = getpass.getuser()
    BASEDIR = os.path.join("/home", user, "Hydra")

BASELOGDIR = os.path.join(BASEDIR, "logs")
RENDERLOGDIR = os.path.join(BASELOGDIR, "render")
SETTINGS = os.path.join(BASEDIR, "HydraSettings.cfg")

#Connections
MANYBYTES = 4096

#Value Dictionaries
TIMEDICT = {
    0:"00:00", 1:"00:30", 2:"01:00", 3:"01:30", 4:"02:00", 5:"02:30", 6:"03:00",
    7:"03:30", 8:"04:00", 9:"04:30", 10:"05:00", 11:"05:30", 12:"06:00",
    13:"06:30", 14:"07:00", 15:"07:30", 16:"08:00", 17:"08:30", 18:"09:00",
    19:"09:30", 20:"10:00", 21:"10:30", 22:"11:00", 23:"11:30", 24:"12:00",
    25:"12:30", 26:"13:00", 27:"13:30", 28:"14:00", 29:"14:30", 30:"15:00",
    31:"15:30", 32:"16:00", 33:"16:30", 34:"17:00", 35:"17:30", 36:"18:00",
    37:"18:30", 38:"19:00", 39:"19:30", 40:"20:00", 41:"20:30", 42:"21:00",
    43:"21:30", 44:"22:00", 45:"22:30", 46:"23:00", 47:"23:30"
}

TIMEDICT_REV = {v: k for k, v in TIMEDICT.items()}

DAYDICT = {
    0:"SUNDAY", 1:"MONDAY", 2:"TUESDAY", 3:"WEDNESDAY", 4:"THURSDAY",
    5:"FRIDAY", 6:"SATURDAY"
}
EVENTDICT = {
    1:"ONLINE", 0:"OFFLINE"
}

#Long strings that are annoying to keep in other files
DOESNOTEXISTERR_STRING = "Information about this node cannot be displayed because it is not registered on the render farm. You may continue to use Farm View, but it must be restarted after this node is registered if you wish to see this node's information."
RESETNODEMGMT_STRING = "Are you sure you want to reset node managment on the selected Job?\nThis will hold all Tasks above the max node count set on the Job."
GETOFF_STRING = "<B>WARNING</B>: All progress on current tasks will be lost for the selected render nodes. Are you sure you want to stop these nodes?\n"
GETOFFLOCAL_STRING = "All progress on the current job will be lost. Are you sure you want to stop it?"
SOCKETERR_STRING = "There was a problem communicating with the render node software. Either it's not running, or it has become unresponsive."
MULTINODEEDIT_STRING = "Are you sure you want to edit multiple nodes? A box will open for each node checked."
NOLOG_STRING = "No log on file for task: {0}\nJob was probably never started or was recently reset."
