"""Useful utilities to get info on or modify nodes listed on the database."""
#Third Party
from MySQLdb import Error as sqlerror

#Hydra
from Setups.MySQLSetup import *

def getThisNodeData():
    """Returns the current node's info from the DB, None if not found in the DB."""
    try:
        [thisNode] = hydra_rendernode.secureFetch("WHERE host = %s", (Utils.myHostName(),))
    except ValueError:
        thisNode = None
    return thisNode

def onlineNode(node):
    """Sets a node to be online given it's node object"""
    if node.status == IDLE:
        return
    elif node.status == OFFLINE:
        node.status = IDLE
    elif node.status == PENDING and node.task_id:
        node.status = STARTED
    with transaction() as t:
        node.update(t)

def offlineNode(node):
    """Sets a node to be offline given it's node object"""
    if node.status == OFFLINE:
            return
    elif node.task_id:
        node.status = PENDING
    else:
        node.status = OFFLINE
    with transaction() as t:
            node.update(t)
