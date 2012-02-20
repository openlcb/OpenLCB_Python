#!/usr/bin/env python
'''
Drive an OpenLCB via USB

argparse is new in Jython 2.7, so dont use here

@author: Bob Jacobsen
'''
import serial

class SerialOlcbLink :
    def __init__(self) :
        
        # defaults (generally overridden by system-wide defaults elsewhere)
        self.host = "/dev/tty.usbserial-A7007AOK" # really serial port
        self.port = 115200                        # really baud rate
        self.timeout = 1.0
        self.verbose = False
        self.ser = None
        return
    
    def connect(self) :
        # if verbose, print
        if (self.verbose) : print "   connect to ",self.host," at ",self.port
        
        self.ser = serial.Serial(self.host, self.port)
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.xonxoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.setDTR(True)
        self.ser.setRTS(True)
        #self.ser.open()
        
        return
        
    def send(self, frame) :
        if (self.ser == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   send    ",frame

        # send
        self.ser.write(frame+'\n')
        
        return
        
    def receive(self) : # returns frame
        if (self.ser == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   receive ",
            
        self.ser.timeout = self.timeout
        line = "";
        r = self.ser.readline()

        # timeout returns ""
        if r == "" : 
            if (self.verbose) : print "<none>" # blank line to show delay?
            return None
        # if verbose, display what's received 
        if (self.verbose) : print r,
        return r       



import getopt, sys

def main():
    global frame
    
    # create connection object
    network = SerialOlcbLink()

    # get defaults
    host = network.host 
    port = network.port
    verbose = network.verbose
    
    frame = ':X180A7000N;'

    # process arguments
    (host, port, frame, verbose) = args(host, port, frame, verbose)
        
    # load new defaults
    network.host = host
    network.port = port
    network.verbose = verbose
    
    # send the frame
    network.send(frame)
    while True :
        network.receive()
    
    return  # done with example

def usage() :
    print ""
    print "Python module for connecting to an OpenLCB via an Ethernet connection."
    print "Called standalone, will send one CAN frame."
    print ""
    print "valid options:"
    print "  -v for verbose; also displays any responses"
    print "  -p, --port for serial port to USB connection"
    print "  -p, --port for baud rate"
    print ""
    print "valid usages (default values):"
    print "  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK"
    print "  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK --speed=115200"
    print "  python serialolcblink.py --port=/dev/tty.usbserial-A7007AOK --speed=115200 :X180A7000N;\;"
    print ""
    print "Note: Most shells require escaping the semicolon at the end of the frame."
    
def args(host, port, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "s:p:v", ["speed=", "port="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt in ("-p", "--port"):
            host = arg
        elif opt in ("-s", "--speed"):
            port = int(arg)
        else:
            assert False, "unhandled option"
    if (len(remainder) > 0) : 
        frame = remainder[0]
    return (host, port, frame, verbose)
    
if __name__ == '__main__':
    main()
    