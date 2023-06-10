#!/usr/bin/env python
'''
Drive an OpenLCB via Ethernet

argparse is new in Jython 2.7, so dont use here

@author: Tim Hatch
@author: Bob Jacobsen
'''
import socket
import time

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
        self.startdelay = 0
        self.socket = None
        self.rcvData = ""
        return

    def connect(self) :
        # if verbose, print
        if (self.verbose) : print ("   connect to ",self.host,":",self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # wait for link startup
        # after (possible) reset due to serial startup
        if self.startdelay > 0 :
            if self.verbose : print ("   waiting", self.startdelay, "seconds for adapter restart")
            time.sleep(self.startdelay)

        return

    def send(self, frame) :
        if (self.socket == None) : self.connect()

        # if verbose, print
        if (self.verbose) : print ("   send    ",frame)

        # send
        self.socket.send((frame+'\n').encode())

        return

    def receive(self) : # returns frame
        if (self.socket == None) : self.connect()

        self.socket.settimeout(self.timeout)
        while (self.rcvData.find('\n') < 0) :
            try:
                self.rcvData = self.rcvData+self.socket.recv(1024).decode('UTF8')
            except socket.timeout as err:
                if (self.verbose) : print ("   receive <none>") # blank line to show delay?
                return None
        r = self.rcvData[0:self.rcvData.find('\n')]
        self.rcvData = self.rcvData[self.rcvData.find('\n')+1:]
        if (self.verbose) : print ("   receive "+r)
        return r

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
        while (True) : # loop to find, timeout or fali
            result = self.receive()

            if (result == None) :
                 if (timeout != 0) :
                    if (time.time() > (start + timeout)) :
                        if (self.verbose) :
                            print ("Timeout")
                        return None
                    else :
                        continue
                 else : return None

            # here, result was not None - do sequential checks
            if (exact == None and startswith == None and data == None) :
                return result   # no test, just get the data

            if (data != None) :
                if (len(data) == ((len(result) - 12) / 2)) :
                    i = 0
                    j = 11
                    while (data[i] == int('0x' + result[j] + result[j + 1], 16)) :
                        i = i + 1
                        j = j + 2
                        if (i != len(data)) :
                            return None

            if (exact != None) :
                print ("exact may not be working right?")
                print (result)
                print (exact)
                print (result == exact)
                if (result != exact) :
                    return None

            if (startswith != None) :
                if (not result.startswith(startswith)) :
                    return None

            # here, we passed all the available tests!
            return result

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

    frame = ':X19490001N;'

    # process arguments
    (host, port, frame, verbose) = args(host, port, frame, verbose)

    # load new defaults
    network.host = host
    network.port = port
    network.verbose = verbose

    # send the frame
    network.send(frame)

    # then wait for and display responses until interrupted or nothing received
    while True :
        reply = network.receive()
        if reply == None : break
        print (reply)
    return


def usage() :
    print ("")
    print ("Python module for connecting to an OpenLCB via an Ethernet connection.")
    print ("Called standalone, will send one CAN frame.")
    print ("")
    print ("valid options:")
    print ("  -v for verbose; also displays any responses")
    print ("  -h, --host for host name or IP address")
    print ("  -p, --port for port number")
    print ("")
    print ("valid usages (default values):")
    print ("  ./ethernetolcblink.py --host=10.00.01.98")
    print ("  ./ethernetolcblink.py --host=10.00.01.98 --port=12021")
    print ("  ./ethernetolcblink.py --host=10.00.01.98 --port=12021 :X19490001N\;")
    print ("")
    print ("Note: Most shells require escaping the semicolon at the end of the frame.")

def args(host, port, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:v", ["host=", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print (str(err)) # will print something like "option -a not recognized"
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
