"""Setups for various local servers"""
#Standard
import SocketServer
import threading
import pickle
import traceback
import time

#Hydra
import Constants
from Setups.LoggingSetup import logger
from Utilities.Utils import getInfoFromCFG

class Server:
    def createIdleLoop(self, interval, function):
        self.idleThread = threading.Thread(target = self.idleLoop,
                                            name = "Idle Thread",
                                            args = (interval, function))

        self.idleThread.start()
        #Without this sleep it returns True even if the server isn't started
        time.sleep(.1)
        if not self.idleThread.isAlive():
            self.threadVar = False
            logger.critical("Server apprears to have failed.")

    def idleLoop(self, interval, function):
        """Class calling this must have self.threadVar set to True"""
        while self.threadVar:
            function()
            time.sleep(interval)

class MySocketServer(SocketServer.TCPServer):
    allow_reuse_address = True

class TCPServer(Server):
    def __init__(self, port = None):
        if not port:
            port = int(getInfoFromCFG("network", "port"))
        HydraTCPHandler.TCPserver = self
        logger.debug('Open TCPServer Socket @ Port {0}'.format(port))
        self.threadVar = True
        self.serverObject = MySocketServer(("", port), HydraTCPHandler)
        self.serverThread = threading.Thread(target = runTheServer,
                                              name = "Server Thread",
                                              args = (self.serverObject,))
        self.serverThread.start()
        if not self.serverThread.isAlive():
            raise
        return self

    def shutdown(self):
        logger.debug("Shutting down TCPServer...")
        self.threadVar = False
        self.serverObject.shutdown()

def runTheServer(serverObject):
    logger.debug("Off to the races!")
    serverObject.serve_forever()

class HydraTCPHandler(SocketServer.StreamRequestHandler):
    TCPserver = None
    def handle(self):
        try:
            questionBytes = self.rfile.read()
            question = pickle.loads(questionBytes)
            answer = question.computeAnswer(self.TCPserver)
            answerBytes = pickle.dumps(answer)
            self.wfile.write(answerBytes)
        except:
            logger.error("Exception caught in Servers: {0}".format(traceback.format_exc()))
