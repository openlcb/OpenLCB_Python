#!/usr/bin/env python
## Input/Output stream helper for TCP sockets
#
# @author: Stuart Baker

## Raw input/output on a TCP socket

import socket

class RawIoTCP :
    ## Constructor.
    # @param host host to connect to
    # @param port number to connect on
    # @param timeout receive timeout
    # @param verbose true to print verbose information
    def __init__(self, host, port, timeout=None, verbose=False) :
        self.socket = None
        
        # defaults (generally overridden by system-wide defaults elsewhere)
        self.host = host
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        return

    ## Create the TCP socket connection.
    def connect(self) :
        if (self.verbose) :
            print "   connect to ", self.host, ":", self.port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        return

    ## Send data to the TCP socket.
    # @param string data to send
    def send(self, string) :        
        # if verbose, print
        if (self.verbose and len(string) > 0) :
            print "  raw send ", string
    
        # send
        self.socket.send(string)
        return

    ## Receive data from the TCP socket.
    # @param size size of data in bytes to receive
    # @param timeout timout to wait for data to araive
    # @Return data received, else None if timeout and no data is available
    def recv(self, size, timeout=None) :
        self.socket.settimeout(timeout)

        # get data
        try:
            data = self.socket.recv(size)
            return data
        except socket.timeout, err:
            if (self.verbose) :
                print "<none>" # blank line to show delay?
            return None

