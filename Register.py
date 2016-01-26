"""Registers a node with the database."""
#Standard
import os
import LoggingSetup
import ConfigParser
from MySQLdb import IntegrityError

#Hydra
import Utils
import Constants
from MySQLSetup import hydra_rendernode, OFFLINE, transaction
from LoggingSetup import logger

config = ConfigParser.RawConfigParser ()
config.read(Constants.SETTINGS)

me = Utils.myHostName()
minJobPriority = config.get(section="rendernode", option="minJobPriority")

try:
    with transaction() as t:
        hydra_rendernode(host = me, status = OFFLINE, minPriority = minJobPriority).insert(t)
except IntegrityError:
    logger.info("Host {0} already exists in the hydra_rendernode table on the databse".format(me))

raw_input("\nPress enter to exit...")
