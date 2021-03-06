"""Setup for MySQL Transactions."""
#Standard
import sys
import shlex
import datetime
import os

#Third Party
import MySQLdb

#Hydra
from hydra.logging_setup import logger
from hydra import password_storage
import hydra.hydra_utils as hydra_utils
from networking.questions import KillCurrentTaskQuestion
from networking.connections import TCPConnection

#pylint: disable=E1101,E0203,R0903,W1201

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

niceNamesRev = {v: k for k, v in niceNames.iteritems()}

def get_database_info():
    """Return host, username, password, database name, and port for logging into database"""
    logger.debug("Getting database info...")

    #Get database information
    host = hydra_utils.get_info_from_cfg("database", "host")
    domain = hydra_utils.get_info_from_cfg("network", "dnsDomainExtension")
    if domain and host not in ["localhost", "::1"] and not host.startswith("127."):
        host += ".{}".format(domain)
    databaseName = hydra_utils.get_info_from_cfg("database", "db")
    port = int(hydra_utils.get_info_from_cfg("database", "port"))
    db_username = hydra_utils.get_info_from_cfg("database", "username")

    #Get login information
    al = hydra_utils.get_info_from_cfg("database", "autologin")
    autoLogin = True if al.lower().startswith("t") else False
    if autoLogin:
        _db_password = password_storage.load_credentials(db_username)
        if not _db_password:
            autoLogin = False

    if not autoLogin:
        returnValues = password_storage.qt_prompt()
        if not all(returnValues):
            logger.error("Could not login!")
            sys.exit(1)
        else:
            db_username = returnValues[0]
            _db_password = returnValues[1]

    return host, db_username, _db_password, databaseName, port

def get_this_node():
    """Return a hydra_rendernode class of the current host, None if host not found in the database"""
    thisNode = hydra_rendernode.fetch("WHERE host = %s", (hydra_utils.my_host_name(),),
                                        multiReturn=False)
    #Fetch will return an empty list if it can't find the host, just return none instead
    return thisNode if thisNode else None

class transaction(object):
    """Handle transactions with the database"""

    #Setup db/login info as class variables so that all instnaces already have it
    host, db_username, _db_password, databaseName, port = get_database_info()

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
    """Generic hydra database table class"""
    def __init__(self, **kwargs):
        self.__dict__['__dirty__'] = set()
        for k, v in kwargs.iteritems():
            self.__dict__[k] = v

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if hydra_utils.non_flanged(k):
            self.__dirty__.add(k)
            #logger.debug(('dirty', k, v))

    def __getattr__(self, attr):
        """Return the requested attribute if available, search the database
        if not, raise except if still not found"""
        if attr in self.__dict__.keys():
            return self.attr
        else:
            logger.warning("%s not found in %s, trying to find in database...", attr, self)
            value = self.find_attr(attr)
            if value:
                self.__dict__[attr] = value[0]
                return value[0]
            else:
                err = "Could not find {0} in {1}".format(attr, self.tableName())
                logger.critical(err)
                raise Exception(err)

    def __repr__(self):
        return "{0} {1}".format(self.tableName(), getattr(self, self.primaryKey))

    @classmethod
    def tableName(cls):
        """Return database table name which is the same as the class name"""
        return cls.__name__

    @classmethod
    def fetch(cls, clause="", arguments=tuple(), cols=None, multiReturn=False,
                    explicitTransaction=None):
        """Fetch data from the database and return class object(s)
        ie. thisNode = hydra_rendernode.fetch("WHERE host = %s", ("test",))"""
        #Column Clause
        colStatement = "*"
        if cols:
            cols = [str(x) for x in cols]
            if cls.primaryKey not in cols:
                cols += [cls.primaryKey]
            colStatement = ",".join(cols)

        #Build Select Statement
        select = "SELECT {0} FROM {1} {2}"
        select = select.format(colStatement, cls.tableName(),
                                clause)
        logger.debug(select % arguments)

        #Fetch the data
        if explicitTransaction:
            return cls.doFetch(explicitTransaction, select, arguments, multiReturn)
        else:
            with transaction() as t:
                return cls.doFetch(t, select, arguments, multiReturn)

    @classmethod
    def doFetch(cls, t, select, arguments, multiReturn):
        t.cur.execute(select, arguments)
        names = [desc[0] for desc in t.cur.description]
        returnList = [cls(**dict(zip(names, tup))) for tup in t.cur.fetchall()]
        if multiReturn:
            return returnList
        else:
            return returnList[0] if len(returnList) == 1 else returnList

    def find_attr(self, attr):
        try:
            with transaction() as t:
                x = "SELECT {0} FROM {1} WHERE {2} = %s".format(attr, self.tableName(), self.primaryKey)
                t.cur.execute(x, (getattr(self, self.primaryKey),))
                tup = t.cur.fetchone()
                return tup if tup else None
        except MySQLdb.Error:
            return None

    def attributes(self):
        return filter(hydra_utils.non_flanged, self.__dict__.keys())

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
            logger.debug("done")

        self.__dict__[attr] = value
        return True

