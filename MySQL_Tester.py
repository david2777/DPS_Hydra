from Setups.MySQLSetup import *
from Setups.LoggingSetup import logger

testJob = hydra_jobboard.fetch("WHERE id = 1")
print testJob
print testJob.status
print testJob.kill()
print testJob.status
