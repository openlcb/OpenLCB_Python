#!/usr/bin/env python
'''
OpenLCB ProtocolIdentificationProtocol message

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils

def makeframe(alias, dest) :
    body = [0x2E]
    return canolcbutils.makeframestring(0x1E000000+alias+(dest<<12),body)
    
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
    if verbose : print "  check OK"
    connection.network.send(makeframe(alias, dest))
    reply = connection.network.receive()
    if (reply == None ) : 
        print "Expected reply not received"
        return 2
    if not (reply.startswith(":X1E") and int(reply[4:7],16)==alias and int(reply[7:10],16)==dest and reply[11:13]=="2F") :
        print "Unexpected reply received ", reply
        return 1

    if verbose : print "  not addressed, no reply"
    connection.network.send(makeframe(alias, (~dest)&0xFFF))
    reply = connection.network.receive()
    if (reply == None ) : 
        return 0
    else :
        print "Unexpected reply received ", reply
        return 1

    return 0

if __name__ == '__main__':
    main()
