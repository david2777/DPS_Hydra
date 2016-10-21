"""Registers a node with the database."""
#Standard
import os
import sys

#Third Party
#pylint: disable=E0611
from MySQLdb import IntegrityError

#Hydra
from Setups.LoggingSetup import logger
from Setups.MySQLSetup import hydra_rendernode, OFFLINE, transaction
import Utilities.Utils as Utils

if __name__ == "__main__":
    me = Utils.myHostName()
    hydraPath, execFile = os.path.split(sys.argv[0])
    logger.info(hydraPath)
    response = Utils.changeHydraEnviron(hydraPath)
    if response:
        try:
            with transaction() as t:
                hydra_rendernode(host=me, status=OFFLINE, minPriority=0).insert(t)
        except IntegrityError:
            logger.info("Host %s already exists in the hydra_rendernode table on the databse", me)
    else:
        logger.error("Could not set Hydra Environ! No changes where made. Exiting...")

    raw_input("\nPress enter to exit...")