#------------------------------------------------------------------------------#
#-----------------------------HYDRA TABLE CLASSES------------------------------#
#------------------------------------------------------------------------------#

class hydra_rendernode(hydraObject):
    """Class representing render node records as listed in the hydra_rendernode table on the database"""
    autoColumn = "id"
    primaryKey = "id"

    def get_task(self, cols=None, explicitTransaction=None):
        if self.task_id:
            return hydra_taskboard.fetch("WHERE id = %s", (self.task_id,),
                                            multiReturn=False, cols=cols,
                                            explicitTransaction=explicitTransaction)
        else:
            return None

    def online(self):
        if self.status == OFFLINE:
            return self.updateAttr("status", IDLE)
        elif self.status == PENDING:
            return self.updateAttr("status", STARTED)
        else:
            logger.debug("No status changes made to %s", self.host)
            return True

    def offline(self):
        newStatus = PENDING if self.status == STARTED else OFFLINE
        return self.updateAttr("status", newStatus)

    def get_off(self):
        response = True
        if self.status == STARTED:
            self.updateAttr("status", PENDING)
            task = self.get_task(["id", "status", "exitCode", "endTime", "host"])
            response = task.kill()

            if response:
                self.status = OFFLINE
                self.task_id = None
                with transaction() as t:
                    self.update(t)

        return response

    def kill_task(self, statusAfterDeath=KILLED):
        if self.status == STARTED and self.task_id:
            taskOBJ = self.get_task(["host", "status", "exitCode", "endTime"])
            logger.debug("Killing task %d on %s", self.task_id, self.host)
            return taskOBJ.kill(statusAfterDeath, True)
        else:
            logger.info("No task to kill on %s", self.host)
            return True

    def get_sql_selector(self):
        return "%{}%".format(self.host)

    @staticmethod
    def is_rendering():
        #TODO:Open connection to render node and check status of self.childProcess
        return True

    @staticmethod
    def resource_check():
        #TODO:Check resources on target machine ie RAM/CPU usage
        return True

