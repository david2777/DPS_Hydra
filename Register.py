"""Registers a node with the database."""
#Standard
import os
import sys

#Third Party
#pylint: disable=E0611
from MySQLdb import IntegrityError

#Hydra
from hydra.logging_setup import logger
from hydra.hydra_sql import hydra_rendernode, transaction
import hydra.hydra_utils as hydra_utils

if __name__ == "__main__":
    me = hydra_utils.my_host_name()
    platform = sys.platform
    hydraPath, execFile = os.path.split(sys.argv[0])
    logger.info(hydraPath)
    try:
        with transaction() as t:
            hydra_rendernode(host=me, platform=platform).insert(t)
            logger.info("Node inserted into database!")
    except IntegrityError:
        logger.info("Host %s already exists in the hydra_rendernode table on the database", me)

    raw_input("\nPress enter to exit...")
