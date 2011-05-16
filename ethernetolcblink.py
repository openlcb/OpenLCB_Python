#!/usr/bin/env python
'''
Drive an OpenLCB via Ethernet

argparse is new in Jython 2.7, so dont use here

@author: Tim Hatch
@author: Bob Jacobsen
'''
import socket

def sendframe(host, port, frame, verbose) :
    # if verbose, print
    if (verbose) : print "send ",frame," to ",host,":",port

    # send
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(frame+'\n')
    
    # if verbose, display what's received
    if (verbose) : 
        r = s.recv(1024)
        while r:
            print r,
            r = s.recv(1024)
    



import getopt, sys

def main():
    global frame
    
    # defaults
    host = '10.0.1.98'  # Arduino adapter default
    port = 23
    verbose = False
    frame = ':X182DF123N0203040506080001;'

    # process arguments
    (host, port, frame, verbose) = args(host, port, frame, verbose)
        
    # send the frame
    sendframe(host, port, frame, verbose)
    
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
    print "  python openlcbdriver.py --host=10.00.01.98"
    print "  python openlcbdriver.py --host=10.00.01.98 --port=23"
    print "  python openlcbdriver.py --host=10.00.01.98 --port=23 :X182DF123N0203040506080001\;"
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
    