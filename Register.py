"""Registeres a node with the database"""
#Standard
import os
import LoggingSetup
import ConfigParser
from MySQLdb import IntegrityError

#RenderAgent
import Utils
import Constants
from MySQLSetup import renderagent_rendernode, OFFLINE, transaction
from LoggingSetup import logger

config = ConfigParser.RawConfigParser ()
config.read (Constants.SETTINGS)

me = Utils.myHostName()
minJobPriority = config.get(section="rendernode", option="minJobPriority")

try:
    with transaction() as t:
        renderagent_rendernode(host = me, status = OFFLINE, minPriority = minJobPriority).insert(t)
except IntegrityError:
    logger.debug("Host %s already exists in the renderagent_rendernode table on the databse" % me)

raw_input("\nPress enter to exit...")