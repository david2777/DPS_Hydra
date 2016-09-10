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

#Get databse information
host = Utils.getInfoFromCFG("database", "host")
databaseName = Utils.getInfoFromCFG("database", "db")
port = int(Utils.getInfoFromCFG("database", "port"))
db_username = Utils.getInfoFromCFG("database", "username")

#Get login information
autoLogin = Utils.getInfoFromCFG("database", "autologin")
autoLogin = True if str(autoLogin).lower()[0] == "t" else False
if autoLogin:
    _db_password = PasswordStorage.loadPassword(db_username)
    if not _db_password:
        autoLogin = False

if not autoLogin:
    returnValues = PasswordStorage.qtPrompt()
    if not returnValues[0] or returnValues[1]:
        logger.error("Could not login!")
        sys.exit(1)
    else:
        db_username = returnValues[0]
        _db_password = returnValues[1]

#Statuses for either jobs/tasks or render nodes
STARTED = 'S'               #Working on a job/job in progress

#Statuses for jobs/tasks
READY = 'R'                 #Ready to be run by a render node
PAUSED = 'U'                #Job was paused
FINISHED = 'F'              #Job complete
KILLED = 'K'                #Job was killed
ERROR = 'E'                 #Job returned a non-zero exit code
CRASHED = 'C'               #Machine or server software crashed, task was found in host's DB record upon restart
TIMEOUT = 'T'               #Job took longer than the timeout time allowed
RESET = 'X'

#Statuses for render nodes
IDLE = 'I'                  #Ready to accept jobs
OFFLINE = 'O'               #Not ready to accept jobs
PENDING = 'P'               #Offline after current job is complete

niceNames = {STARTED: 'Started',
            READY: 'Ready',
            PAUSED: 'Paused',
            FINISHED: 'Finished',
            KILLED: 'Killed',
            ERROR: 'Error',
            CRASHED: 'Crashed',
            TIMEOUT: "Timed Out",
            RESET: 'Reset',
            IDLE: 'Idle',
            OFFLINE: 'Offline',
            PENDING: 'Pending',
            }

niceNamesRev = {v: k for k, v in niceNames.items()}

class tupleObject:
    @classmethod
    def tableName(cls):
        return cls.__name__

    autoColumn = None

    def __init__(self, **kwargs):
        self.__dict__['__dirty__'] = set()
        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if Utils.nonFlanged(k):
            self.__dirty__.add(k)
            #logger.debug(('dirty', k, v))

    @classmethod
    def fetch(cls, whereClause = "", whereTuple = None, cols = None,
                    orderTuples = None, limit = None, multiReturn = False,
                    explicitTransaction=None):
        """A fetch function with paramater binding.
        ie. thisNode = hydra_rendernode.fetch("WHERE host = %s", ("test",))
            idAttr = thisNode.id"""
        queryTuple = tuple()
        #Where Clause
        if whereClause and whereTuple:
            queryTuple += whereTuple

        #Order Clause
        orderClause = ""
        if orderTuples:
            orderClause = " ORDER BY"
            for oTuple in orderTuples:
                orderClause += " %s %s"
                queryTuple += oTuple

        #Limit Clause
        limitClause = ""
        if limit:
            limitClause = " LIMIT %s "
            queryTuple += (limit,)

        #Column Clause
        colStatement = "*"
        if cols:
            cols = [str(x) for x in cols]
            """
            if "id" not in cols:
                cols.append("id")
            """
            colStatement = ",".join(cols)

        #Build Select Statement
        select = "SELECT " + colStatement + " FROM {0} {1} {2} {3}"
        select =  select.format(cls.tableName(), whereClause, orderClause, limitClause)
        logger.debug(select % queryTuple)

        #Fetch the data
        def doFetch(t):
            t.cur.execute(select, queryTuple)
            names = [desc[0] for desc in t.cur.description]
            returnList = [cls(**dict(zip(names, tup))) for tup in t.cur.fetchall()]
            if multiReturn:
                return returnList
            return returnList[0] if len(returnList) == 1 else returnList

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
        return True

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

    def __init__(self):
        #Open DB Connection
        self.db = MySQLdb.connect(host = host,
                                    user = db_username,
                                    passwd = _db_password,
                                    db = databaseName,
                                    port = port)
        self.cur = self.db.cursor()
        self.cur.execute("SET autocommit = 1")

    def __enter__(self):
        #logger.debug("enter transaction %s", self)
        self.cur.execute("start transaction")
        return self

    def __exit__(self, errorType, traceback, value):
        if errorType is None:
            logger.debug("commit %s", self)
            self.cur.execute ("commit")
        else:
            logger.error("rollback %s", self)
            self.cur.execute ("rollback")
        #logger.debug("exit transaction %s", self)
        self.db.close()
