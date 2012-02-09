#!/usr/bin/env python
'''
Send one generic datagram

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import datagram
    
def usage() :
    print ""
    print "Called standalone, will do one-byte memory read"
    print " and display response"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-c --content message content (default 1,2,3,4)"
    print "-t find destination alias automatically"
    print "-v verbose"

import getopt, sys

def main():
    # argument processing
    alias = connection.thisNodeAlias
    dest = connection.testNodeAlias
    identifynode = False
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vt", ["dest=", "alias="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-v":
            connection.network.verbose = True
        elif opt in ("-a", "--alias"):  # needs hex processing
            alias = int(arg)
        elif opt in ("-d", "--dest"):  # needs hex processing
            dest = int(arg)
        elif opt == "-t":
            identifynode = True
        else:
            assert False, "unhandled option"

    if identifynode :
        import getUnderTestAlias
        dest = getUnderTestAlias.get(alias, None)

    # now execute: read 1 byte from address 0, configuration space 
    connection.network.send(datagram.makeframe(alias, dest, [0x20,0x42,0,0,0,0,1]))

    # datagram reply
    reply = connection.network.receive()
    if (reply == None ) : 
        print "No reply to read command datagram"
        exit(2)
    elif (not reply.startswith(":X1E")) or ( reply[11:13] != '04' ):
        print "Unexpected reply to read command datagram ", reply
        exit(1)
    
    # data response
    reply = connection.network.receive()
    if (reply == None ) : 
        print "No data returned"
        exit(4)
    elif (not reply.startswith(":X1D")) or ( reply[11:23] != '205200000000' ):
        print "Unexpected message instead of reply datagram ", reply
        exit(3)

    # send final reply
    connection.network.send(datagram.makereply(alias, dest))
    return

if __name__ == '__main__':
    main()
