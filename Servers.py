#Standard
import SocketServer
import threading
import pickle
import traceback
import time

#Hydra
import Constants
from LoggingSetup import logger
#Note that this imports Questions at the bottom for some reason

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

class Server:
    def createIdleLoop(self, interval, function):
        self.idleThread = threading.Thread(target = self.idleLoop,
                                            name = "idle thread",
                                            args = (interval, function)
                                            )
        self.idleThread.start()

    def idleLoop(self, interval, function):
        while True:
            try:
                function()
            except Exception, e:
                logger.error("Idle loop exception: {0}".format(traceback.format_exc(e)))
            time.sleep(interval)

class LocalServer(Server):
    pass

class MySocketServer(SocketServer.TCPServer):
    allow_reuse_address = True

class TCPServer(Server):
    def __init__( self,
                  port = Constants.PORT,
                  ):

        MyTCPHandler.TCPserver = self
        logger.info('Open TCPServer Socket @ Port {0}'.format(port))
        self.serverObject = MySocketServer(("", port), MyTCPHandler)
        self.serverThread = threading.Thread(target = runTheServer,
                                              name = "server thread",
                                              args = (self.serverObject,)
                                              )
        self.serverThread.start()

    def shutdown(self):
        logger.debug("Shutting down TCPServer...")
        self.serverObject.shutdown()

def runTheServer(serverObject):
    logger.info ("Off to the races")
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
            logger.error("Exception caught: {0}".format(traceback.format_exc()))
