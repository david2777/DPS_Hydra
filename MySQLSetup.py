"""Setup for MySQL Transactions"""
#Standard
import MySQLdb
import ConfigParser
import os
import shutil
import sys

#Hydra
from LoggingSetup import logger
import Utils
import Constants

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

#Statuses for jobs/tasks
HOLD = 'H'
PAUSED = 'U'                #Job was paused(let running jobs finish)
ERROR = 'E'                 #Job returned a non-zero exit code
READY = 'R'                 #Ready to be run by a render node
FINISHED = 'F'              #Job complete
KILLED = 'K'                #Job was killed
CRASHED = 'C'               #Machine or server software crashed, task was found in host's DB record upon restart

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
            HOLD: 'Hold',
            }

SETTINGS = Constants.SETTINGS

def getDbInfo():
    # open config file
    config = ConfigParser.RawConfigParser()
    # creat a copy if it doesn't exist
    if not os.path.exists(SETTINGS):
        folder = os.path.dirname(SETTINGS)
        logger.info('Check for folder {0}'.format(folder))
        if os.path.exists(folder):
            logger.info('{0} Exists'.format(folder))
        else:
            logger.info('Make {0}'.format(folder))
            os.mkdir(folder)
        cfgFile = os.path.join(os.path.dirname(sys.argv[0]), os.path.basename(SETTINGS))
        logger.info('Copy {0}'.format(cfgFile))
        shutil.copyfile(cfgFile, SETTINGS)

    config.read(SETTINGS)

    #Get server & db names
    host = config.get(section="database", option="host")
    db = config.get(section="database", option="db")
    #Get Username and Password
    username = config.get(section="database", option="username")
    password = config.get(section="database", option="password")

    return host, db, username, password

db_host, db_name, db_username, db_password = getDbInfo()

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
    def fetch(cls, whereClause = "", order = None, limit = None,
               explicitTransaction=None):
        orderClause = "" if order is None else " " + order + " "
        limitClause = "" if limit is None else " LIMIT {0} ".format(limit)
        select = "SELECT * FROM {0} {1} {2} {3}".format(cls.tableName(), whereClause, orderClause, limitClause)
        logger.info(select)

        def doFetch(t):
            t.cur.execute(select)
            names = [desc[0] for desc in t.cur.description]
            return [cls (**dict(zip(names, tuple)))
                    for tuple in t.cur.fetchall()]
        if explicitTransaction:
            return doFetch(explicitTransaction)
        else:
            with transaction() as t:
                return doFetch(t)

    def attributes(self):
        return filter(Utils.nonFlanged, self.__dict__.keys ())

    def insert(self, transaction):
        names = self.attributes()
        values = [getattr(self, name)
                  for name in names]
        nameString = ", ".join(names)
        valueString = ", ".join(len(names) * ["%s"])
        valueStringSimple = ", ".join([str(val) for val in values])
        query = "INSERT INTO %s (%s) VALUES (%s)" % (self.tableName(), nameString, valueString)
        queryRepr = "INSERT INTO %s (%s) VALUES (%s)" % (self.tableName(), nameString, valueStringSimple)
        logger.info(queryRepr)
        transaction.cur.executemany(query, [values])
        if self.autoColumn:
            transaction.cur.execute("SELECT last_insert_id()")
            [id] = transaction.cur.fetchone()
            self.__dict__[self.autoColumn] = id

    def update(self, transaction):
        names = list(self.__dirty__)
        if not names:
            return

        values = ([getattr(self, name) for name in names] + [getattr(self, self.primaryKey)])
        assignments = ", ".join(["%s = %%s" % name for name in names])
        query = "UPDATE %s SET %s WHERE %s = %%s" % (self.tableName(), assignments, self.primaryKey)
        logger.info((query, values))
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
    
class hydra_schedules(tupleObject):
    primaryKey = 'id'
    
class hydra_holidays(tupleObject):
    primaryKey = 'id'


class transaction:
    def __init__(self):
        # open db connection
        self.db = MySQLdb.connect(db_host, user=db_username, passwd = db_password, db=db_name)
        self.cur = self.db.cursor ()
        self.cur.execute("set autocommit = 1")

    def __enter__(self):
        logger.debug("enter transaction %s", self)
        self.cur.execute("start transaction")
        return self

    def __exit__(self, errorType, value, traceback):
        if errorType is None:
            logger.debug("commit %s", self)
            self.cur.execute ("commit")
        else:
            logger.error("rollback %s", self)
            self.cur.execute ("rollback")
        logger.debug("exit transaction %s", self)
        self.db.close()
