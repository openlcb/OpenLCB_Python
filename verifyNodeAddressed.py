#!/usr/bin/env python
'''
OpenLCB VerifyNodeAddressed message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest, nodeID) :
    body = [0x0A]
    if nodeID != None : body = body+nodeID
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),body)
    
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
    connection.network.send(makeframe(alias, dest, nodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply not received"
        return 2
    elif not reply.startswith(":X188B7") :
        print "Unexpected reply received ", reply
        return 1

    # try with invalid alias
    connection.network.send(makeframe(alias, ~dest, nodeID))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received ", reply
        return 1
    
    return 0

if __name__ == '__main__':
    main()
