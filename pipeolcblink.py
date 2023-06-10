#!/usr/bin/env python
'''
Drive an OpenLCB via pipes to an executable

@author: Bob Jacobsen
'''

import subprocess

class PipeOlcbLink :
    def __init__(self) :

        # Defaults (generally overridden by system-wide defaults elsewhere)
        # To use these:
        #    cd ../C   (e.g. to prototypes/C)
        #    make
        self.location = "../C/libraries/OlcbTestCAN/obj/test/" # where to find file
        self.name = "pyOlcbBasicNode"                          # executable name
        self.timeout = 0.010
        self.startdelay = 0;
        self.verbose = False
        self.process = None
        return

    def connect(self) :
        # if verbose, print
        if (self.verbose) : print("   starting ",self.name," from ",self.location)

        executable = self.location+self.name
        self.process = subprocess.Popen(executable,1,None,subprocess.PIPE,subprocess.PIPE,
                        sys.stderr, None, False, True)
        self.seenEnd = False

        # dump startup needed here
        if self.timeout < 2 :
            self.flush()
            self.process.stdin.write('T\n')
            self.flush()
            self.process.stdin.write('T\n')
            self.flush()
            self.process.stdin.write('T\n')
            self.flush()
            self.process.stdin.write('T\n')
            self.flush()
            self.process.stdin.write('T\n')
            self.flush()
        return

    def send(self, frame) :
        if self.process == None :
            self.connect()
        elif not self.seenEnd :
            self.flush()

        # if verbose, print
        if self.verbose : print("   send    ",frame)

        # send
        self.seenEnd = False
        self.process.stdin.write(frame+'\n')
        self.process.stdin.flush()

        return

    def receive(self) : # returns frame
        if (self.process == None) : self.connect()

        r = self.process.stdout.readline()

        # timeout returns empty line
        count = 0
        while not r.startswith(":") and self.timeout >= count*0.040 :
            count = count + 1
            # try again a time or two
            self.process.stdin.write('T\n')
            self.process.stdin.flush()
            r = self.process.stdout.readline()

        if not r.startswith(":") :
            if (self.verbose) : print("   receive <none>") # blank line to show delay?
            self.seenEnd = True
            return None

        # if verbose, display what's received
        if (self.verbose) : print("   receive "+str(r))

        return r

    def close(self) :
        self.process.kill()
        self.process.wait()
        return

    def flush(self) : # reads past any pending input
        while True :
            r = self.process.stdout.readline()
            if not r.startswith(":") :
                self.seenEnd = True
                break
            if self.verbose : print("   drop    ",r, end=' ')
        return

    def more(self) : # checks whether any more input in response to most recent stimulus
        return False

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
    print("")
    print("Python module for connecting to an OpenLCB via an Ethernet connection.")
    print("Called standalone, will send one CAN frame.")
    print("")
    print("valid options:")
    print("  -v for verbose; also displays any responses")
    print("  -n, --name executable name, e.g. "+location)
    print("  -l, --location directory to look for file, e.g. "+name)
    print("")
    print("example:")
    print("  python pipeolcblink.py :X180A7000N;\;")
    print("")
    print("Note: Most shells require escaping the semicolon at the end of the frame.")

def args(location, name, frame, verbose) :
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:l:vV", ["name=", "location="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
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

