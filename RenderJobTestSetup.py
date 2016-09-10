from Setups.MySQLSetup import *
from Setups.RenderJob import RenderJob
from Setups.LoggingSetup import logger

testJob = hydra_jobboard.fetch("WHERE id = 1")
rj = RenderJob(testJob)
print rj
rj.reset()
print rj
