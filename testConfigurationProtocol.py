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
        dest, nodeID = getUnderTestAlias.get(alias, None, verbose)

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
        print "  Configuration Options:"
        cmd = retval[2]*256+retval[3]
        print "    Available commands (",hex(cmd),")"
        print "                Write under mask: ", "yes" if cmd&0x8000 else "no"
        print "                 Unaligned reads: ", "yes" if cmd&0x4000 else "no"
        print "                Unaligned writes: ", "yes" if cmd&0x2000 else "no"
        print "              Mfg ACDI 0xFD read: ", "yes" if cmd&0x0800 else "no"
        print "              Usr ACDI 0xFC read: ", "yes" if cmd&0x0400 else "no"
        print "             Usr ACDI 0xFC write: ", "yes" if cmd&0x0200 else "no"
        print "    Write lengths (", hex(retval[4]),")"
        print "                          1 byte: ", "yes" if retval[4]&0x80 else "no"
        print "                          2 byte: ", "yes" if retval[4]&0x40 else "no"
        print "                          4 byte: ", "yes" if retval[4]&0x20 else "no"
        print "                         64 byte: ", "yes" if retval[4]&0x10 else "no"
        print "                       arbitrary: ", "yes" if retval[4]&0x02 else "no"
        print "                          stream: ", "yes" if retval[4]&0x01 else "no"
        print "    Highest space ", retval[5]
        print "    Lowest space  ", retval[6]
    lowSpace = retval[6]
    highSpace = retval[5]
    
    # One byte read from config space
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x41,0,0,0,0,1], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,0x51,0x00,0x00,0x00,0x00] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "  Read one byte result", retval[6:7]
    
    # Eight byte read from config space
    retval = datagram.sendOneDatagram(alias, dest, [0x20,0x41,0,0,0,0,8], connection, verbose)
    if retval != 0 :
        return retval
    # read data response
    retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
    if (type(retval) is int) : 
        # pass error code up
        return retval
    if retval[0:6] != [0x20,0x51,0x00,0x00,0x00,0x00] :
        print "Unexpected message instead of read reply datagram ", retval
        return 3
    if verbose : print "  Read eight bytes result", retval[6:]
       
    n = highSpace
    while n >= lowSpace-1 :
        # Get Address Space Info from each space
        retval = datagram.sendOneDatagram(alias, dest, [0x20,0x84,n], connection, verbose)
        if retval != 0 :
            return retval
        # read data response
        retval = datagram.receiveOneDatagram(alias, dest, connection, verbose)
        if (type(retval) is int) : 
            # pass error code up
            return retval
        if retval[0] != 0x20 or retval[1]&0xFE != 0x86 or retval[2] != n :
            print "Unexpected message instead of starting with [0x20,0x86,",n,"] read reply datagram: ", retval
            return 3
        if verbose : 
            print "  Address Space",n,"Options:"
            print "      Present? ", "yes" if retval[1]&0x01 else "no"
            print "      Highest address ", hex(((retval[3]*256+retval[4])*256+retval[5])*256+retval[6])
            print "                Flags (", hex(retval[7]),")"
            print "                        Read-only ", "yes" if retval[7]&0x01 else "no"
            
            if len(retval) > 9:
                print "      Lowest address ", hex(((retval[9]*256+retval[10])*256+retval[11])*256+retval[12])
            else:
                print "      Lowest address implied at 0x0000"
            if len(retval) > 12:
                print "           Space name ", str(retval[12:])
        n = n-1
        
    return 0

if __name__ == '__main__':
    main()
