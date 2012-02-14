#!/usr/bin/env python
'''
Tests a node's response to seeing messages with its alias

@author: Bob Jacobsen
'''

# Expects:
# :X17020573N;
# :X16304573N;
# :X15050573N;
# :X10700573N;
# :X19087573N020304050607;
# :X192AB573N0203040506070001;
# :X192AB573N0203040506070004;
# :X1926B573N0203040506070005;
# :X1926B573N0203040506070008;

import connection as connection
import canolcbutils
import verifyNodeGlobal
import verifyNodeAddressed
import time
    
def usage() :
    print ""
    print "Called standalone, tests a node's response to"
    print "seeing messages with its alias"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 123)"
    print "-d --dest dest alias (default 123)"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V very verbose"

import getopt, sys

def main():
    alias = connection.thisNodeAlias;
    dest = connection.testNodeAlias;
    verbose = False
    identifynode = False
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["alias=", "dest="])
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
            alias = int(arg) # needs hex decode
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex decode
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, otherNodeId = getUnderTestAlias.get(alias, None)

    retval = test(alias, dest, connection, verbose)
    return retval
    
def test(alias, dest, connection, verbose) :
    # Sending a global message (that normally doesn't get a response)
    if verbose : print "  check no-response global message with alias conflict"
    connection.network.send(verifyNodeGlobal.makeframe(dest, [0,0,0,0,0,0]))
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "no response received to RIF"
        return 2
    if int(reply[7:10],16) != dest :
        if verbose : print "mismatched reply alias"
        return 12
    if not reply.startswith(":X10700") :
        if verbose : print "CID reply not correct, RID expected"
        return 32
    
    # Sending a global message (that normally does get a response)
    if verbose : print "  check response-inducing global message with alias conflict"
    connection.network.send(verifyNodeGlobal.makeframe(dest, nodeID))
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "no response received to RIF"
        return 2
    if int(reply[7:10],16) != dest :
        if verbose : print "mismatched reply alias"
        return 12
    if not reply.startswith(":X10700") :
        if verbose : print "CID reply not correct, RID expected"
        return 32
    
    # Sending an addressed message to some other alias (note arguments backwards, on purpose)
    if verbose : print "  check addressed message with alias conflict"
    connection.network.send(verifyNodeAddressed.makeframe(dest, alias, None))
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "no response received to RIF"
        return 2
    if int(reply[7:10],16) != dest :
        if verbose : print "mismatched reply alias"
        return 12
    if not reply.startswith(":X10700") :
        if verbose : print "CID reply not correct, RID expected"
        return 32

    # send a CheckID   
    if verbose : print "  check CheckID with alias conflict"
    connection.network.send(canolcbutils.makeframestring(0x17020000+dest, None))
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "no response received to RIF"
        return 2
    if int(reply[7:10],16) != dest :
        if verbose : print "mismatched reply alias"
        return 12
    if not reply.startswith(":X10700") :
        if verbose : print "CID reply not correct, RID expected"
        return 32

    # send a ReserveID   
    connection.network.send(canolcbutils.makeframestring(0x10700000+dest, None))
    if verbose : print "  check ReserveID with alias conflict"
    reply = connection.network.receive()
    if reply == None :
        if verbose : print "no response received to RIF"
        return 4
    if int(reply[7:10],16) == dest :
        if verbose : print "node did not change alias"
        return 14
    if not reply.startswith(":X17") :
        if verbose : print "RID reply not correct, CID sequence expected"
        return 34

    # we should probably check the rest of the sequence here
    # but for now, assuming it starts OK is enough.
    return 0

if __name__ == '__main__':
    main()
