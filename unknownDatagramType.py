#!/usr/bin/env python
'''
Check that unknown (unallocated) datagram types get a reject message

Tests that implementor has not grabbed datagram types for their own purposes

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
    
def usage() :
    print ""
    print "Called standalone, will scan unknown Datagram types"
    print " and display response"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias automatically"
    print "-v verbose"
    print "-V Very verbose"

import getopt, sys

knownType = [0x01, 0x02, 0x20, 0x21, 0x30]

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
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    connection.network.close()
    exit(retval)
    
def test(alias, dest, connection, verbose) :
    import datagram
    for type in range(0,256) :
        if type in knownType : continue
        connection.network.send(datagram.makeonlyframe(alias, dest, [type]))
        reply = connection.network.receive()
        if reply == None : 
            print "Expected reply not received for", type
            return 2
        if  (not reply.startswith(":X19A48")) or reply[15:19] != "1040"  : 
            print "Wrong reply received for", type
            return 4
    return 0

if __name__ == '__main__':
    main()
