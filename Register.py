"""Registers a node with the database."""
#Standard
import os
import sys

#Third Party
from MySQLdb import IntegrityError

#Hydra
import Constants
from Setups.LoggingSetup import logger
import Utilities.Utils as Utils
from Setups.MySQLSetup import hydra_rendernode, OFFLINE, transaction

if __name__ == "__main__":
    me = Utils.myHostName()
    hydraPath,execFile = os.path.split(sys.argv[0])
    logger.info(hydraPath)
    response = Utils.changeHydraEnviron(hydraPath)
    if response:
        try:
            with transaction() as t:
                hydra_rendernode(host = me, status = OFFLINE, minPriority = 0).insert(t)
        except IntegrityError:
            logger.info("Host {0} already exists in the hydra_rendernode table on the databse".format(me))
    else:
        logger.error("Could not set Hydra Environ! No changes where made. Exiting...")

    raw_input("\nPress enter to exit...")
