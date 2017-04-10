"""A Connection allows a Client to ask a Server for an Answer to a Question."""
#Standard
import socket
import pickle

#Hydra
import Constants
from hydra.logging_setup import logger
from hydra.hydra_utils import get_info_from_cfg

#pylint: disable=R0903

class TCPConnection(object):
    """A connection to a remote Hydra server, using TCP"""
    def __init__(self, address=None, port=None):
        """Constructor. Supply a address to connect to another computer."""
        if not address:
            address = get_info_from_cfg("database", "host")
        if not port:
            port = int(get_info_from_cfg("network", "port"))
        self.address = address
        self.port = port

    def get_answer(self, question):
        """Send the question to a remote server and get an answer back"""
        if self.address is None or self.port is None:
            return None
        #Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #Connect to the server
            logger.debug("TCP Connect to %s %d", self.address, self.port)
            try:
                sock.connect((self.address, self.port))
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
                    logger.error("EOF Error on connections.TCPConnection.get_answer()")
                    logger.error("answerBytes = %s", str(answerBytes))
                    answer = None
            except socket.error as err:
                logger.debug(err)
                answer = None
        finally:
            sock.close()
            logger.debug("TCP Connection to %s %d was closed.", self.address, self.port)
        return answer
