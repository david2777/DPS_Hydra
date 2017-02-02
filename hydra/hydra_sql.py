"""Setup for MySQL Transactions."""
#Standard
import sys
import shlex
import datetime
import os

#Third Party
import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#Hydra
import Constants
from hydra.logging_setup import logger
from hydra import password_storage
from networking.questions import KillCurrentTaskQuestion
from networking.connections import TCPConnection
import utils.hydra_utils as hydra_utils

#pylint: disable=E1101,E0203

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

#Statuses for render nodes
IDLE = 'I'                  #Ready to accept jobs
OFFLINE = 'O'               #Not ready to accept jobs
PENDING = 'P'               #Offline after current job is complete
GETOFF = 'G'

niceNames = {STARTED: 'Started',
            READY: 'Ready',
            PAUSED: 'Paused',
            FINISHED: 'Finished',
            KILLED: 'Killed',
            ERROR: 'Error',
            CRASHED: 'Crashed',
            TIMEOUT: "Timed Out",
            IDLE: 'Idle',
            OFFLINE: 'Offline',
            PENDING: 'Pending',
            GETOFF: 'GetOff'
            }

niceNamesRev = {v: k for k, v in niceNames.items()}

def getDatabaseInfo():
    logger.debug("Finding login information...")

    #Get databse information
    host = hydra_utils.getInfoFromCFG("database", "host")
    domain = hydra_utils.getInfoFromCFG("network", "dnsDomainExtension").replace(" ", "")
    if domain != "" and host != "localhost":
        host += ".{}".format(domain)
    databaseName = hydra_utils.getInfoFromCFG("database", "db")
    port = int(hydra_utils.getInfoFromCFG("database", "port"))
    db_username = hydra_utils.getInfoFromCFG("database", "username")

    #Get login information
    autoLogin = hydra_utils.getInfoFromCFG("database", "autologin")
    autoLogin = True if str(autoLogin).lower()[0] == "t" else False
    if autoLogin:
        _db_password = password_storage.loadCredentials(db_username)
        if not _db_password:
            autoLogin = False

    if not autoLogin:
        returnValues = password_storage.qtPrompt()
        if not returnValues[0] or not returnValues[1]:
            logger.error("Could not login!")
            sys.exit(1)
        else:
            db_username = returnValues[0]
            _db_password = returnValues[1]

    return host, db_username, _db_password, databaseName, port

class transaction(object):
    #pylint: disable=R0903
    host, db_username, _db_password, databaseName, port = getDatabaseInfo()

    def __init__(self):
        #Open DB Connection
        self.db = MySQLdb.connect(host=self.host, user=self.db_username,
                                    passwd=self._db_password, db=self.databaseName,
                                    port=self.port)
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

