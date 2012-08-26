#!/usr/bin/env python
'''
OpenLCB VerifyNodeAddressed message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import copy

def makeframe(alias, dest, nodeID) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    if nodeID != None : body = body+nodeID
    return canolcbutils.makeframestring(0x19488000+alias,body)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN VerifyNode (addressed) message"
    print " and display response"
    print ""
    print "Expect a single VerifiedNode reply in return"
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
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:n:a:vVt", ["alias=", "node=", "dest="])
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
        dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)
        if nodeID == None : nodeID = otherNodeId

    retval = test(alias, dest, nodeID, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, nodeID, connection, verbose) :
    # send correct address, correct node ID in body
    connection.network.send(makeframe(alias, dest, nodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply to correct alias & correct ID not received"
        return 2
    elif not reply.startswith(":X19170") :
        print "Unexpected reply received ", reply
        return 1

    # send correct address, no node ID in body
    connection.network.send(makeframe(alias, dest, None))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply to correct alias & no ID not received"
        return 2
    elif not reply.startswith(":X19170") :
        print "Unexpected reply received ", reply
        return 1

    # send correct address, wrong node ID in body
    tnodeID = copy.copy(nodeID)
    tnodeID[0] = tnodeID[0]^1
    
    connection.network.send(makeframe(alias, dest, tnodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply to correct alias & incorrect ID not received"
        return 2
    elif not reply.startswith(":X19170") :
        print "Unexpected reply received ", reply
        return 1

    # repeat all three with invalid alias
    connection.network.send(makeframe(alias, (~dest)&0xFFF, nodeID))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received on incorrect alias, OK nodeID", reply
        return 1
    
    connection.network.send(makeframe(alias, (~dest)&0xFFF, None))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received on incorrect alias, no nodeID", reply
        return 1
    
    connection.network.send(makeframe(alias, (~dest)&0xFFF, tnodeID))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received on incorrect alias, wrong nodeID", reply
        return 1
    
    return 0

if __name__ == '__main__':
    main()
