"""Setups for various local servers"""
#Standard
import SocketServer
import threading
import pickle
import traceback
import time

#Hydra
import Constants
from LoggingSetup import logger

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra


class Server:
    def createIdleLoop(self, interval, function):
        self.idleThread = threading.Thread(target = self.idleLoop,
                                            name = "Idle Thread",
                                            args = (interval, function))
        self.idleThread.start()
        #Without this sleep it returns True even if the server isn't started
        time.sleep(.1)
        if not self.idleThread.isAlive():
            raise Exception

    def idleLoop(self, interval, function):
        """Class calling this must have self.threadVar set to True"""
        while self.threadVar:
            function()
            time.sleep(interval)

class LocalServer(Server):
    pass

class MySocketServer(SocketServer.TCPServer):
    allow_reuse_address = True

class TCPServer(Server):
    def __init__(self, port = Constants.PORT):
        MyTCPHandler.TCPserver = self
        logger.info('Open TCPServer Socket @ Port {0}'.format(port))
        self.threadVar = True
        self.serverObject = MySocketServer(("", port), MyTCPHandler)
        self.serverThread = threading.Thread(target = runTheServer,
                                              name = "Server Thread",
                                              args = (self.serverObject,))
        self.serverThread.start()
        if not self.serverThread.isAlive():
            raise

        return self

    def shutdown(self):
        logger.info("Shutting down TCPServer...")
        self.threadVar = False
        self.serverObject.shutdown()

def runTheServer(serverObject):
    logger.info ("Off to the races!")
    serverObject.serve_forever()

class MyTCPHandler(SocketServer.StreamRequestHandler):
    TCPserver = None #The Hydra server object, NOT the SocketServer.
    def handle( self ):
        logger.info ("request")
        try:
            questionBytes = self.rfile.read()
            question = pickle.loads(questionBytes)
            logger.debug(question)

            answer = question.computeAnswer(self.TCPserver)

            answerBytes = pickle.dumps( answer )
            self.wfile.write( answerBytes )
        except:
            logger.error("Exception caught in Servers: {0}".format(traceback.format_exc()))
