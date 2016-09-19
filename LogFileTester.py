import Utilities.LogParsers as LP
from Setups.MySQLSetup import *

RSL = LP.RedshiftMayaLog("C:\\Hydra\\logs\\render\\SampleRedshiftSimple.txt")
MRL = LP.MentalRayMayaLog("C:\\Hydra\\logs\\render\\SampleMentalRayLog.txt")
ti = RSL.getAverageRenderTime()
print MRL.getAverageRenderTime()

with transaction() as t:
    task = hydra_taskboard.fetch("WHERE id = '28'", explicitTransaction = t)
    task.mpf = ti
    task.update(t)
