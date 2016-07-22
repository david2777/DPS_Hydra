"""A Connection allows a Client to ask a Server for an Answer to a Question."""
#Standard
import exceptions
import socket
import pickle

#Hydra
import Networking.Servers as Servers
import Constants
from Setups.LoggingSetup import logger
from Utilities.Utils import getInfoFromCFG

class Connection:
    "A connection to a Hydra server. Base class, must be subclassed."
    def getAnswer(self, question):
        """Protocol for getting the server to answer a question. Must be implemented in subclasses."""
        raise exceptions.NotImplementedError

class TCPConnection(Connection):
    """A connection to a remote Hydra server, using TCP"""
    def __init__(self, hostname = None, port = None):
        """Constructor. Supply a hostname to connect to another computer."""
        if not hostname:
            hostname = getInfoFromCFG("database", "host")
        if not port:
            port = int(getInfoFromCFG("network", "port"))
        self.hostname = hostname
        self.port = port

    def getAnswer(self, question):
        """Send the question to a remote server and get an answer back"""
        #Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #Connect to the server
            logger.debug('TCP Connect to {0} {1}'.format(self.hostname, self.port))
            if self.hostname == None:
                return None
            try:
                sock.connect((self.hostname, self.port))
                #Convert the question to ASCII
                questionBytes = pickle.dumps(question)
                #Send the question
                sock.sendall(questionBytes)
                #Close the sending half of the connection so the other side
                #Knows we're done sending
                sock.shutdown(socket.SHUT_WR)
                #Read the response, an ASCII encoded object
                answerBytes = sock.recv(Constants.MANYBYTES)
                #Convert the response to an object
                try:
                    answer = pickle.loads(answerBytes)
                except EOFError:
                    logger.error("EOF Error on Connections.TCPConnection.getAnswer()")
                    logger.error("answerBytes = {0}".format(str(answerBytes)))
                    answer = None
            except socket.error as err:
                logger.debug(err)
                answer = None
        finally:
            sock.close()
            logger.debug("TCP Connection to {0} {1} was closed.".format(self.hostname, self.port))
        return answer

    def sendQuestion(self, question):
        """Send question without waiting for a response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        returnVal = False
        try:
            #Connect to the server
            logger.debug('TCP Connect to {0} {1}'.format(self.hostname, self.port))
            if self.hostname == None:
                return None
            sock.connect((self.hostname, self.port))
            questionBytes = pickle.dumps(question)
            sock.sendall(questionBytes)
            sock.shutdown(socket.SHUT_WR)
            sock.close()
            returnVal = True
        except socket.error as err:
            logger.error(err)
        logger.debug("TCP Connection to {0} {1} was closed.".format(self.hostname, self.port))
        return returnVal
