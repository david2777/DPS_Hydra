#3rd party
from MySQLdb import Error as sqlerror

#Hydra
from MySQLSetup import *

def getThisNodeData():
    """Gets the row corresponding to localhost in the hydra_rendernode table.
    Raises MySQLdb.Error"""

    [thisNode] = hydra_rendernode.fetch("where host = '%s'"
                                        % Utils.myHostName())
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
