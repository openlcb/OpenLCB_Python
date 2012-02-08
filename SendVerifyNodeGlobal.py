#!/usr/bin/env python
'''
Created on March 18, 2011

@author: Bob Jacobsen
'''

import defaults as defaults

def makeframe(alias, nodeID) :
    return ':X180A000FN;'
    
def usage() :
    print ""
    print "Python module for connecting to an OpenLCB via an Ethernet connection."
    print "Called standalone, will send one CAN VerifyNode (Global) message"
    print "display response"
    print ""
    print "Connection detail taken from defaults.py in that case"
    print ""
    print "-a --alias alias (default 123)"
    print "-n --node nodeID (default 01.02.03.04.05.06)"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "h:p:n:a:v", ["alias=", "node=", "host=", "port="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            defaults.network.verbose = True
        elif opt in ("-h", "--host"):
            defaults.network.host = arg
        elif opt in ("-p", "--port"):
            defaults.network.port = int(arg)
        elif opt in ("-a", "--alias"):
            defaults.network.port = int(arg)
        elif opt in ("-n", "--node"):
            defaults.network.port = int(arg)
        else:
            assert False, "unhandled option"

    # now execute
    defaults.network.send(makeframe(0,0))

if __name__ == '__main__':
    main()
