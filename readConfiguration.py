#!/usr/bin/env python
'''
Send one request for a configuration read

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
    print "-c --count number of bytes to read (default 1)"
    print "-s --space address space (default 254, configuration; CDI is 255, all-mem is 253)"
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
    count = 1
    space = 0xFE
    
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "s:d:a:c:vVt", ["space=", "dest=", "count=", "alias="])
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
        elif opt in ("-s", "--space"):
            space = int(arg)
        elif opt in ("-c", "--count"):
            count = int(arg)
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
        dest, nodeID = getUnderTestAlias.get(alias, None)

    retval = test(alias, dest, connection, count, space, verbose)
    exit(retval)
    
def test(alias, dest, connection, count, space, verbose) :
    cmd = 0x40
    if space == 0xFF :
        cmd = 0x43
    if space == 0xFE :
        cmd = 0x42
    if space == 0xFD :
        cmd = 0x41
    retval = datagram.sendOneDatagram(alias, dest, [0x20,cmd,0,0,0,0,count], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,cmd|0x10,0x00,0x00,0x00,0x00] :
        if verbose : print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "read value", retval[6:]

if __name__ == '__main__':
    main()
