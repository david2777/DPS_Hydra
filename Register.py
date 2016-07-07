"""Registers a node with the database."""
#Standard
import os

#Third Party
from MySQLdb import IntegrityError

#Hydra
import Constants
from Setups.LoggingSetup import logger
import Utilities.Utils as Utils
from Setups.MySQLSetup import hydra_rendernode, OFFLINE, transaction

me = Utils.myHostName()

try:
    with transaction() as t:
        hydra_rendernode(host = me, status = OFFLINE, minPriority = 0).insert(t)
except IntegrityError:
    logger.info("Host {0} already exists in the hydra_rendernode table on the databse".format(me))

raw_input("\nPress enter to exit...")
