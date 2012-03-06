#!/usr/bin/env python
'''
Read and check the Configuration Definition Information

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import datagram
    
def usage() :
    print ""
    print "Read and check the Configuration Definition Information"
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-a --alias source alias (default 0x"+hex(connection.thisNodeAlias).upper()+")"
    print "-d --dest dest alias (default 0x"+hex(connection.testNodeAlias).upper()+")"
    print "-t find destination alias automatically"
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
        opts, remainder = getopt.getopt(sys.argv[1:], "d:a:vVt", ["dest=", "alias="])
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
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

    retval = test(alias, dest, connection, verbose)
    exit(retval)
    
def test(alias, dest, connection, verbose) :

    # Read from CDI space
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x43,0,0,0,0,8], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,0x53,0x00,0x00,0x00,0x00] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "  Read CDI result", chr(retval[6]),chr(retval[7]),chr(retval[8])
               
    return 0

if __name__ == '__main__':
    main()
