#Standard
import os
import sys
import operator
import collections
import datetime

#Hydra
from hydra.logging_setup import logger
import hydra.hydra_sql as sql
import hydra.single_instance as single_instance
import networking.servers as servers
import networking.questions as questions
import networking.connections as connections
import utils.hydra_utils as hydra_utils

class RenderManagementServer(servers.TCPServer):
    def __init__(self):
        port = int(hydra_utils.getInfoFromCFG("manager", "port"))
        self.startServerThread(port)

    #--------------------------------------------------------------------------#
    #-------------------------Process Render Tasks-----------------------------#
    #--------------------------------------------------------------------------#

    def process_render_tasks(self):
        logger.debug("Processing Render Tasks")
        #TODO: Optimize SQL Transactions
        jobList, jobDict, taskList, taskDict = self.get_job_task_data()

        if self.timeout_check(taskList, jobDict):
            jobList, jobDict, taskList, taskDict = self.get_job_task_data()

        renderJobList = self.create_render_jobs(jobList, taskDict)
        logger.debug("RenderJobs: %s", str(renderJobList))

        #Fetch all Nodes and find out which ones are online
        nodeList = sql.hydra_rendernode.fetch("WHERE is_render_node = '1' AND ip_addr IS NOT NULL",
                                                multiReturn=True)
        #startedNodeList = [x for x in nodeList if x.status == sql.STARTED]
        if renderJobList:
            idleNodeList = [x for x in nodeList if x.status == sql.IDLE]
            idleNodeList = self.check_idle_nodes(idleNodeList)

        if renderJobList and len(idleNodeList) < len(renderJobList):
            self.shuffle_queue(renderJobList, taskList, jobDict)

        if renderJobList:
            self.assign_render_jobs(renderJobList, idleNodeList)

        logger.debug("End of loop, waiting...")

    @staticmethod
    def get_job_task_data():
        #Fetch all Jobs
        jobList = sql.hydra_jobboard.fetch("WHERE archived = 0 AND status IN ('R','S')",
                                            multiReturn=True)
        jobDict = {x.id : x for x in jobList}

        #Fetch running tasks
        taskList = sql.hydra_taskboard.fetch("WHERE status = 'S'",
                                                multiReturn=True)
        taskDict = collections.defaultdict(list)
        for task in taskList:
            taskDict[int(task.job_id)].append(task)

        return jobList, jobDict, taskList, taskDict

    @staticmethod
    def timeout_check(taskList, jobDict):
        logger.debug("Checking for timeouts")
        #Task Timeouts
        now = datetime.datetime.now()
        status = False
        for task in taskList:
            try:
                job = jobDict[task.job_id]
            except KeyError:
                job = sql.hydra_jobboard.fetch("WHERE id = %s", (task.job_id,),
                                            cols=["timeout"])
            if job.timeout > 0 and task.last_frame_start_time:
                timeoutDT = datetime.timedelta(seconds=job.timeout)
                timeCheck = (now - task.last_frame_start_time)
                if timeCheck > timeoutDT:
                    logger.debug("Task %s has been timed out after %s seconds (timeout = %s)",
                                    task.id, timeCheck.total_seconds(), job.timeout)
                    task.kill(sql.ERROR)
                    status = True
        return status

    @staticmethod
    def create_render_jobs(jobList, taskDict):
        logger.debug("Creating Render Jobs")
        #Sorting
        sortedJobs = sorted(jobList, key=operator.attrgetter("id"))
        sortedJobs = sorted(sortedJobs, key=operator.attrgetter("priority"),
                            reverse=True)
        #Filtering
        renderJobList = []
        for job in sortedJobs:
            if job.id in taskDict.keys():
                runningTasks = len(taskDict[job.id])
            else:
                runningTasks = 0

            if job.maxNodes > 0 and runningTasks > 0:
                if runningTasks >= int(job.maxNodes):
                    logger.debug("Skipping job %d because it is over the node limit", job.id)

            elif job.attempts >= job.maxAttempts:
                logger.debug("Skipping job %d because it is over the attempt limit", job.id)
                job.updateAttr("status", sql.ERROR)

            else:
                renderJobList.append(job)

        return renderJobList

    @staticmethod
    def check_idle_nodes(idleNodeList):
        logger.debug("Checking Node Status on Idle Nodes")
        onlineList = []
        for node in idleNodeList:
            conn = connections.TCPConnection(address=node.ip_addr)
            question = questions.IsAliveQuestion()
            answer = conn.get_answer(question)
            if not answer:
                logger.debug("%s could not be reached, removing from Idle Nodes", node.host)
            else:
                onlineList.append(node)
        return onlineList

    @staticmethod
    def shuffle_queue(renderJobList, taskList, jobDict):
        """Pretty messy...."""
        logger.debug("Shuffling Render Tasks")
        sortedTasks = sorted(taskList, key=operator.attrgetter("last_frame_start_time"),
                                reverse=True)
        sortedTasks = sorted(sortedTasks, key=operator.attrgetter("priority"))
        sortedJobs = sorted(renderJobList, key=operator.attrgetter("priority"), reverse=True)

        #TODO:This is very messy, should probably clean it up...
        i = 0
        limit = len(sortedJobs) - 1
        for task in sortedTasks:
            if i > limit:
                logger.debug("Exiting shuffle due to limit reached")
                return
            breakStatus = False
            try:
                parentJob = jobDict[task.job_id]
            except KeyError:
                logger.warning("Could not find job %s in allJobs", task.job_id)
                parentJob = sql.hydra_jobboard.fetch("WHERE id = %s", (task.job_id,),
                                            cols=["priority"])
            while not breakStatus:
                job = sortedJobs[i]
                #If the job priority is 25% or more higher than the task's,
                #   kill the task to make room for the new job
                killCalc = (float(parentJob.priority) / float(job.priority))
                if killCalc < .75:
                    logger.debug("Killing task %s due to killCalc of %s",
                                    task.id, killCalc)
                    #task.kill(KILLED)
                    breakStatus = True
                    i += 1
                else:
                    logger.debug("Exiting shuffle due to killCalc of %s from task %s",
                                    killCalc, task.id)
                    return

    def assign_render_jobs(self, renderJobList, idleNodeList):
        #pylint: disable=E1101
        if not renderJobList:
            logger.debug("No Ready Jobs found, skipping assignment")
            return True
        if not idleNodeList:
            logger.debug("No Idle Nodes found, skipping assignment")
            return True
        logger.debug("Assigning Render Tasks")
        for node in idleNodeList:
            for job in renderJobList:
                response = self.filter_job(job, node)
                if response:
                    #Create task object and insert into databse
                    task = sql.hydra_taskboard(job_id=job.id, host=node.host,
                                            status=sql.STARTED,
                                            startTime=datetime.datetime.now(),
                                            priority=job.priority,
                                            startFrame=job.startFrame,
                                            endFrame=job.endFrame,
                                            currentFrame=job.startFrame)
                    with sql.transaction() as t:
                        task.insert(t)
                    #Send task to render node, record result in databse
                    if self.send_task(node, task, job):
                        node.status = sql.STARTED
                        node.task_id = task.id
                        with sql.transaction() as t:
                            node.update(t)
                        renderJobList.remove(job)
                        break
                    else:
                        logger.debug("Cleaning up task %s", task.id)
                        task.status = sql.KILLED
                        task.endTime = datetime.datetime.now()
                        task.exitCode = 1337
                        #Mark job failure? Offline node?
                        with sql.transaction() as t:
                            task.update(t)
                        break

    @staticmethod
    def filter_job(job, node):
        if job.priority < node.minPriority:
            logger.debug("Skipping job %d because it does not meet %s's minPriority requirement", job.id, node.host)
            return False

        if job.failedNodes and job.failedNodes != "":
            failures = job.failedNodes.split(",")
            if node.host in failures:
                logger.debug("Skipping job %d because it has failed on node %s in the past", job.id, node.host)
                return False

        if job.requirements and job.requirements != "":
            jobReqs = job.requirements.split(",")
            nodeCaps = node.capabilities.split(" ")
            checker = [x in nodeCaps for x in jobReqs]
            if not all(checker):
                logger.debug("Skipping job %d because node %s cannot meet its feature requirements", job.id, node.host)
                return False

        #If all of the above tests pass
        return True

    @staticmethod
    def send_task(node, task, job):
        logger.debug("Assigning task with id %d to node %s", task.id, node.host)
        connection = connections.TCPConnection(address=node.ip_addr)
        response = connection.get_answer(questions.StartRenderQuestion(job, task))
        if response:
            logger.debug("Task %d was accepted on %s", task.id, node.host)
        else:
            logger.error("Task %d was declined on %s", task.id, node.host)
        return response

    #--------------------------------------------------------------------------#
    #-------------------------Incoming TCP Handlers----------------------------#
    #--------------------------------------------------------------------------#
    @staticmethod
    def is_alive():
        return True

    @staticmethod
    def progress_update_handler(updateType, data):
        logger.debug("Progress Update: %s", str(data))
        if updateType == "TaskProgress" or updateType == "tp":
            renderNode = sql.hydra_rendernode.fetch("WHERE host = %s", (data["thisNode"],),
                                                    cols=["task_id"])
            task = sql.hydra_taskboard.fetch("WHERE id = %s", (renderNode.task_id,),
                                            cols=["currentFrame", "currentRenderLayer",
                                                    "last_frame_start_time", "mpf",
                                                    "job_id", "frame_count"])
            job = sql.hydra_jobboard.fetch("WHERE id = %s", (task.job_id,),
                                            cols=["frame_count", "startFrame",
                                                    "endFrame", "byFrame"])
            try:
                job.frame_count += 1
                task.frame_count += 1
                task.currentFrame = data["currentFrame"]
                task.currentRenderLayer = data["renderLayer"]
                oldTime = task.last_frame_start_time
                task.last_frame_start_time = datetime.datetime.now()
                if oldTime:
                    tdiff = task.last_frame_start_time - oldTime
                    if task.mpf:
                        tsecs = ((task.mpf.total_seconds() + tdiff.total_seconds()) / 2)
                        task.mpf = datetime.timedelta(seconds=tsecs)
                    else:
                        task.mpf = tdiff
                with sql.transaction() as t:
                    task.update(t)
                    job.update(t)
                return True
            except KeyError:
                logger.error("Key error on ProgressUpdate Update. Data: %s", str(data))
                return False

        elif updateType == "TaskCompletion" or updateType == "tc":
            taskCols = ["job_id", "host", "exitCode", "endTime", "mpf", "status"]
            jobCols = ["mpf", "status", "attempts", "failedNodes", "maxAttempts"]
            nodeCols = ["status", "task_id"]
            try:
                task = sql.hydra_taskboard.fetch("WHERE id = %s", (data["task_id"],),
                                                    cols=taskCols)
                job = sql.hydra_jobboard.fetch("WHERE id = %s", (task.job_id,),
                                                cols=jobCols)
                node = sql.hydra_rendernode.fetch("WHERE host = %s", (task.host,),
                                                    cols=nodeCols)
                with sql.transaction() as t:
                    t.cur.execute("SELECT count(id) FROM hydra_taskboard WHERE job_id = %s AND status = 'S'", (task.job_id,))
                    taskCount = t.cur.fetchall()
                taskCount = int(taskCount[0][0]) - 1

                node.status = sql.IDLE if node.status == sql.STARTED else sql.OFFLINE
                node.task_id = None

                task.exitCode = data["exitCode"]
                task.endTime = data["endTime"]

                totalFrameRange = range(job.startFrame, (job.endFrame + 1))[::job.byFrame]
                targetFrameCount = len(totalFrameRange)

                if task.mpf:
                    if job.mpf:
                        job.mpf = ((job.mpf.total_seconds() + task.mpf.total_seconds()) / 2)
                    else:
                        job.mpf = task.mpf

                if task.exitCode == 0:
                    task.status = sql.FINISHED
                    #TODO: Cleanup log?
                    if taskCount <= 0:
                        job.status = sql.FINISHED
                        if job.frame_count != targetFrameCount and job.byFrame != 1:
                            logger.warning("Job %s totalFrameRange is %s. %s expected.", job.id, totalFrameRange, targetFrameCount)
                else:
                    newStatus = data["statusAfterDeath"]
                    task.status = newStatus if newStatus else sql.ERROR
                    if task.status == sql.ERROR:
                        job.attempts += 1
                        if job.failedNodes == "":
                            job.failedNodes = task.host
                        else:
                            job.failedNodes += task.host
                        if job.attempts >= job.maxAttempts:
                            job.status = sql.ERROR

                with sql.transaction() as t:
                    job.update(t)
                    task.update(t)
                    node.update(t)

                return True
            except KeyError:
                logger.error("Key error on TaskCompletion Update. Data: %s", str(data))
                return False
        else:
            logger.error("Bad UpdateType!")
            return False

    @staticmethod
    def change_node_status(node, newStatus, force=False):
        if newStatus == sql.IDLE:
            if force:
                return node.updateAttr("status", sql.IDLE)
            else:
                return node.online()
        elif newStatus == sql.OFFLINE:
            if force:
                return node.updateAttr("status", sql.OFFLINE)
            else:
                return node.offline()
        elif newStatus == sql.GETOFF:
            return None
        else:
            return None

    @staticmethod
    def unstick_node(node, nodeStatus, taskStatus):
        task = sql.hydra_taskboard.fetch("WHERE id = %s", (node.task_id,))
        task.status = taskStatus
        task.endTime = datetime.datetime.now()
        task.exitCode = 1

        node.status = nodeStatus
        node.task_id = None
        node.last_frame_start_time = None

        with sql.transaction() as t:
            task.update(t)
            node.update(t)

def main():
    logger.info("starting in %s", os.getcwd())
    logger.info("arglist is %s", sys.argv)

    #Check for other RenderNode isntances
    lockFile = single_instance.InstanceLock("HydraRenderManager")
    lockStatus = lockFile.isLocked()
    logger.debug("Lock File Status: %s", lockStatus)
    if not lockStatus:
        logger.critical("Only one RenderManager is allowed to run at a time! Exiting...")
        sys.exit(-1)

    socketServer = RenderManagementServer()
    socketServer.createIdleLoop("Process_Render_Tasks_Thread",
                                socketServer.process_render_tasks,
                                interval=10)

if __name__ == "__main__":
    main()
