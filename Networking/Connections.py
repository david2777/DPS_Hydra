"""A Connection allows a Client to ask a Server for an Answer to a Question."""
#Standard
import socket
import pickle

#Hydra
import constants
from hydra.logging_setup import logger
from utils.hydra_utils import getInfoFromCFG

class TCPConnection(object):
    """A connection to a remote Hydra server, using TCP"""
    def __init__(self, hostname=None, port=None):
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
            logger.debug("TCP Connect to %s %d", self.hostname, self.port)
            if self.hostname is None:
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
                answerBytes = sock.recv(constants.MANYBYTES)
                #Convert the response to an object
                try:
                    answer = pickle.loads(answerBytes)
                except EOFError:
                    logger.error("EOF Error on connections.TCPConnection.getAnswer()")
                    logger.error("answerBytes = %s", str(answerBytes))
                    answer = None
            except socket.error as err:
                logger.debug(err)
                answer = None
        finally:
            sock.close()
            logger.debug("TCP Connection to %s %d was closed.", self.hostname, self.port)
        return answer

    def sendQuestion(self, question):
        """Send question without waiting for a response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        returnVal = False
        try:
            #Connect to the server
            logger.debug("TCP Connect to %s %d", self.hostname, self.port)
            if self.hostname is None:
                return None
            sock.connect((self.hostname, self.port))
            questionBytes = pickle.dumps(question)
            sock.sendall(questionBytes)
            sock.shutdown(socket.SHUT_WR)
            sock.close()
            returnVal = True
        except socket.error as err:
            logger.error(err)
        logger.debug("TCP Connection to %s %d was closed.", self.hostname, self.port)
        return returnVal
