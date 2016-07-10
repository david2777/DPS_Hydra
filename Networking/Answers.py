"""Answers for Questions"""

class Answer:
    """Interface for Answer objects"""
    pass

class CMDAnswer(Answer):
    def __init__(self, output):
        self.output = output

class KillCurrentJobAnswer(Answer):
    """An answer which tells whether or not child process was killed."""
    def __init__(self, childKilled):
        self.childKilled = childKilled
