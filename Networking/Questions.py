"""Questions you can ask nodes, can probably be cleaned up a bit to get rid
of legacy stuff that isn't used anymore."""
#Standard
import subprocess

#pylint: disable=R0903,W0613

class IsAliveQuestion(object):
    """A simple Question for checking if a server is alive"""
    @staticmethod
    def computeAnswer(server):
        return True

class StartRenderQuestion(object):
    def __init__(self, job, task):
        self.job = job
        self.task = task
    def computeAnswer(self, server):
        response = server.startRenderTask(self.job, self.task)
        return response

class CMDQuestion(object):
    """A Question for running arbitrary commands on a server."""
    def __init__(self, args):
        self.args = args
    def computeAnswer(self, server):
        output = subprocess.check_output(self.args, stderr=subprocess.STDOUT)
        return output

class KillCurrentTaskQuestion(object):
    def __init__(self, statusAfterDeath):
        self.statusAfterDeath = statusAfterDeath
    def computeAnswer(self, server):
        server.killCurrentJob(self.statusAfterDeath)
        return server.childKilled