class hydraObject(object):
    def __init__(self, **kwargs):
        self.__dict__['__dirty__'] = set()
        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if hydra_utils.nonFlanged(k):
            self.__dirty__.add(k)
            #logger.debug(('dirty', k, v))

    def __repr__(self):
        return "{0} {1}".format(self.tableName(), getattr(self, self.primaryKey))

    @classmethod
    def tableName(cls):
        return cls.__name__

    @classmethod
    def fetch(cls, whereClause="", whereTuple=None, cols=None,
                    orderTuples=None, limit=None, multiReturn=False,
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
        select = select.format(colStatement, cls.tableName(), whereClause,
                                orderClause, limitClause)
        #pylint: disable=W1201
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
        else:
            return returnList[0] if len(returnList) == 1 else returnList

    def attributes(self):
        return filter(hydra_utils.nonFlanged, self.__dict__.keys())

    def vals(self):
        return self.__dict__

    def insert(self, trans):
        names = self.attributes()
        values = [getattr(self, name) for name in names]
        nameString = ", ".join(names)
        valueString = ", ".join(["%s" for _ in range(len(names))])
        query = "INSERT INTO {0} ({1}) VALUES ({2})".format(self.tableName(), nameString, valueString)

        trans.cur.executemany(query, [values])
        if self.autoColumn:
            trans.cur.execute("SELECT last_insert_id()")
            [insert_id] = trans.cur.fetchone()
            self.__dict__[self.autoColumn] = insert_id

    def update(self, trans):
        names = list(self.__dirty__)
        if not names:
            logger.info("Nothing to update on %s", self.tableName())
            return

        values = ([getattr(self, n) for n in names] + [getattr(self, self.primaryKey)])
        assignments = ", ".join(["{} = %s".format(n) for n in names])
        query = "UPDATE {0} SET {1} WHERE {2} = %s".format(self.tableName(), assignments, self.primaryKey)
        logger.debug((query, values))
        trans.cur.executemany(query, [values])
        return True

    def updateAttr(self, attr, value):
        if attr not in self.attributes():
            logger.error("Attr %s not found in %s", attr, self.tableName())
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
        if self.status == "O":
            return self.updateAttr("status", "I")
        elif self.status == "P":
            return self.updateAttr("status", "S")
        else:
            logger.debug("No status changes made to %s", self.host)
            return True

    def offline(self):
        newStatus = "P" if self.status == "S" else "O"
        return self.updateAttr("status", newStatus)

    def getOff(self):
        response = True
        if self.status == "S":
            self.updateAttr("status", PENDING)
            task = hydra_taskboard.fetch("WHERE id  = %s", (self.task_id,),
                                        cols=["id", "status", "exitCode", "endTime", "host"])
            response = task.kill()

            if response:
                self.status = OFFLINE
                self.task_id = None
                with transaction() as t:
                    self.update(t)

        return response

    def kill_task(self, statusAfterDeath=KILLED):
        if self.status == "S" and self.task_id:
            taskOBJ = hydra_taskboard.fetch("WHERE id = %s", self.task_id,
                                            cols=["host", "status", "exitCode",
                                                    "endTime"])
            logger.debug("Killing task %d on %s", self.task_id, self.host)
            return taskOBJ.kill(statusAfterDeath, True)
        else:
            logger.info("No task to kill on %s", self.host)
            return True

    @staticmethod
    def is_rendering():
        #TODO:Open connection to render node and check status of self.childProcess
        return True

    @staticmethod
    def resource_check():
        #TODO:Check resources on target machine ie RAM/CPU usage
        return True

class hydra_jobboard(hydraObject):
    autoColumn = "id"
    primaryKey = "id"

    def start(self):
        return self.updateAttr("status", "R")

    def pause(self):
        return self.updateAttr("status", "U")

    def kill(self, statusAfterDeath="K", TCPKill=True):
        subTasks = hydra_taskboard.fetch("WHERE job_id = %s AND status = 'S'", (self.id,),
                                        cols=["id", "status", "exitCode", "endTime", "host"],
                                        multiReturn=True)
        responses = [task.kill(statusAfterDeath, TCPKill) for task in subTasks]

        responses += [self.updateAttr("status", statusAfterDeath)]
        return responses

    def reset(self, resetData):
        logger.debug("Resetting job %s with data: %s", self.id, resetData)
        self.status = PAUSED
        self.frame_count = 0
        self.renderLayers = resetData[0]
        self.startFrame = resetData[1]
        self.endFrame = resetData[2]
        self.byFrame = resetData[3]
        if resetData[4]:
            self.failedNodes = ""
            self.attempts = 0

        with transaction() as t:
            self.update(t)

        return 0

    def archive(self, mode):
        """Function for archiving/unarchiveing job. Accepts binary ints, booleans,
        or case insensitive true or false strings."""
        if not isinstance(mode, int):
            mode = 1 if str(mode)[0].lower() == "t" else 0
        return self.updateAttr("archived", mode)

    def prioritize(self, priority):
        return self.updateAttr("priority", priority)

class hydra_taskboard(hydraObject):
    autoColumn = "id"
    primaryKey = "id"

    def create_task_cmd(self, hydraJob, platform="win32"):
        execs = hydra_executable.fetch(multiReturn=True)
        if platform == "win32":
            execsDict = {ex.name: ex.win32 for ex in execs}
        else:
            execsDict = {ex.name: ex.linux for ex in execs}

        baseCMD = shlex.split(hydraJob.baseCMD)

        if hydraJob.jobType == "Maya_Render":
            renderList = [execsDict[hydraJob.execName]]
            renderList += baseCMD

            #TODO: do this better
            if hydraJob.baseCMD.find("-r redshift") > 0:
                renderList += ["-preRender", "source hydra_maya_utils;DPSHydra_RSPreRender;"]

            renderList += ["-postFrame", "source hydra_maya_utils;DPSHydra_TaskUpdate;",
                            "-s", self.startFrame, "-e", self.endFrame, "-b",
                            hydraJob.byFrame, "-rl", hydraJob.renderLayers]

            if hydraJob.frameDirectory:
                renderList += ["-rd", hydraJob.frameDirectory]

            renderList += [hydraJob.taskFile]

        elif hydraJob.jobType == "FusionComp":
            renderList = [execsDict[hydraJob.execName], hydraJob.taskFile]
            renderList += baseCMD
            renderList += ["/render", "/quiet", "/frames",
                            "{0}..{1}".format(self.startFrame, self.endFrame),
                            "/by", hydraJob.byFrame, "/exit", "/log TestLog.txt", "/verbose"]

        elif hydraJob.jobType == "BatchFile":
            renderList = [hydraJob.taskFile, hydraJob.baseCMD]

        else:
            logger.error("Bad Job Type!")
            return None

        if hydraJob.jobType == "BatchFile":
            return " ".join([str(x) for x in renderList])
        else:
            return [str(x) for x in renderList]

    def send_kill_question(self, newStatus):
        """Kill the current task running on the renderhost. Return True if successful,
        else False"""
        logger.debug('Kill task on %s', self.host)
        node = hydra_rendernode.fetch("WHERE task_id = %s", (self.id,),
                                        cols=["ip_addr"])
        connection = TCPConnection(address=node.ip_addr)
        answer = connection.get_answer(KillCurrentTaskQuestion(newStatus))
        if answer is None:
            logger.debug("%s appears to be offline or unresponsive. Treating as dead.", self.host)
        else:
            logger.debug("Child killed return code '%s' for node '%s'", answer, self.host)
            if answer < 0:
                logger.warning("%s tried to kill its job but failed for some reason.", self.host)

        return answer


    def kill(self, statusAfterDeath="K", TCPKill=True):
        if self.status == STARTED:
            killed = False
            updateNode = True
            node = hydra_rendernode.fetch("WHERE host = %s", (self.host,),
                                            cols=["status", "task_id"])

            if TCPKill:
                if node.task_id != self.id:
                    logger.warning("Node is not running the given task! Marking as dead.")
                    updateNode = False

                else:
                    killed = self.send_kill_question(statusAfterDeath)
                    #If killed returns None then the node is probably offline
                    if killed:
                        return True if killed > 0 else False

            #If it was not killed by the node then we need to mark it as dead here instead
            if not killed:
                logger.debug("TCPKill recived None, marking task as killed")
                self.status = statusAfterDeath
                self.exitCode = 1
                self.endTime = datetime.datetime.now()
                with transaction() as t:
                    self.update(t)
                    if updateNode:
                        node.status = IDLE if node.status == STARTED else OFFLINE
                        node.task_id = None
                        node.update(t)
                return True
        else:
            logger.debug("Task Kill is skipping task %s because of status %s", self.id, self.status)
            return True

    def get_log_path(self):
        thisHost = hydra_utils.myHostName()
        path = os.path.join(Constants.RENDERLOGDIR, '{:0>10}.log.txt'.format(self.id))
        if thisHost == self.host:
            return path
        else:
            _, shortPath = os.path.splitdrive(path)
            newPath = os.path.join("\\\\{}".format(self.host), shortPath)
            newPath = os.path.normpath(newPath)
            if sys.platform == "win32":
                return "\\{}".format(newPath)
            else:
                return newPath

class hydra_capabilities(hydraObject):
    autoColumn = None
    primaryKey = "name"

class hydra_jobtypes(hydraObject):
    autoColumn = None
    primaryKey = "type"

class hydra_executable(hydraObject):
    autoColumn = None
    primaryKey = "name"

class hydra_holidays(hydraObject):
    autoColumn = None
    primaryKey = "id"
