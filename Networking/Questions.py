"""Questions you can ask nodes, can probably be cleaned up a bit to get rid
of legacy stuff that isn't used anymore."""
#Standard
import subprocess
import exceptions

class Question:
    """Interface for Question objects."""
    def computeAnswer(self, server):
        """ Override this method when creating a Question subclass code in this
        method will be run by the server"""
        raise exceptions.NotImplementedError

class IsAliveQuestion(Question):
    """A simple Question for checking if a server is alive"""
    def computeAnswer(self, server):
        return True

class StartRenderQuestion(Question):
    def __init__(self, job, task):
        self.job = job
        self.task = task
    def computeAnswer(self, server):
        response = server.processRenderTask(self.job, self.task)
        return response

class CMDQuestion(Question):
    """A Question for running arbitrary commands on a server."""
    def __init__(self, args):
        self.args = args
    def computeAnswer(self, server):
        output = subprocess.check_output(self.args, stderr=subprocess.STDOUT)
        return output

class KillCurrentTaskQuestion(Question):
    def __init__(self, statusAfterDeath):
        self.statusAfterDeath = statusAfterDeath
    def computeAnswer(self, server):
        server.killCurrentJob(self.statusAfterDeath)
        return server.childKilled
