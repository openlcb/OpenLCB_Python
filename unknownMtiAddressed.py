#!/usr/bin/env python
'''
OpenLCB UnknownMtiAddressed message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest, nodeID) :
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),[0x00]+nodeID)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN message with unknown MTI"
    print " and display response"
    print ""
    print "Expect a single error reply in return"
    print "e.g. [1Edddsss] 0C nn nn nn nn nn nn"
    print "containing dest alias and error info"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-n --node dest nodeID (default 01.02.03.04.05.06)"
    print "-t find destination alias automatically"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = connection.testNodeID
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:n:a:vt", ["alias=", "node=", "dest="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"): # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"): # needs hex processing
            dest = int(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None)

    # now execute
    connection.network.send(makeframe(alias, dest, nodeID))
    while (True) :
        reply = connection.network.receive()
        if (reply == None ) : 
            print "Expected reply not received"
            exit(2)
        elif reply.startswith(":X180B7") :
            exit(0)
        else
            print "Unexpected reply ", reply
            exit(1)
    return

if __name__ == '__main__':
    main()
