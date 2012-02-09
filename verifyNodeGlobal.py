#!/usr/bin/env python
'''
Created on March 18, 2011

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, nodeID) :
    return canolcbutils.makeframestring(0x180A7000+alias,nodeID)
    
def usage() :
    print ""
    print "Called standalone, will send  CAN VerifyNode (Global) message"
    print ""
    print "Expect a single VerifiedNode reply in return"
    print "e.g. [180B7sss] nn nn nn nn nn nn"
    print "containing dest alias and NodeID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-n --node dest nodeID (default None, format 01.02.03.04.05.06)"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = None
    alias = connection.thisNodeAlias
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:a:v", ["alias=", "node="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    # now execute
    connection.network.send(makeframe(alias, nodeID))
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : 
            print "Expected reply not received"
            exit(2)
        elif reply.startswith(":X180B7") :
            exit(0)
        else :
            print "Unexpected reply received ", reply
            exit(1)
    return

if __name__ == '__main__':
    main()
