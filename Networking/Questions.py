"""Questions you can ask TCP Servers"""
#Standard
import subprocess

#pylint: disable=R0903,W0613

class StartRenderQuestion(object):
    def __init__(self, job, task):
        self.job = job
        self.task = task
    def compute_answer(self, server):
        return server.startRenderTask(self.job, self.task)

class CMDQuestion(object):
    """A Question for running arbitrary commands on a server."""
    def __init__(self, args):
        self.args = args
    def compute_answer(self, server):
        return subprocess.check_output(self.args, stderr=subprocess.STDOUT)

class KillCurrentTaskQuestion(object):
    def __init__(self, statusAfterDeath):
        self.statusAfterDeath = statusAfterDeath
    def compute_answer(self, server):
        server.killCurrentJob(self.statusAfterDeath)
        return server.childKilled

class ProgressUpdateQuestion(object):
    def __init__(self, node, data):
        self.node = node
        self.data = data
    def compute_answer(self, server):
        return server.progress_update_handler(self.node, self.data)
