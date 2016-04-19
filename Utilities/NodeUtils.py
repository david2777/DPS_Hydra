"""Useful utilities to get info on or modify nodes listed on the DB.
Probably need to move the rest of the node utilities into here."""
#Third Party
from MySQLdb import Error as sqlerror

#Hydra
from Setups.MySQLSetup import *

def getThisNodeData():
    """Gets the row corresponding to localhost in the hydra_rendernode table."""
    try:
        [thisNode] = hydra_rendernode.fetch("WHERE host = '{0}'".format(Utils.myHostName()))
    except ValueError:
        thisNode = None
    return thisNode

def onlineNode(node):
    """Onlines the node.
    Precondition: node refers to a row from the hydra_rendernode table.
    Raises MySQLdb.Error"""

    if node.status == IDLE:
        return
    elif node.status == OFFLINE:
        node.status = IDLE
    elif node.status == PENDING and node.task_id:
        node.status = STARTED
    with transaction() as t:
        node.update(t)

def offlineNode(node):
    """Onlines the node.
    Precondition: node refers to a row from the hydra_rendernode table.
    Raises MySQLdb.Error"""

    if node.status == OFFLINE:
            return
    elif node.task_id:
        node.status = PENDING
    else:
        node.status = OFFLINE
    with transaction() as t:
            node.update(t)
