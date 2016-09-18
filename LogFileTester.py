import Utilities.LogParsers as LP

RSL = LP.RedshiftMayaLog("C:\\Hydra\\logs\\render\\SampleRedshiftSimple.txt")
MRL = LP.MentalRayMayaLog("C:\\Hydra\\logs\\render\\SampleMentalRayLog.txt")
print RSL.getAverageRenderTime()
print MRL.getAverageRenderTime()
