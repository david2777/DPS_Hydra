"""Setup for MySQL Transactions."""
#Standard
import sys
import shlex

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
domain = Utils.getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
if domain != "" and host != "localhost":
    host += ".{}".format(domain)
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

class transaction:
    global host
    global db_username
    global _db_password
    global databaseName
    global port

    def __init__(self):
        #Open DB Connection
        self.db = MySQLdb.connect(host = host, user = db_username,
                                    passwd = _db_password, db = databaseName,
                                    port = port)
        self.cur = self.db.cursor()
        self.cur.execute("SET autocommit = 1")

    def __enter__(self):
        #logger.debug("enter transaction %s", self)
        self.cur.execute("start transaction")
        return self

    def __exit__(self, errorType, traceback, value):
        if errorType is None:
            #logger.debug("commit %s", self)
            self.cur.execute("commit")
        else:
            logger.error("rollback %s", self)
            self.cur.execute("rollback")
        #logger.debug("exit transaction %s", self)
        self.db.close()

class hydraObject:
    def __init__(self, **kwargs):
        self.__dict__['__dirty__'] = set()
        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if Utils.nonFlanged(k):
            self.__dirty__.add(k)
            #logger.debug(('dirty', k, v))

    def __repr__(self):
        return "{0} object {1}".format(self.tableName(), getattr(self, self.primaryKey))

    @classmethod
    def tableName(cls):
        return cls.__name__

    @classmethod
    def fetch(cls, whereClause = "", whereTuple = None, cols = None,
                    orderTuples = None, limit = None, multiReturn = False,
                    explicitTransaction=None):
        """A fetch function with paramater binding.
        ie. thisNode = hydra_rendernode.fetch("WHERE host = %s", ("test",))
            idAttr = thisNode.id"""
        #Column Clause
        colStatement = "*"
        if cols and len(cols) > 0:
            cols = [str(x) for x in cols]
            if cls.primaryKey not in cols:
                cols += [cls.primaryKey]
            colStatement = ",".join(cols)

        queryTuple = tuple()
        #Where Clause
        if whereClause and whereTuple:
            queryTuple += whereTuple

        #Order Clause
        orderClause = ""
        if orderTuples:
            orderClause = "ORDER BY"
            for oTuple in orderTuples:
                orderClause += " %s %s"
                queryTuple += oTuple

        #Limit Clause
        limitClause = ""
        if limit:
            limitClause = "LIMIT %s "
            queryTuple += (limit,)

        #Build Select Statement
        select = "SELECT {0} FROM {1} {2} {3} {4}"
        select =  select.format(colStatement, cls.tableName(), whereClause,
                                orderClause, limitClause)
        logger.debug(select % queryTuple)

        #Fetch the data
        if explicitTransaction:
            return cls.doFetch(explicitTransaction, select, queryTuple, multiReturn)
        else:
            with transaction() as t:
                return cls.doFetch(t, select, queryTuple, multiReturn)

    @classmethod
    def doFetch(cls, t, select, queryTuple, multiReturn):
        t.cur.execute(select, queryTuple)
        names = [desc[0] for desc in t.cur.description]
        returnList = [cls(**dict(zip(names, tup))) for tup in t.cur.fetchall()]
        if multiReturn:
            return returnList
        return returnList[0] if len(returnList) == 1 else returnList

    def attributes(self):
        return filter(Utils.nonFlanged, self.__dict__.keys())

    def vals(self):
        return self.__dict__

    def insert(self, transaction):
        names = self.attributes()
        values = [getattr(self, name) for name in names]
        nameString = ", ".join(names)
        valueString = ", ".join(["%s" for x in len(names)])
        query = "INSERT INTO {0} ({1}) VALUES ({2})".format(self.tableName(), nameString, valueString)

        transaction.cur.executemany(query, [values])
        if self.autoColumn:
            transaction.cur.execute("SELECT last_insert_id()")
            [insert_id] = transaction.cur.fetchone()
            self.__dict__[self.autoColumn] = insert_id

    def update(self, transaction):
        names = list(self.__dirty__)
        if not names:
            logger.info("Nothing to update on {}".format(self.tableName()))
            return

        values = ([getattr(self, n) for n in names] + [getattr(self, self.primaryKey)])
        assignments = ", ".join(["{} = %s".format(n) for n in names])
        query = "UPDATE {0} SET {1} WHERE {2} = %s".format(self.tableName(), assignments, self.primaryKey)
        logger.debug((query, values))
        transaction.cur.executemany(query, [values])
        return True

    def updateAttr(self, attr, value):
        if attr not in self.attributes():
            logger.error("Attr {0} not found in {1}".format(attr, self.tableName()))
            return

        with transaction() as t:
            updateStr = "UPDATE {0} SET {1} = %s WHERE {2} = %s"
            t.cur.execute(updateStr.format(self.tableName(), attr, self.primaryKey),
                            (value, getattr(self, self.primaryKey)))

        self.__dict__[attr] = value
        return True

