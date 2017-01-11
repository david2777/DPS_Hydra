"""Questions you can ask TCP Servers"""
#Standard
import subprocess

#pylint: disable=R0903,W0613,R0201

class StartRenderQuestion(object):
    def __init__(self, job, task):
        self.job = job
        self.task = task
    def compute_answer(self, server):
        return server.start_render_task(self.job, self.task)

class CMDQuestion(object):
    """A Question for running arbitrary commands on a server."""
    def __init__(self, args):
        self.args = args
    def compute_answer(self, server):
        return subprocess.check_output(self.args, stderr=subprocess.STDOUT)

class IsAliveQuestion(object):
    """A Question for running arbitrary commands on a server."""
    def compute_answer(self, server):
        return server.is_alive()

class KillCurrentTaskQuestion(object):
    def __init__(self, statusAfterDeath):
        self.statusAfterDeath = statusAfterDeath
    def compute_answer(self, server):
        server.kill_current_job(self.statusAfterDeath)
        return server.childKilled

class ProgressUpdateQuestion(object):
    def __init__(self, updateType, data):
        self.updateType = updateType
        self.data = data
    def compute_answer(self, server):
        return server.progress_update_handler(self.updateType, self.data)

class ChangeNodeStatusQuestion(object):
    def __init__(self, node, newStatus):
        self.node = node
        self.newStatus = newStatus
    def compute_answer(self, server):
        return server.change_node_status(self.node, self.newStatus)

class UnstickNodeQuestion(object):
    def __init__(self, node, nodeStatus, taskStatus):
        self.node = node
        self.nodeStatus = nodeStatus
        self.taskStatus = taskStatus
    def compute_answer(self, server):
        return server.unstick_node(self.node, self.nodeStatus, self.taskStatus)
