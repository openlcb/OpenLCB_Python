#!/usr/bin/env python
'''
Comprehensive test of the Memory Configuration Protocol implementation

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import datagram
    
def usage() :
    print ""
    print "Comprehensive test of the Memory Configuration "
    print "Protocol implementation"
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
        dest, nodeID = getUnderTestAlias.get(alias, None)

    retval = test(alias, dest, connection, verbose)
    exit(retval)
    
def test(alias, dest, connection, verbose) :

    # Get Configuration Options
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x80], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:2] != [0x20,0x82] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : 
        print "Configuration Options:"
        print "   Available commands ", hex(retval[2]*256+retval[3])
        print "        Write lengths ", hex(retval[4])
        print "        Highest space ", retval[5]
        print "         Lowest space ", retval[6]

    # One byte read from config space
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x42,0,0,0,0,1], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,0x52,0x00,0x00,0x00,0x00] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "read value", retval[6:7]
    
    # Eight byte read from config space
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x42,0,0,0,0,8], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,0x52,0x00,0x00,0x00,0x00] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "read value", retval[6:]
        
    # Get Address Space Info from space 0xFF
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x84,0xFF], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:3] != [0x20,0x86,0xFF] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : 
        print "Address Space Options:"
        print "      Highest address ", hex(((retval[3]*256+retval[4])*256+retval[5])*256+retval[6])
        print "      Alignment flags ", hex(retval[7])
        print "           Space name ", str(retval[8:])
    
    return 0

if __name__ == '__main__':
    main()
