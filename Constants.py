"""Things that will remain constant. Also makes them easy to change in here..."""
import os

PORT = 3606
HOSTNAME = "localhost" # for testing on a single machine
#HOSTNAME = "154-01"    # for testing on another machine
MANYBYTES = 1 << 20
BASEDIR = r"C:\Hydra"
BASELOGDIR = os.path.join(BASEDIR, "logs")
RENDERLOGDIR = os.path.join(BASELOGDIR, "render")
SETTINGS = os.path.join(BASEDIR, "HydraSettings.cfg")
