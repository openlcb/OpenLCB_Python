#!/usr/bin/env python
'''
Test that various reserved bits are not being (incorrectly) checked

Relies on the node properly handling verifyNodeAddressed and verifyNodeGlobal

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

    
def usage() :
    print ""
    print "Test that various reserved bits are not being (incorrectly) checked."
    print ""
    print "Relies on the node properly handling verifyNodeAddressed and verifyNodeGlobal"
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
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "tn:a:vVd:", ["alias=", "node=", "dest="])
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
        elif opt in ("-d", "--dest"): # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)
        if nodeID == None : nodeID = otherNodeId

    # now execute
    retval = test(alias, nodeID, dest, connection, verbose)
    exit(retval)    

def makeAddressedFrame(alias, dest, nodeID) :
    body = [0x0A]
    if nodeID != None : body = body+nodeID
    return canolcbutils.makeframestring(0x0E000000+alias+(dest<<12),body)

def test(alias, nodeID, dest, connection, verbose):
    if verbose : print "  test against verifyNodeGlobal"
    # first, send to this node
    connection.network.send(canolcbutils.makeframestring(0x088A7000+alias,nodeID))
    reply = connection.network.receive()
    if reply == None : 
        print "Global verify with matching node ID did not receive expected reply"
        return 2
    elif not reply.startswith(":X188B7") :
        print "Global verify with matching node ID received wrong reply message", reply
        return 4

    # send without node ID
    connection.network.send(canolcbutils.makeframestring(0x088A7000+alias, None))
    reply = connection.network.receive()
    if reply == None : 
        print "Global verify without node ID did not receive expected reply"
        return 12
    elif not reply.startswith(":X188B7") :
        print "Global verify without node ID received wrong reply message ", reply
        return 14

    # send with wrong node ID
    connection.network.send(canolcbutils.makeframestring(0x088A7000+alias, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if reply != None : 
        print "Global verify with wrong node ID should not receive reply but did: ", reply
        return 24

    if verbose : print "  test against verifyNodeAddressed"
    connection.network.send(makeAddressedFrame(alias, dest, nodeID))
    reply = connection.network.receive()
    if reply == None : 
        print "Expected reply not received"
        return 2
    elif not reply.startswith(":X188B7") :
        print "Unexpected reply received ", reply
        return 1

    # try with invalid alias
    connection.network.send(makeAddressedFrame(alias, ~dest, nodeID))
    reply = connection.network.receive()
    if reply != None : 
        print "Unexpected reply received ", reply
        return 1
    
    return 0

if __name__ == '__main__':
    main()