class hydra_jobboard(hydraObject):
    """Class representing render job records as listed in the hydra_jobboard table on the database"""
    autoColumn = "id"
    primaryKey = "id"

    def get_tasks(self, cols=None, explicitTransaction=None):
        return hydra_taskboard.fetch("WHERE job_id = %s", (self.id,),
                                            multiReturn=True, cols=cols,
                                            explicitTransaction=explicitTransaction)

    def get_complementary_phase(self):
        #TODO: Return the job object for the job's other phase
        phaseToFind = 1 if self.phase == 2 else 2
        return phaseToFind

    def start(self):
        if self.status in [PAUSED, KILLED]:
            self.status = READY
            taskList = self.get_tasks(["status"])
            with transaction() as t:
                self.update(t)
                for task in taskList:
                    if task.status in [PAUSED, KILLED]:
                        task.status = READY
                        task.update(t)
            return True
        else:
            return None

    def pause(self):
        if self.status in [READY, KILLED]:
            self.status = PAUSED
            taskList = self.get_tasks(["status"])
            with transaction() as t:
                self.update(t)
                for task in taskList:
                    if task.status in [READY, KILLED]:
                        task.status = PAUSED
                        task.update(t)
            return True
        else:
            return None

    def kill(self, statusAfterDeath=KILLED, TCPKill=True):
        subTasks = self.get_tasks(["id", "status", "exitCode", "endTime", "host"])
        responses = [task.kill(statusAfterDeath, TCPKill) for task in subTasks]
        responses += [self.updateAttr("status", statusAfterDeath)]
        for task in subTasks:
            if task.status != FINISHED:
                responses += [task.updateAttr("status", statusAfterDeath)]

        return responses

    def reset(self):
        cols = ["status", "mpf", "host", "startTime", "endTime", "exitCode"]
        taskList = self.get_tasks(cols)
        self.status = PAUSED
        self.mpf = None
        self.attempts = 0
        self.failedNodes = ""
        for task in taskList:
            task.status = PAUSED
            task.mpf = None
            task.host = None
            task.startTime = None
            task.endTime = None
            task.exitCode = None
        with transaction() as t:
            self.update(t)
            _ = [task.update(t) for task in taskList]

    def archive(self, mode):
        """Function for archiving/unarchiveing job. Accepts binary ints, booleans,
        or case insensitive true or false strings."""
        if not isinstance(mode, int):
            mode = 1 if str(mode).lower().startswith("t") else 0
        return self.updateAttr("archived", mode)

    def prioritize(self, priority):
        return self.updateAttr("priority", priority)

