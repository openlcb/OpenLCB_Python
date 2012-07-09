#!/usr/bin/env python
'''
Handle OpenLCB verifyNodeGlobal

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, nodeID) :
    return canolcbutils.makeframestring(0x188A7000+alias,nodeID)
    
def usage() :
    print ""
    print "Called standalone, will send  CAN VerifyNode (Global) message."
    print "By default, this carries no Node ID information in the body, "
    print "but if you supply the -n or --node option, it will be included."
    print ""
    print "Expect a single VerifiedNode reply in return"
    print "e.g. [180B7sss] nn nn nn nn nn nn"
    print "containing dest alias and NodeID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-n --node dest nodeID (default None, format 01.02.03.04.05.06)"
    print "-t find NodeID automatically"
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
        opts, remainder = getopt.getopt(sys.argv[1:], "tn:a:vV", ["alias=", "node="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            verbose = True
        elif opt == "-V":
            verbose = True
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):
            alias = int(arg)
        elif opt in ("-n", "--node"):
            nodeID = canolcbutils.splitSequence(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)
        if nodeID == None : nodeID = otherNodeId

    # now execute
    retval = test(alias, nodeID, connection)
    connection.network.close()
    exit(retval)    
    
def test(alias, nodeID, connection):
    # first, send to this node
    connection.network.send(makeframe(alias, nodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Global verify with matching node ID did not receive expected reply"
        return 2
    elif not reply.startswith(":X188B7") :
        print "Global verify with matching node ID received wrong reply message", reply
        return 4

    # send without node ID
    connection.network.send(makeframe(alias, None))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Global verify without node ID did not receive expected reply"
        return 12
    elif not reply.startswith(":X188B7") :
        print "Global verify without node ID received wrong reply message ", reply
        return 14

    # send with wrong node ID
    connection.network.send(makeframe(alias, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if (reply == None ) : 
        return 0
    else :
        print "Global verify with wrong node ID should not receive reply but did: ", reply
        return 24

if __name__ == '__main__':
    main()
