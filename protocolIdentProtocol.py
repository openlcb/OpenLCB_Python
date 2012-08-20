#!/usr/bin/env python
'''
OpenLCB ProtocolIdentificationProtocol message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest) :
    body = [(dest>>8)&0xFF, dest&0xFF]
    return canolcbutils.makeframestring(0x19828000+alias,body)
    
def usage() :
    print ""
    print "Called standalone, will send one CAN ProtocolIdentificationProtocol (addressed) message"
    print " and display response"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias and NodeID automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    verbose = False
    
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
            connection.network.verbose = True
            verbose = True
        elif opt in ("-a", "--alias"): # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"): # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest, otherNodeId = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, connection, verbose) :
    connection.network.send(makeframe(alias, dest))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply to good request not received"
        return 2
    if not (reply.startswith(":X19668") and int(reply[11:15],16)==alias and int(reply[7:10],16)==dest) :
        print "Unexpected reply received ", reply
        return 1
    if verbose : 
        print "  Node supports:"
        value = canolcbutils.bodyArray(reply)
        if (value[2] & 0x80) != 0 : print "      Protocol Identification"
        if (value[2] & 0x40) != 0 : print "      Datagram Protocol"
        if (value[2] & 0x20) != 0 : print "      Stream Protocol"
        if (value[2] & 0x10) != 0 : print "      Memory Configuration Protocol"
        if (value[2] & 0x08) != 0 : print "      Reservation Protocol"
        if (value[2] & 0x04) != 0 : print "      Event Exchange (P/C) Protocol"
        if (value[2] & 0x02) != 0 : print "      Identification Protocol"
        if (value[2] & 0x01) != 0 : print "      Teaching/Learning Protocol"
        if (value[3] & 0x80) != 0 : print "      Remote Button Protocol"
        if (value[3] & 0x40) != 0 : print "      Abbreviated Default CDI Protocol"
        if (value[3] & 0x20) != 0 : print "      Display Protocol"
        if (value[3] & 0x10) != 0 : print "      Simple Node Information Protocol"
        if (value[3] & 0x08) != 0 : print "      Configuration Description Information"

    if verbose : print "  not addressed, expect no reply"
    connection.network.send(makeframe(alias, (~dest)&0xFFF))
    reply = connection.network.receive()
    if (reply != None ) : 
        print "Unexpected reply received to request to different node ", reply
        return 1

    # test expansion by sending a start-only, then an end-only frame
        
    body = [((dest>>8)&0xFF)|0x10, dest&0xFF,0,0, 0,0,0,0]
    frame = canolcbutils.makeframestring(0x19828000+alias,body)
    connection.network.send(frame)

    reply = connection.network.receive()

    body = [((dest>>8)&0xFF)|0x20, dest&0xFF,0,0, 0,0,0,0]
    frame = canolcbutils.makeframestring(0x19828000+alias,body)
    connection.network.send(frame)

    if (reply == None ) : # if no reply to 1st frame, see if reply to 2nd frame; either OK
        reply = connection.network.receive()

    if (reply == None ) : 
        print "Expected reply to double frame not received"
        return 2
    if not (reply.startswith(":X19668") and int(reply[11:15],16)==alias and int(reply[7:10],16)==dest) :
        print "Unexpected reply received ", reply
        return 1

    reply = connection.network.receive()
    if (reply != None ) : 
        print "  Suggestion: PIP should handle start-end bits in requests for future expansion"

    return 0

if __name__ == '__main__':
    main()
