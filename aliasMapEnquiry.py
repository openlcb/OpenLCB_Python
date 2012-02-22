#!/usr/bin/env python
'''
OpenLCB AliasMapEquiry frame

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, nodeID) :
    return canolcbutils.makeframestring(0x10702000+alias,nodeID)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN AliasMapEquiry frame"
    print " and display response"
    print ""
    print "Expect a single frame in return"
    print "e.g. [180B7sss] nn nn nn nn nn nn"
    print "containing dest alias and NodeID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-n --node dest nodeID (default None, format 01.02.03.04.05.06)"
    print "-t find destination alias and NodeID automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    nodeID = None
    alias = connection.thisNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:a:vVt", ["alias=", "node="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            connection.network.verbose = True
            verbose = True
        elif opt in ("-a", "--alias"): # needs hex processing
            alias = int(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)
        if nodeID == None : nodeID = otherNodeId

    retval = test(alias, nodeID, connection, verbose)
    exit(retval)
    
def test(alias, nodeID, connection, verbose) :
    connection.network.send(makeframe(alias, nodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply when node ID matches not received"
        return 2
    elif not reply.startswith(":X10701") :
        print "Unexpected reply received ", reply
        return 1

    # test non-matching NodeID using a reserved one
    connection.network.send(makeframe(alias, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received when node ID didnt match ", reply
        return 2
        
    return 0

if __name__ == '__main__':
    main()
