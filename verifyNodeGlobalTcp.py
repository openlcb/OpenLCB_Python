#!/usr/bin/env python
'''
Handle OpenLCB verifyNodeGlobal

@author: Bob Jacobsen
'''

import connection as connection
import tcpolcbutils

def makeMessage(sourceNodeID, destNodeID) :
    body = [0x04,0x90]+sourceNodeID
    if destNodeID != None :
        body += destNodeID
    return tcpolcbutils.makemessagestring(sourceNodeID, None, body)
    
def usage() :
    print ""
    print "Called standalone, will send TCP VerifyNode (Global) message."
    print "By default, this carries no Node ID information in the body, "
    print "but if you supply the -n or --node option, it will be included."
    print ""
    print "Expect a single VerifiedNode reply in return"
    print "containing destination NodeID"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-n --node dest nodeID (default None, format 01.02.03.04.05.06)"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    sourceNodeID = [0x11,0x12,0x13,0x14,0x15,0x16]
    destNodeID = [1,2,3,4,5,6]
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
        elif opt in ("-n", "--node"):
            destNodeID = tcpolcbutils.splitSequence(arg)
        else:
            assert False, "unhandled option"

    # now execute
    retval = test(sourceNodeID, destNodeID, connection, verbose)
    connection.network.close()
    exit(retval)    
    
def test(sourceNodeID, destNodeID, connection, verbose):

    if verbose :
        print "First message sent: "+tcpolcbutils.format(makeMessage(sourceNodeID, destNodeID))
        
    # first, send with dest node's nodeID in data
    connection.network.send(makeMessage(sourceNodeID, destNodeID))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Global verify with matching node ID did not receive expected reply"
        return 2
    [transmitter, message] = reply
    [mti, source, dest, body] = tcpolcbutils.parseMessage(message)
    if not mti == 0x0170 :
        print "Global verify with matching node ID received wrong reply message", tcpolcbutils.formatMessage(message)
        return 4

    # send without nodeID in data
    connection.network.send(makeMessage(sourceNodeID, None))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Global verify without node ID did not receive expected reply"
        return 12
    [transmitter, message] = reply
    [mti, source, dest, body] = tcpolcbutils.parseMessage(message)
    if not mti == 0x0170 :
        print "Global verify without node ID received wrong reply message ", tcpolcbutils.formatMessage(message)
        return 14

    # send with wrong node ID in data
    connection.network.send(makeMessage(sourceNodeID, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if (reply == None ) : 
        return 0
    else :
        [transmitter, message] = reply
        print "Global verify with wrong node ID should not receive reply but did: ", tcpolcbutils.formatMessage(message)
        return 24

if __name__ == '__main__':
    main()
