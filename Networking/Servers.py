"""Setups for various local servers"""
#Standard
import SocketServer
import threading
import pickle

#Hydra
from Setups.LoggingSetup import logger

class Server(object):
    allThreads = {}
    def createIdleLoop(self, threadName, targetFunction, interval=None):
        self.targetFunction = targetFunction
        self.interval = interval
        self.threadName = threadName
        self.stopEvent = threading.Event()
        self.allThreads[threadName] = self.stopEvent
        self.threadOBJ = threading.Thread(target=self.tgt, name=self.threadName)
        self.threadOBJ.deamon = True
        self.threadOBJ.start()

    def tgt(self):
        if self.interval:
            while not self.stopEvent.is_set():
                self.targetFunction()
                self.stopEvent.wait(self.interval)
        else:
            while not self.stopEvent.is_set():
                self.targetFunction()

    def shutdown(self):
        for threadName, stopEvent in self.allThreads.iteritems():
            logger.info("Killing %s Thread...", threadName)
            stopEvent.set()

class TCPServer(Server):
    def startServerThread(self, port):
        HydraTCPHandler.TCPserver = self
        logger.debug("Open TCPServer Socket @ Port %s", port)
        self.serverObject = MySocketServer(("", port), HydraTCPHandler)
        self.serverThread = self.createIdleLoop("TCP_Server_Thread",
                                                self.serverObject.serve_forever)

    def shutdown(self):
        self.serverObject.shutdown()
        Server.shutdown(self)

class MySocketServer(SocketServer.TCPServer):
    allow_reuse_address = True

class HydraTCPHandler(SocketServer.StreamRequestHandler):
    TCPserver = None
    def handle(self):
        questionBytes = self.rfile.read()
        question = pickle.loads(questionBytes)
        answer = question.computeAnswer(self.TCPserver)
        answerBytes = pickle.dumps(answer)
        self.wfile.write(answerBytes)