class hydra_rendernode(hydraObject):
    autoColumn = None
    primaryKey = "host"

    def online(self):
        self.updateAttr("status", "I")

    def offline(self):
        newStatus = "P" if self.status == "S" else "O"
        self.updateAttr("status", newStatus)

    def getOff(self):
        return True

class hydra_jobboard(hydraObject):
    autoColumn = "id"
    primaryKey = "id"

    subtasksLoaded = False
    #TODO:Fix Job Type
    jobType = "MayaRender"

    def loadSubtasks(self):
        self.subtasksLoaded = True
        self.subTasks = hydra_taskboard.fetch("WHERE job_id = %s", (self.id,),
                                                multiReturn = True)
        self.activeSubTasks = [t for t in self.subTasks if t.status == "S"]

    def start(self):
        return self.updateAttr("status", "R")

    def pause(self):
        return self.updateAttr("status", "U")

    def kill(self, statusAfterDeath = "K", TCPKill = True):
        #TODO: Better exception handling for killing in general
        if not self.subtasksLoaded:
            self.loadSubtasks()
        responses = [task.kill() for task in self.activeSubTasks]
        #logger.debug(responses)

        responses += [self.updateAttr("status", statusAfterDeath)]
        return all(responses)

    def reset(self):
        response = self.kill("R")
        if not response:
            logger.error("Job Kill was unsuccessful, skipping reset...")
            return False
        renderLayerTracker = ["0" for x in self.renderLayers]
        renderLayerTracker = ",".join(renderLayerTracker)
        with transaction() as t:
            t.cur.execute("UPDATE hydra_jobboard SET renderLayerTracker = %s, failures = '', attempts = '0' WHERE id = %s",
                            (renderLayerTracker, self.id))
        return True

    def archive(self, mode):
        if type(mode) != int:
            mode = 1 if str(mode)[0].lower() == "t" else 0
        return self.updateAttr("archive", mode)

    def createJobCMD(self, platform = "win32"):
        #TODO:Get path with correct platform
        #TODO:Test This
        execs = hydra_executable.fetch()
        self.execsDict = {ex.name: ex.path for ex in execs}

        #Not sure if Maya for Linux or Maya 2016 thing but one of the two is
        #   is appending quotes on the file cmd and messing everything up
        if platform == "win32":
            taskFile = "\"{0}\"".format(self.taskFile)
        else:
            taskFile = self.taskFile

        baseCMD = shlex.split(self.baseCMD)

        if self.jobType == "MayaRender":
            renderList = [self.execsDict[self.execName]]
            renderList += baseCMD
            renderList += ["-s", str(self.startFrame), "-e",
                            str(self.endFrame), "-b", str(self.byFrame),
                             "-rl", str(self.renderLayers), taskFile]

        elif self.jopType == "FusionComp":
            renderList = [self.execsDict[self.execName], taskFile]
            renderList += baseCMD
            renderList += ["/render", "/frames",
                            "{0}..{1}".format(self.startFrame, self.endFrame),
                            "/by", str(self.byFrame), "/exit"]

        return renderList

class hydra_taskboard(hydraObject):
    autoColumn = "id"
    primaryKey = "id"

    def kill(self):
        return True

    def check(self):
        return True

class hydra_capabilities(hydraObject):
    autoColumn = None
    primaryKey = "name"

class hydra_executable(hydraObject):
    autoColumn = None
    primaryKey = "name"

class hydra_holidays(hydraObject):
    autoColumn = None
    primaryKey = "id"
