"""Setup for MySQL Transactions."""
#Standard
import sys

#Third Party
import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra
from Setups.LoggingSetup import logger
from Setups import PasswordStorage
import Utilities.Utils as Utils

host = Utils.getInfoFromCFG("database", "host")
databaseName = Utils.getInfoFromCFG("database", "db")
port = int(Utils.getInfoFromCFG("database", "port"))
db_username = Utils.getInfoFromCFG("database", "username")

autoLogin = eval(Utils.getInfoFromCFG("database", "autologin"))
if autoLogin:
    _db_password = PasswordStorage.loadPassword(db_username)
    if not _db_password:
        autoLogin = False

if not autoLogin:
    returnValues = PasswordStorage.qtPrompt()
    if not returnValues[0]:
        logger.error("Could not login!")
        sys.exit(1)
    else:
        _db_password = returnValues[1]

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

#Statuses for jobs/tasks
MANAGED = 'M'               #Job is being managed by the max node manager
PAUSED = 'U'                #Job was paused
ERROR = 'E'                 #Job returned a non-zero exit code
READY = 'R'                 #Ready to be run by a render node
FINISHED = 'F'              #Job complete
KILLED = 'K'                #Job was killed
CRASHED = 'C'               #Machine or server software crashed, task was found in host's DB record upon restart
TIMEOUT = 'T'

#Statuses for render nodes
IDLE = 'I'                  #Ready to accept jobs
OFFLINE = 'O'               #Not ready to accept jobs
PENDING = 'P'               #Offline after current job is complete

#Statuses for either jobs/tasks or render nodes
STARTED = 'S'               #Working on a job

niceNames = {PAUSED: 'Paused',
            READY: 'Ready',
            FINISHED: 'Finished',
            KILLED: 'Killed',
            CRASHED: 'Crashed',
            IDLE: 'Idle',
            OFFLINE: 'Offline',
            PENDING: 'Pending',
            STARTED: 'Started',
            ERROR: 'Error',
            MANAGED: 'Managed',
            TIMEOUT: "Timed Out",
            }


class AUTOINCREMENT:
    pass

