import Utilities.LogParsers as LP
from Setups.MySQLSetup import *

#RSL = LP.RedshiftMayaLog("C:\\Hydra\\logs\\render\\SampleRedshiftSimple.txt")
#MRL = LP.MentalRayMayaLog("C:\\Hydra\\logs\\render\\SampleMentalRayLog.txt")
FCL = LP.FusionCompLog("C:\\Hydra\\logs\\render\\FusionLog.txt")
print FCL.getTotalRenderTime()