class hydra_taskboard(hydraObject):
    """Class representing render task records as listed in the hydra_taskboard table on the database"""
    autoColumn = "id"
    primaryKey = "id"

    def get_job(self, cols=None, explicitTransaction=None):
        return hydra_jobboard.fetch("WHERE id = %s", (self.job_id,),
                                    multiReturn=False, cols=cols,
                                    explicitTransaction=explicitTransaction)

    def get_host(self, cols=None, explicitTransaction=None):
        if self.host:
            return hydra_rendernode.fetch("WHERE host = %s", (self.host,),
                                            multiReturn=False, cols=cols,
                                            explicitTransaction=explicitTransaction)
        else:
            return None

    def get_other_subtasks(self, cols=None, explicitTransaction=None):
        return hydra_taskboard.fetch("WHERE job_id = %s AND id != %s",
                                        (self.job_id, self.id), cols=cols,
                                        explicitTransaction=explicitTransaction)

    def start(self):
        if self.status in [PAUSED, KILLED]:
            job = self.get_job(["status"])
            self.status = READY
            with transaction() as t:
                self.update(t)
                if job.status in [PAUSED, KILLED]:
                    job.status = READY
                    job.update(t)
            return True
        else:
            return None

    def pause(self):
        if self.status in [READY, KILLED]:
            job = self.get_job(["status"])
            self.status = PAUSED
            with transaction() as t:
                self.update(t)
                if job.status in [READY, KILLED]:
                    job.status = PAUSED
                    job.update(t)
            return True
        else:
            return None

    def kill(self, statusAfterDeath=KILLED, TCPKill=True):
        if self.status == STARTED:
            killed = False
            updateNode = True
            node = self.get_host(["status", "task_id"])

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

    def reset(self):
        if self.status != STARTED:
            job = self.get_job(["status"])
            otherTasks = self.get_other_subtasks(["status"])
            statusCheck = any([task.status == STARTED for task in otherTasks])
            self.status = PAUSED
            self.mpf = None
            self.host = None
            self.startTime = None
            self.endTime = None
            self.exitCode = None
            with transaction() as t:
                self.update(t)
                if job.status == KILLED and not statusCheck:
                    job.status = PAUSED
                    job.update(t)
            return True
        else:
            return None

    def send_kill_question(self, newStatus):
        """Kill the current task running on the renderhost. Return True if successful,
        else False"""
        logger.debug('Kill task on %s', self.host)
        node = self.get_host(["ip_addr"])
        connection = TCPConnection(address=node.ip_addr)
        answer = connection.get_answer(KillCurrentTaskQuestion(newStatus))
        if answer is None:
            logger.debug("%s appears to be offline or unresponsive. Treating as dead.", self.host)
        else:
            logger.debug("Child killed return code '%s' for node '%s'", answer, self.host)
            if answer < 0:
                logger.warning("%s tried to kill its job but failed for some reason.", self.host)

        return answer

    def create_task_cmd(self, hydraJob, platform="win32"):
        execs = hydra_executable.fetch(multiReturn=True)
        if platform.startswith("win"):
            execsDict = {ex.name: ex.win32 for ex in execs}
        else:
            execsDict = {ex.name: ex.linux for ex in execs}

        baseCMD = shlex.split(hydraJob.baseCMD, posix=False)
        map(os.path.normpath, baseCMD)

        taskFile = os.path.normpath(hydraJob.taskFile)

        if hydraJob.jobType == "Maya_Render":
            renderList = [execsDict[hydraJob.execName]]
            renderList += baseCMD

            renderList += ["-preRender"]
            preRender = "source hydra_maya_utils;"
            if hydraJob.baseCMD.find("-r redshift") > 0:
                preRender += "DPSHydra_RSPreRender;"
            #TODO: Replace with phase col once that is implemented
            if hydraJob.niceName.find("Phase_01"):
                preRender += "DPSHydra_Phase01PreRender;"
            renderList += [preRender]

            renderList += ["-s", self.startFrame, "-e", self.endFrame, "-b",
                            hydraJob.byFrame, "-rl", hydraJob.renderLayers]

            if hydraJob.frameDirectory:
                frameDir = os.path.normpath(hydraJob.frameDirectory)
                renderList += ["-rd", frameDir]

            renderList += [taskFile]

        elif hydraJob.jobType == "FusionComp":
            renderList = [execsDict[hydraJob.execName], taskFile]
            renderList += baseCMD
            renderList += ["/render", "/quiet", "/frames",
                            "{0}..{1}".format(self.startFrame, self.endFrame),
                            "/by", hydraJob.byFrame, "/exit", "/log TestLog.txt", "/verbose"]

        elif hydraJob.jobType == "BatchFile":
            renderList = [taskFile, hydraJob.baseCMD]

        else:
            logger.error("Bad Job Type!")
            return None

        if hydraJob.jobType == "BatchFile":
            return " ".join([str(x) for x in renderList])
        else:
            return [str(x) for x in renderList]

    def get_log_path(self):
        thisHost = hydra_utils.my_host_name()
        renderLogDir = hydra_utils.get_info_from_cfg("logging", "render_log_path")
        path = os.path.join(renderLogDir, '{:0>10}.log.txt'.format(self.id))
        if self.host and thisHost == self.host:
            return path
        elif self.host:
            _, shortPath = os.path.splitdrive(path)
            newPath = os.path.join("\\\\{}".format(self.host), shortPath)
            return os.path.normpath(newPath)
        else:
            return None

class hydra_capabilities(hydraObject):
    """Simple class representing capability records as listed in the hydra_capabilties table on the database"""
    autoColumn = None
    primaryKey = "name"

class hydra_jobtypes(hydraObject):
    """Simple class representing job type records as listed in the hydra_jobtypes table on the database"""
    autoColumn = None
    primaryKey = "type"

class hydra_executable(hydraObject):
    """Simple class representing executeable records as listed in the hydra_executeable table on the database"""
    autoColumn = None
    primaryKey = "name"

class hydra_holidays(hydraObject):
    """Simple class representing holiday records as listed in the hydra_holidays table on the database"""
    autoColumn = None
    primaryKey = "id"
