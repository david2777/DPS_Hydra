"""Registeres a node with the database"""
#Standard
import os
import LoggingSetup
import ConfigParser

#RenderAgent
import Utils
import Constants
from MySQLSetup import renderagent_rendernode, OFFLINE, transaction

config = ConfigParser.RawConfigParser ()
config.read (Constants.SETTINGS)

me = Utils.myHostName()
minJobPriority = config.get(section="rendernode", option="minJobPriority")

if renderagent_rendernode.fetch( "where host = '%s'" % me ):
    raise Exception( 'Already registered' )

with transaction() as t:
    renderagent_rendernode(host = me, status = OFFLINE, minPriority = minJobPriority).insert(t)

raw_input("\nPress enter to exit...")