class tupleObject:
    @classmethod
    def tableName(cls):
        return cls.__name__

    autoColumn = None

    def __init__(self, **kwargs):
        self.__dict__['__dirty__'] = set ()
        for k, v in kwargs.iteritems ():
            self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if Utils.nonFlanged(k):
            self.__dirty__.add(k)
            logger.debug (('dirty', k, v))

    @classmethod
    def fetch(cls, whereClause = "", order = None, limit = None, explicitTransaction=None):
        """A deprecated method for easily fethcing information from the SQL server.
        This is insecure and vulnerable to SQL injection so don't use it where possible."""
        orderClause = "" if order is None else " " + order + " "
        limitClause = "" if limit is None else " LIMIT {0} ".format(limit)
        select = "SELECT * FROM {0} {1} {2} {3}".format(cls.tableName(), whereClause, orderClause, limitClause)
        logger.debug(select)

        def doFetch(t):
            t.cur.execute(select)
            names = [desc[0] for desc in t.cur.description]
            return [cls (**dict(zip(names, tup)))
                    for tup in t.cur.fetchall()]
        if explicitTransaction:
            return doFetch(explicitTransaction)
        else:
            with transaction() as t:
                return doFetch(t)

    @classmethod
    def secureFetch(cls, whereClause, whereTuple, cols = None, orderTuples = None,
                    limit = None, explicitTransaction=None):
        """A fetch function with paramater binding.
        ie. [thisNode] = hydra_rendernode.fetch("WHERE host = %s", ("test",))
            idAttr = thisNode.id"""
        #orderClause = "" if order is None else " " + order + " "
        #limitClause = "" if limit is None else " LIMIT %s "
        if orderTuples:
            if type(orderTuples) is not tuple:
                logger.error("Bad orderTuple!")
                return None
            for oTuple in orderTuples:
                if type(oTuple) is not tuple or len(oTuple) != 2:
                    logger.error("Bad orderTuple!")
                    return None
            orderClause = " ORDER BY"
            for oTuple in orderTuples:
                orderClause += " %s %s"
                whereTuple = whereTuple + oTuple
            orderClause += " "
        else:
            orderClause = ""

        if limit:
            limitClause = " LIMIT %s "
            whereTuple = whereTuple + (limit,)
        else:
            limitClause = ""

        if cols:
            cols = [str(x) for x in cols]
            colStatement = ",".join(cols)
            select = "SELECT " + colStatement + " FROM {0} {1} {2} {3}"
        else:
            select = "SELECT * FROM {0} {1} {2} {3}"

        select =  select.format(cls.tableName(), whereClause, orderClause, limitClause)
        logger.debug(select % whereTuple)

        def doFetch(t):
            t.cur.execute(select, whereTuple)
            names = [desc[0] for desc in t.cur.description]
            return [cls (**dict(zip(names, tup)))
                    for tup in t.cur.fetchall()]
        if explicitTransaction:
            return doFetch(explicitTransaction)
        else:
            with transaction() as t:
                return doFetch(t)

    def attributes(self):
        return filter(Utils.nonFlanged, self.__dict__.keys())

    def vals(self):
        return self.__dict__

    def insert(self, transaction):
        names = self.attributes()
        values = [getattr(self, name)
                  for name in names]
        nameString = ", ".join(names)
        valueString = ", ".join(len(names) * ["%s"])
        valueStringSimple = ", ".join([str(val) for val in values])
        query = "INSERT INTO %s (%s) VALUES (%s)" % (self.tableName(), nameString, valueString)
        queryRepr = "INSERT INTO %s (%s) VALUES (%s)" % (self.tableName(), nameString, valueStringSimple)
        logger.debug(queryRepr)
        transaction.cur.executemany(query, [values])
        if self.autoColumn:
            transaction.cur.execute("SELECT last_insert_id()")
            [insert_id] = transaction.cur.fetchone()
            self.__dict__[self.autoColumn] = insert_id

    def update(self, transaction):
        names = list(self.__dirty__)
        if not names:
            return

        values = ([getattr(self, name) for name in names] + [getattr(self, self.primaryKey)])
        assignments = ", ".join(["%s = %%s" % name for name in names])
        query = "UPDATE %s SET %s WHERE %s = %%s" % (self.tableName(), assignments, self.primaryKey)
        logger.debug((query, values))
        transaction.cur.executemany(query, [values])

class hydra_rendernode(tupleObject):
    primaryKey = 'host'

class hydra_jobboard(tupleObject):
    autoColumn = 'id'
    primaryKey = 'id'

class hydra_taskboard(tupleObject):
    autoColumn = 'id'
    primaryKey = 'id'

class hydra_capabilities(tupleObject):
    primaryKey = 'name'

class hydra_executable(tupleObject):
    primaryKey = 'name'

class hydra_holidays(tupleObject):
    primaryKey = 'id'


class transaction:
    global host
    global db_username
    global _db_password
    global databaseName
    global port
    print host, db_username, _db_password, databaseName, port

    def __init__(self):
        #Open DB Connection
        self.db = MySQLdb.connect(host = host,
                                    user = db_username,
                                    passwd = _db_password,
                                    db = databaseName,
                                    port = port)
        self.cur = self.db.cursor()
        self.cur.execute("set autocommit = 1")

    def __enter__(self):
        logger.debug("enter transaction %s", self)
        self.cur.execute("start transaction")
        return self

    def __exit__(self, errorType, traceback, value):
        if errorType is None:
            logger.debug("commit %s", self)
            self.cur.execute ("commit")
        else:
            logger.error("rollback %s", self)
            self.cur.execute ("rollback")
        logger.debug("exit transaction %s", self)
        self.db.close()
