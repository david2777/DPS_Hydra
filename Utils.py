"""Miscellaneous pieces of useful code"""
#Standard
import ConfigParser
import os
import itertools
import socket

#Hydra
import Constants

#Authors: David Gladstein and Aaron Cohn
#Taken from Cogswell's Project Hydra

def myHostName():
    """This computer's host name in the RenderHost table"""
    #Open config file
    config = ConfigParser.RawConfigParser ()
    config.read(Constants.SETTINGS)
    domain = config.get(section="network", option="dnsDomainExtension")
    return socket.gethostname() + domain

def flanged(name):
    return name.startswith ('__') and name.endswith ('__')

def nonFlanged(name):
    return not flanged(name)

def sockRecvAll(sock):
    """
    Receive all bytes from a socket, with no buffer size limit
    Generator to recieve strings from socket, will return
    Empty strings(forever) upon EOF
    """
    receivedStrings  = (sock.recv(Constants.MANYBYTES)
                        for i in itertools.count(0))
    #Concatenate the nonempty ones
    return ''.join(itertools.takewhile(len, receivedStrings))

def flushOut(f):
    "Flush and sync a file to disk"
    f.flush()
    os.fsync(f.fileno())
