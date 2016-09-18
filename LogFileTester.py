import Utilities.LogParsers as LP

RSL = LP.RedshiftMayaLog("C:\\Hydra\\logs\\render\\SampleRedshiftSimple.txt")
print RSL.getTotalRenderTime()
