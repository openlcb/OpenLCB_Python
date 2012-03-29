#!/usr/bin/env python
'''
Forces repeated reallocation of alias to check for zero or repeated aliases

@author: Bob Jacobsen
'''

import connection as connection
import canolcbutils
import verifyNodeGlobal

import time
    
def usage() :
    print ""
    print "Forces repeated reallocation of alias to check for zero or repetition."
    print ""
    print "Default connection detail taken from connection.py"
    print ""
    print "-d --dest destination (target node) starting alias"
    print "-t find destination alias automatically"
    print "-n --num number of cycles (default 40000, 0 means forever)"
    print "-v verbose"
    print "-V very verbose"

import getopt, sys

def main():
    n = 40000
    dest = connection.testNodeAlias;
    verbose = False
    identifynode = False
    
    # argument processing
    try:
        opts, remainder = getopt.getopt(sys.argv[1:], "n:d:a:vVt", ["alias=", "dest=","num="])
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
        elif opt in ("-d", "--dest"):
            dest = int(arg) # needs hex decode
        elif opt == "-t":
            identifynode = True
        elif opt in ("-n", "--num"):
            n = int(arg)
        else:
            assert False, "unhandled option"

    retval = test(dest, connection, identifynode, n, verbose)
    return retval
    
def once(dest, connection, identifynode, verbose) :
    alias = (dest-10)|1

    # Note: This test assumes that the response will be
    # to reacquire another alias after the conflicted one is
    # dropped.  This isn't required behavior by standard, but
    # is a necessary condition for the test to continue and 
    # check another conflict condition.
    #
    # Sending a global message (that normally doesn't get a response)
    # by sending verifyNodeGlobal with a nodeID that doesn't match any valid
    if verbose : print "  check no-response global message with alias conflict"
    connection.network.send(verifyNodeGlobal.makeframe(dest, [0,0,0,0,0,1]))
    reply = connection.network.receive()
    if reply == None :
        print "no response received to conflict frame"
        return -21
    if not reply.startswith(":X10703") :
        print "Expected first AMR"
        return -22
    reply = connection.network.receive()
    if reply == None :
        print "no response received to conflict frame"
        return -21
    if not reply.startswith(":X17") :
        print "Expected first CID"
        return -22
    if int(reply[7:10],16) == 0 :
        print "received alias == 0"
        return -24
    if int(reply[7:10],16) == dest :
        print "received alias == previous alias"
        return -25
    dest = int(reply[7:10],16)
    # pull & drop rest of sequence
    reply = connection.network.receive()  # CID 2
    reply = connection.network.receive()  # CID 3
    reply = connection.network.receive()  # CID 4
    time.sleep(0.65)
    reply = connection.network.receive()  # RID
    reply = connection.network.receive()  # AMD
    reply = connection.network.receive()  # VerifiedNID

    return dest
    
def test(dest, connection, identifynode, n, verbose) :
    if identifynode :
        import getUnderTestAlias
        dest, otherNodeId = getUnderTestAlias.get(0x123, None, verbose)

    if n == 0 :
        while dest >= 0 : 
            dest = once(dest, connection, identifynode, verbose)
    else :
        for i in range(n) :
            dest = once(dest, connection, identifynode, verbose)
            if dest < 0 : return -dest
    
    return 0

if __name__ == '__main__':
    main()
