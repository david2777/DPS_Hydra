"""Questions you can ask TCP Servers"""
#pylint: disable=R0903,W0613,R0201

class StartRenderQuestion(object):
    def __init__(self, job, task):
        self.job = job
        self.task = task
    def compute_answer(self, server):
        return server.start_render_task(self.job, self.task)

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
