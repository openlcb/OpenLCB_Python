#!/usr/bin/env python
'''
Drive an OpenLCB via Ethernet

argparse is new in Jython 2.7, so dont use here

@author: Tim Hatch
@author: Bob Jacobsen
'''
import socket

class EthernetToOlcbLink :
    def __init__(self) :
        # prepare, but don't open
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.socket.timeout(10)
        
        # defaults (generally overridden by system-wide defaults elsewhere)
        self.host = "10.00.01.98" # Arduino adapter default
        self.port = 23
        self.timeout = 1.0
        self.verbose = False
        self.socket = None
        return
    
    def connect(self) :
        # if verbose, print
        if (self.verbose) : print "   connect to ",self.host,":",self.port
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        
        return
        
    def send(self, frame) :
        if (self.socket == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   send    ",frame
    
        # send
        self.socket.send(frame+'\n')
        
        return
        
    def receive(self) : # returns frame
        if (self.socket == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   receive ",
            
        self.socket.settimeout(self.timeout)
        line = "";
        try:
            r = self.socket.recv(1024)
            # assuming we get frame in a single message
            while r:
                # if verbose, display what's received 
                if (self.verbose) : print r,
                return r
        except socket.timeout, err:
            if (self.verbose) : print "<none>" # blank line to show delay?
            return None

    def close(self) :
        return


import getopt, sys

def main():
    global frame
    
    # create connection object
    network = EthernetToOlcbLink()

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

def usage() :
    print ""
    print "Python module for connecting to an OpenLCB via an Ethernet connection."
    print "Called standalone, will send one CAN frame."
    print ""
    print "valid options:"
    print "  -v for verbose; also displays any responses"
    print "  -h, --host for host name or IP address"
    print "  -p, --port for port number"
    print ""
    print "valid usages (default values):"
    print "  ./ethernetolcblink.py --host=10.00.01.98"
    print "  ./ethernetolcblink.py --host=10.00.01.98 --port=23"
    print "  ./ethernetolcblink.py --host=10.00.01.98 --port=23 :X182DF123N0203040506080001\;"
    print ""
    print "Note: Most shells require escaping the semicolon at the end of the frame."
    
def args(host, port, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:v", ["host=", "port="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        else:
            assert False, "unhandled option"
    if (len(remainder) > 0) : 
        frame = remainder[0]
    return (host, port, frame, verbose)
    
if __name__ == '__main__':
    main()
    