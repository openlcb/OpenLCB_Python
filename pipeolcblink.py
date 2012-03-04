#!/usr/bin/env python
'''
Drive an OpenLCB via pipes to an executable

argparse is new in Jython 2.7, so dont use here

@author: Bob Jacobsen
'''

import subprocess

# stdout,stderr = p.communicate("send stuff input\n more studd")
# print "O",stdout
# print "E",stderr

class PipeOlcbLink :
    def __init__(self) :
        
        # defaults (generally overridden by system-wide defaults elsewhere)
        self.location = "../C/libraries/OlcbTestCAN/obj/test/" # where to find file
        self.name = "pymain"                                   # executable name
        self.timeout = 1.0
        self.startdelay = 0;
        self.verbose = False
        self.process = None
        return
    
    def connect(self) :
        # if verbose, print
        if (self.verbose) : print "   starting ",self.name," from ",self.location
        
        executable = self.location+self.name
        self.process = subprocess.Popen(executable,1,None,subprocess.PIPE,subprocess.PIPE, 
                        subprocess.STDOUT, None, False, True)

        # dump startup needed here
        return
        
    def send(self, frame) :
        if (self.process == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   send    ",frame

        # send
        self.process.stdin.write(frame+'\n')
        self.process.stdin.flush()

        return
        
    def receive(self) : # returns frame
        if (self.process == None) : self.connect()
        
        # if verbose, print
        if (self.verbose) : print "   receive ",
            
        r = self.process.stdout.readline()

        # timeout returns empty line
        if not r.startswith(":") : 
            if (self.verbose) : print "<none>" # blank line to show delay?
            return None

        # if verbose, display what's received 
        if (self.verbose) : print r,
        
        return r       



import getopt, sys

def main():
    global frame
    
    # create connection object
    network = PipeOlcbLink()

    # get defaults
    location = network.location 
    name = network.name
    verbose = network.verbose
    
    frame = ':X180A7000N;'

    # process arguments
    (location, name, frame, verbose) = args(location, name, frame, verbose)
        
    # load new defaults
    network.location = location
    network.name = name
    network.verbose = verbose
    
    # send the frame
    network.send(frame)
    while True :
        network.receive()
    
    return  # done with example

def usage(location, name) :
    print ""
    print "Python module for connecting to an OpenLCB via an Ethernet connection."
    print "Called standalone, will send one CAN frame."
    print ""
    print "valid options:"
    print "  -v for verbose; also displays any responses"
    print "  -n, --name executable name, e.g. "+location
    print "  -l, --location directory to look for file, e.g. "+name
    print ""
    print "example:"
    print "  python pipeolcblink.py :X180A7000N;\;"
    print ""
    print "Note: Most shells require escaping the semicolon at the end of the frame."
    
def args(location, name, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:l:vV", ["name=", "location="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage(location, name)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            verbose = True
        elif opt in ("-l", "--location"):
            location = arg
        elif opt in ("-n", "--name"):
            name = arg
        else:
            assert False, "unhandled option"
            
    if (len(remainder) > 0) : 
        frame = remainder[0]
    return (location, name, frame, verbose)
    
if __name__ == '__main__':
    main()
    
