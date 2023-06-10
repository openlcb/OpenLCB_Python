#!/usr/bin/env python
'''
Drive an OpenLCB link via TCP (native protocol)

argparse is new in Jython 2.7, so dont use here

@author: Bob Jacobsen
@author: Stuart Baker - cleaned up and modernized
'''
import socket
import time

import tcpolcbutils

class TcpToOlcbLink :
    def __init__(self) :
        # prepare, but don't open
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.timeout(10)
        
        # defaults (generally overridden by system-wide defaults elsewhere)
        self.host = "172.168.1.10" # Arduino adapter default
        self.port = 12021
        self.timeout = 1.0
        self.verbose = True
        self.startdelay = 0
        self.socket = None
        self.rcvData = ""
        self.rcvIndex = 0
        return
    
    def connect(self) :
        # if verbose, print
        if (self.verbose) : print("   connect to ",self.host,":",self.port)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
        # wait for link startup
        # after (possible) reset due to serial startup
        if self.startdelay > 0 :
            if self.verbose : print("   waiting", self.startdelay, "seconds for adapter restart")
            time.sleep(self.startdelay)

        return
        
    def send(self, string) :
        if (self.socket == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) :
            print("   send   ",string)
    
        # send
        self.socket.send(string)
        
        return
        
    # returns multiplet or None on error
    #    transmitter
    #    message (includes MTI)   
    def receive(self) : # returns frame
        if (self.socket == None) : self.connect()
        
        self.socket.settimeout(self.timeout)

        if (self.rcvIndex >= len(self.rcvData)) :
            self.rcvIndex = 0
            self.rcvData = ""

        result = ""
        i = 0
        while (True) :
            if (len(self.rcvData) == 0) :
                # get more data
                try:
                    self.rcvData = self.socket.recv(1024)
                    self.rcvIndex = 0
                except socket.timeout as err:
                    if (self.verbose) :
                        print("<none>") # blank line to show delay?
                    return None
            else :
                # parse our data
                while (True) :
                    if (self.rcvData[self.rcvIndex] == ':') :
                        result = ""
                        i = 0
                    result = result + self.rcvData[self.rcvIndex]
                    if (self.rcvData[self.rcvIndex] == ';') :
                        self.rcvIndex = self.rcvIndex + 1
                        # if verbose, print
                        if (self.verbose) :
                            print("   receive",result)
                        return result
                    i = i + 1
                    self.rcvIndex = self.rcvIndex + 1
                    if (self.rcvIndex >= len(self.rcvData)) :
                        self.rcvIndex = 0
                        self.rcvData = ""
                        break
        # shouldn't reach here

    '''
    Continue receiving data until the we get the expected result or timeout.
    @param exact if != None, look for result with exact string
    @param startswith if != None, look for result starting with string
    @param data if != None, tuple of data bytes to match
    @param timeout timeout in seconds, if timeout != 0, return None on timeout
    @return resulting message on success, None on timeout
    '''
    def expect(self, exact=None, startswith=None, data=None, timeout=1) :
        start = time.time()
        while (True) :
            result = self.receive()
            if (data != None and result != None) :
                if (len(data) == ((len(result) - 12) / 2)) :
                    i = 0
                    j = 11
                    while (data[i] == int('0x' + result[j] + result[j + 1], 16)) :
                        i = i + 1
                        j = j + 2
                        if (i == len(data)) :
                            return result
            elif (exact != None) :
                if (result == exact) :
                    return result
            elif (startswith != None and result != None) :
                if (result.startswith(startswith)) :
                    return result
            elif (exact == None and startswith == None and data == None) :
                return result

            if (timeout != 0) :
                if (time.time() > (start + timeout)) :
                    if (self.verbose) :
                        print("Timeout")
                    return None

    def close(self) :
        return

import sys
from optparse import OptionParser

def main():
    global frame
    
    # create connection object
    network = TcpToOlcbLink()

    # get defaults
    host = network.host 
    port = network.port
    verbose = network.verbose
    
    frame = ':X182DF123N0203040506080001;'

    # process arguments
    (host, port, frame, verbose) = args(host, port, frame, verbose)
        
    # load new defaults
    network.host = host
    network.port = port
    network.verbose = verbose
    
    # send the frame
    network.send(frame)
    
    return  # done with example

def args(host, port, frame, verbose) :
    # argument processing
    usage = "usage: %prog [options] arg1\n\n" + \
            "Python module for connecting to an OpenLCB via a TCP native " + \
            "connection.\n" + \
            "Called standalone, will send one message frame.\n\n" + \
            "valid usages (default values):\n" + \
            "  ./tcpolcblink.py --ip=localhost\n" + \
            "  ./tcpolcblink.py --ip=localhost --port=12021\n" + \
            "  ./tcpolcblink.py --ip=localhost " + \
            "--port=12021 :X182DF123N0203040506080001\;" \

    parser = OptionParser(usage=usage)
    parser.add_option("-i", "--ip", dest="host", metavar="IP",
                      default="localhost",
                      help="host name or ip address")
    parser.add_option("-p", "--port", dest="port", metavar="PORT",
                      default=12021,
                      help="port number")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="print verbose debug information")

    (options, args) = parser.parse_args()

    if (len(args) > 0) :
        frame = args[0]

    return (options.host, options.port, frame, options.verbose)
    
if __name__ == '__main__':
    main()
    
